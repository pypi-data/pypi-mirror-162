"""Main application. See run_cmd() for main entry point"""

import logging
import os
import re
import shlex
import time
from configparser import ConfigParser
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Dict, List, NamedTuple, Optional, Tuple, Union

from .config import SnapSet, Volume
from .errors import AutosnapConfigError, AutosnapError
from .exit import errexit
from .lvs import LVS
from .mounts import Mounts
from .subproc import check_call

if TYPE_CHECKING:
    from .cli import CLIArgs


# Globals
logger = logging.getLogger(__name__)
lvs: LVS
mounts: Mounts


def check_root():
    if os.geteuid() != 0:
        errexit("This command requires root privileges.", 126)


def run_cmd(args: "CLIArgs"):
    if args.command == "genconf":
        # genconf doesn't need any of the setup
        genconf()
        exit(0)
    check_root()
    global lvs
    global mounts
    lvs = LVS()
    mounts = Mounts()
    manager = SnapMgr(args.config_path)

    # Get volumes to process
    volumes = manager.get_volumes(args.vol_id)
    if not volumes:
        raise AutosnapError(f"Specifed volume vol{args.vol_id} is not in {args.config_path}")

    # Get snapsets to process
    snapset_keys = manager.get_snapset_keys(args.snap_set_id)
    if not snapset_keys:
        raise AutosnapError(f"Specifed snap set set{args.snap_set_id} is not in {args.config_path}")

    # Run command
    # All commands have anywhere from one to three args
    # volume: Volume, snap_set_id: int, autoclean: bool, automount: bool
    CliCmd = Callable[..., Optional[str]]
    CliCmdSignature = Tuple[CliCmd, int]  # with nargs
    cli_cmds: Dict[str, CliCmdSignature] = {
        "mount": (mount_snapset, 2),
        "umount": (umount_snapset, 2),
        "snap": (create_snap, 2),
        "clean": (manager.clean, 2),
        "list": (list_snapshots, 2),
        "remove": (remove_snapset, 2),
        "autosnap": (manager.autosnap, 4),
        "check": (check_space, 1),
    }

    if args.command in cli_cmds:
        for vol in volumes:
            cmd, nargs = cli_cmds[args.command]
            if nargs > 1:
                for snap_set_id in snapset_keys:
                    cmd_args = (vol, snap_set_id, args.autoclean, vol.snap_mount_point != "NOMOUNT")
                    cmd(*cmd_args[:nargs])
            else:
                cmd(vol)
    else:
        assert False  # arg parsing should prevent reaching here


def mkdir(path: Path, *args, **kwargs):
    """Wrapper for Path.mkdir to just print what happens if dry_run is True"""
    path.mkdir(*args, **kwargs)


def rmdir(path: Path):
    """Wrapper for Path.rmdir to just print what happens if dry_run is True"""
    path.rmdir()


def utcnow():
    # mockable function for testing
    return datetime.now().astimezone(timezone.utc)


def get_snapshot_names(vol: Volume, snap_set_i: int) -> List[str]:
    """Get a list of all snapshot names for a given snap set"""
    snap_prefix = f"{vol.lv}-set{snap_set_i:02d}"
    return [lvdata.lv for lvdata in lvs.table if lvdata.vg == vol.vg and snap_prefix in lvdata.lv]


class SnapshotDt(NamedTuple):
    """Meaning of tuples output by get_snapshot_dts"""

    name: str
    dt: datetime


def get_snapshot_dts(vol: Volume, snap_set_i: int) -> List[SnapshotDt]:
    """Get the timestamps of all snapshots in a snap set that end with any timestamp"""
    snap_names = get_snapshot_names(vol, snap_set_i)
    # Need this generator so we can filter out snaps without a datetime in the following comprehension
    snap_dt_gen = (get_dt_from_snapname(snap_name) for snap_name in snap_names)
    return sorted(
        (
            SnapshotDt(snap_name, snap_dt)
            for snap_name, snap_dt in zip(snap_names, snap_dt_gen)
            if snap_dt is not None
        ),
        key=lambda tpl: tpl[1],
    )


def get_dt_from_snapname(snap_name: str) -> Optional[datetime]:
    """Get the datetime from the end of a snapshot name is possible. Otherwise return None."""
    try:
        return datetime.strptime("-".join(snap_name.split("-")[-2:]), "%Y.%m.%d-%H.%M.%S").replace(
            tzinfo=timezone.utc
        )
    except ValueError:
        # no datestr at the end of snap_name
        return None


def create_snap(vol: Volume, snap_set_i: int) -> str:
    """Create a snapshot for a volume and snap set"""
    time.sleep(1)  # Ensure unique snap timestamps
    snap_date = utcnow()
    snap_datestr = f"{snap_date:%Y.%m.%d-%H.%M.%S}"
    snap_name = f"{vol.lv}-set{snap_set_i:02d}-{snap_datestr}"
    logger.info("Creating snaphot %s from %s/%s", snap_name, vol.vg, vol.lv)
    create_cmd = f"/sbin/lvcreate -s -n {snap_name} {vol.dev_path}"
    check_call(shlex.split(create_cmd))
    return snap_name


def mount_snap(vol: Volume, snap_name: str):
    # Put together a target path for mounting the snapshot
    logger.info("Mounting snap %s/%s", vol.vg, snap_name)
    # Ensure mounting is allowed
    if vol.snap_mount_point == "NOMOUNT":
        raise AutosnapError(f"{vol.vg}/{vol.lv} is configured with NOMOUNT. Will not mount {snap_name}.")
    # Get name for mount
    snap_datestr = "-".join(snap_name.split("-")[-2:])
    snap_mountname = f"@GMT-{snap_datestr}"
    # Ensure mounting the snapshot is possible
    if vol.snap_mount_point:
        snap_mountparent = vol.snap_mount_point
    else:
        vol_mount = mounts.find_by_dev(vol.dev_path)
        if not vol_mount:
            raise AutosnapError(f"{vol.dev_path} must be mounted to mount snapshots in it.")
        snap_mountparent = vol_mount.target
    if not snap_mountparent.is_dir():
        raise AutosnapError(f"Snaps parent mount path {snap_mountparent} is not a directory")
    lvs_lv = lvs.find(vol.vg, snap_name)
    if not lvs_lv:
        raise AutosnapError(f"{vol.vg}/{snap_name} does not appear in lvs and cannot be mounted.")
    if lvs_lv.origin != vol.lv:
        raise AutosnapError(f"{vol.vg}/{snap_name} is not a snapshot of {vol.vg}/{vol.lv}")

    snap_mount_target = snap_mountparent / snap_mountname
    # Check for mount target conflicts
    if snap_mount_target.is_dir():
        # If so, is something already mounted there?
        exg_mount = mounts.find_by_path(snap_mount_target)
        if exg_mount:
            if Path(exg_mount.device).resolve() != Path(f"/dev/{vol.vg}/{snap_name}").resolve():
                # If it's not this snapshot, then we have a problem.
                raise AutosnapError(
                    f"Cannot mount snap {snap_name} to {snap_mount_target}. {exg_mount.device} is already"
                    " mounted there."
                )
            logger.info("%s is already mounted at %s.", snap_name, exg_mount.device)
            return
    elif snap_mount_target.exists():
        raise AutosnapError(
            f"Cannot mount {snap_name} because {snap_mount_target} exists and is not a dir (very weird)"
        )
    mkdir(snap_mount_target)
    # Ensure the snap is activated, then mount it
    activate_cmd = f"/sbin/lvchange -ay -K {vol.vg}/{snap_name}"
    check_call(shlex.split(activate_cmd))
    mount_opts = ",".join(["ro", vol.snap_mount_options])
    mount_cmd = f"/bin/mount -o {mount_opts} /dev/{vol.vg}/{snap_name} {snap_mount_target}"
    check_call(shlex.split(mount_cmd))


def check_snapshot(vol: Volume, snap_name: str):
    """Ensure that an lv is a snapshot of a volume"""
    snap_lvs_entry = lvs.find(vol.vg, snap_name)
    if not snap_lvs_entry:
        raise AutosnapError(f"{vol.vg}/{snap_name} is not in lvs")
    return snap_lvs_entry.is_snapshot_of(vol.lv)


def umount_snap(vol: Volume, snap_name: str):
    # sourcery skip: use-named-expression
    """Unmount a snapshot, optionally keeping the directory"""
    if not check_snapshot(vol, snap_name):
        raise AutosnapError(f"{snap_name} is not a snapshot of {vol.vg}/{vol.lv}")
    snap_dev = Path(f"/dev/{vol.vg}/{snap_name}")
    mount = mounts.find_by_dev(snap_dev)
    if mount:
        logger.info("Unmounting %s from %s", mount.device, mount.target)
        umount_cmd = f"/bin/umount -f -l {mount.device}"
        check_call(shlex.split(umount_cmd))
        rmdir(mount.target)
    deactivate_cmd = f"/sbin/lvchange -an {snap_dev}"
    check_call(shlex.split(deactivate_cmd))


def remove_snap(vol: Volume, snap_name: str):
    """Remove a snapshot"""
    if not check_snapshot(vol, snap_name):
        raise AutosnapError(f"{snap_name} is not a snapshot of {vol.vg}/{vol.lv}")
    snap_dev = Path(f"/dev/{vol.vg}/{snap_name}")
    if mounts.find_by_dev(snap_dev):
        raise AutosnapError("Snap must be unmounted before it is removed.")
    logger.info("Removing snapshot %s/%s", vol.vg, snap_name)
    lvremove_cmd = f"/sbin/lvremove -y {vol.vg}/{snap_name}"
    check_call(shlex.split(lvremove_cmd))


def mount_snapset(vol: Volume, snap_set_i: int):
    for snap_name in get_snapshot_names(vol, snap_set_i):
        mount_snap(vol, snap_name)


def umount_snapset(vol: Volume, snap_set_i: int):
    for snap_name in get_snapshot_names(vol, snap_set_i):
        umount_snap(vol, snap_name)


def remove_snapset(vol: Volume, snap_set_i: int):
    for snap_name in get_snapshot_names(vol, snap_set_i):
        remove_snap(vol, snap_name)


def list_snapshots(vol: Volume, snap_set_i: int):
    print(f"Snapshots and mountpoints for volume {vol.vg}/{vol.lv}, snap set {snap_set_i}:")
    # get the snap names and their mount targets
    snapnames = get_snapshot_names(vol, snap_set_i)
    snap_mounts = [mounts.find_by_dev(Path(f"/dev/{vol.vg}/{name}")) for name in snapnames]
    snap_mount_targets = [mount.target if mount else "--not mounted--" for mount in snap_mounts]
    # Determine max snapname len to create a format string for printing
    max_snapname_len = max((len(name) for name in snapnames)) if snapnames else 0
    fmtstr = f"{{name:{max_snapname_len}s}}  {{target}}"
    for name, target in zip(snapnames, snap_mount_targets):
        print(fmtstr.format(name=name, target=target))
    print("--------")


def check_space(vol: Volume):
    logger.info("Checking space in %s/%s's pool...", vol.vg, vol.lv)
    if not vol.warning_pct:
        raise AutosnapConfigError(f"Volume {vol.vg}/{vol.lv} is not configured with a warning percent value")
    lvs_entry = lvs.find(vol.vg, vol.lv)
    if lvs_entry:
        pool_entry = lvs.find(vol.vg, lvs_entry.pool_lv)
        if pool_entry:
            logger.info("Used space in %s/%s's pool: %g", vol.vg, vol.lv, pool_entry.data_percent)
            if pool_entry.data_percent and pool_entry.data_percent > vol.warning_pct:
                logger.warning(
                    "Data usage of pool %s/%s has reached over %g percent",
                    vol.vg,
                    lvs_entry.pool_lv,
                    vol.warning_pct,
                )


def fstrim(vol: Volume):
    logger.info("Trimming %s/%s", vol.vg, vol.lv)
    vol_mount = mounts.find_by_dev(Path(f"/dev/{vol.vg}/{vol.lv}"))
    if not vol_mount:
        raise AutosnapError("Cannot trim non-mounted volume.")
    fstrim_cmd = f"/sbin/fstrim {vol_mount.target}"
    check_call(shlex.split(fstrim_cmd))


def genconf():
    example_conf = Path(__file__).parent / "ltautosnap.conf"
    print(example_conf.read_text())


class SnapMgr:
    """Class for creating and managing scheduled snapshots"""

    def __init__(self, conf_path: Path = Path("/etc/ltautosnap.conf")):
        """Parse and validate the configuration for Autosnap

        Parameters
        ----------
        conf_path
            Path to the configuration file, by default Path("/etc/ltautosnap.conf")
        """
        self.volumes: Dict[int, Volume] = {}
        self.snap_sets: Dict[int, SnapSet] = {}
        self.parse_and_validate_config(conf_path)

    def get_volumes(self, vol_id: Union[int, str]) -> List[Volume]:
        """Helper to get all volumes if vol_id is "all" or just one if a valid index, or empty list"""
        if vol_id == "all":
            return list(self.volumes.values())
        elif vol_id in self.volumes:
            assert isinstance(vol_id, int)
            return [self.volumes[vol_id]]
        else:
            return []

    def get_snapset_keys(self, snap_set_id: Optional[int]):
        """Helper to get all snap set keys if snap_set_id is None or just one if a valid key, or empty list"""
        if snap_set_id is None:
            return list(self.snap_sets.keys())
        elif snap_set_id in self.snap_sets:
            return [snap_set_id]
        else:
            return []

    def parse_and_validate_config(self, conf_path: Path):
        """Parse the config file"""
        if not conf_path.is_file():
            raise FileNotFoundError(f"Configuration file {conf_path} does not exist.")
        self.volumes = {}
        self.snap_sets = {}
        config = ConfigParser()
        config.read(conf_path)
        for section in config.sections():
            if re.match(r"vol\d+", section):
                self.volumes[int(section[3:])] = Volume.from_parser_section(config[section])
            if re.match(r"set\d+", section):
                self.snap_sets[int(section[3:])] = SnapSet.from_parser_section(config[section])
        self.validate_config()

    def validate_config(self):
        """Check the config for any problems. Must have mounts and lvs populated before running."""
        if not self.volumes:
            raise AutosnapConfigError("No volumes are specified in config.")
        if not self.snap_sets:
            raise AutosnapConfigError("No snap sets are specified in config")
        for vol_i, vol in self.volumes.items():
            if not vol.dev_path.is_block_device():
                raise AutosnapConfigError(f"vol{vol_i}: {vol.dev_path} is not a block device")
            if not vol.is_thin(lvs):
                raise AutosnapError("autosnap.py only works with thin volumes.")
            for set_i in vol.snap_sets:
                if set_i not in self.snap_sets:
                    raise AutosnapConfigError(f"Volume vol{vol_i} includes undefined snap set set{set_i}.")

    def autosnap(self, vol: Volume, snap_set_i: int, autoclean=False, automount=True):
        # sourcery skip: use-named-expression
        """Determine if a snapshot needs to be made for the selected volume and snap set and if so, make it."""
        logger.info("Running autosnap for volume %s/%s, set %d", vol.vg, vol.lv, snap_set_i)
        snap_dts = get_snapshot_dts(vol, snap_set_i)
        if snap_dts:
            nearest_snap_dt = snap_dts[-1]
            td_since_last_snap = utcnow() - nearest_snap_dt.dt
            if td_since_last_snap < self.snap_sets[snap_set_i].period_td:
                return
        snap_name = create_snap(vol, snap_set_i)
        if automount:
            mount_snap(vol, snap_name)
        if autoclean:
            self.clean(vol, snap_set_i)

    def clean(self, vol: Volume, snap_set_i: int):
        logger.info("Running clean for volume %s/%s, set %d", vol.vg, vol.lv, snap_set_i)
        # Get the list of snap dts for this volume and snap set.
        # Since they come ordered, we can use them to find the n newest snapshots.
        snap_dts = get_snapshot_dts(vol, snap_set_i)
        if len(snap_dts) > self.snap_sets[snap_set_i].count:
            n_to_remove = len(snap_dts) - self.snap_sets[snap_set_i].count
            snaps_to_remove = snap_dts[:n_to_remove]
            for snap_name, _ in snaps_to_remove:
                umount_snap(vol, snap_name)
                remove_snap(vol, snap_name)
        fstrim(vol)
