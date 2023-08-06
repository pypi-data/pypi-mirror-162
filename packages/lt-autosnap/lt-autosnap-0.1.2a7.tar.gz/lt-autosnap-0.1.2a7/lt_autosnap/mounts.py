"""Classes for accessing data about mounts from /proc/mounts"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Mount:
    """Dataclass for a mounted device as gleaned from /proc/mounts

    Attributes
    ----------
    device
        block device or remote filesystem that is mounted
    target
        Path where `device` is mounted
    fs_type
        Filesystem type of the mounted device
    mount_opts
        Mount options for the filesystem
    dump
        1 if the filesystem is dumped by `dump`, 0 otherwise.
    fsck_pass
        Whether to fsck at boot and if so, priority. 0: skip, 1: top priority, 2: 2nd priority, etc..
    """

    device: str
    target: Path
    fs_type: str
    mount_opts: str
    dump: int
    fsck_pass: int

    @classmethod
    def from_mtab_line(cls, line: str):
        """Create a Mount instance from a line in /etc/mtab or /proc/mounts"""
        fs_spec, fs_file, fs_vfstype, fs_mntops, fs_freq, fs_passno, *_ = line.strip().split(" ")
        return cls(
            device=fs_spec,
            target=Path(fs_file),
            fs_type=fs_vfstype,
            mount_opts=fs_mntops,
            dump=int(fs_freq),
            fsck_pass=int(fs_passno),
        )


class Mounts:
    """Wrapper for an auto-updating list of mountpoints"""

    @property
    def table(self):
        self.update()
        return self._table

    def update(self):
        with open("/proc/mounts") as fmounts:
            mount_list = fmounts.readlines()
        self._table = [Mount.from_mtab_line(line) for line in mount_list]

    def find_by_dev(self, dev_path: Path) -> Optional[Mount]:
        """Find a mount by its device path"""
        dev_path = dev_path.resolve()
        return next((mount for mount in self.table if dev_path == Path(mount.device).resolve()), None)

    def find_by_path(self, mount_path: Path) -> Optional[Mount]:
        """Find a mount in the mounts list from the mount path (target)"""
        mount_path = mount_path.resolve()
        return next((mount for mount in self.table if mount_path == Path(mount.target).resolve()), None)
