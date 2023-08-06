"""Command line interface and data structure"""
import logging
import textwrap
from argparse import ArgumentParser, RawTextHelpFormatter
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from .autosnap import run_cmd
from .exit import errexit
from .logger import set_daemon_formatter, set_loglevel
from .version import __version__

logger = logging.getLogger(__name__)


@dataclass
class CLIArgs:
    command: str
    vol_id: Union[str, int]
    snap_set_id: Optional[int]
    autoclean: bool
    config_path: Path
    log_level: int
    daemon: bool

    @property
    def parser(self):
        parser = ArgumentParser(
            description="Automated thin volume snapshot management",
            formatter_class=lambda prog: RawTextHelpFormatter(prog, width=80),
        )
        parser.add_argument(
            "command",
            help=textwrap.dedent(
                """\
                Command to execute. Valid commands:
                mount    - Mount snapshots
                umount   - Unmount snapshots
                snap     - Make a new snapshot
                clean    - Cleanup outdated snapshots
                autosnap - Create snapshots per the configured snap set and
                           clean up outdated ones.
                check    - Check that the data usage of the pool for each specified volume
                           has not exceeded its configured warning percent.
                list     - List all snapshots
                remove   - Remove all snapshots in set (run umount first)
                genconf  - Print an example configuration file to stdout.
                """
            ),
        )
        parser.add_argument(
            "--autoclean",
            action="store_true",
            help="If command is autosnap, run clean after creating the new\nsnapshots.",
        )
        parser.add_argument(
            "--config",
            default="/etc/ltautosnap.conf",
            help="Alternate configuration file. Default is /etc/ltautosnap.conf.",
        )
        parser.add_argument("-v", dest="verbosity", action="count", default=0)
        parser.add_argument(
            "-d", "--daemon", action="store_true", help="Make logging appropriate for file output."
        )
        parser.add_argument("-V", "--version", action="version", version=__version__)
        parser.add_argument(
            "volume", help='Number of the volume, or "all" for all volumes', default="", nargs="?"
        )
        parser.add_argument(
            "snap_set",
            nargs="?",
            type=int,
            default=None,
            help=textwrap.dedent(
                """\
                Number of the snaphot-set.
                Optional for all commands except snap, autosnap, and clean."""
            ),
        )
        return parser

    def __init__(self):
        args = self.parser.parse_args()
        command: str = args.command
        volume: str = args.volume
        if command not in (
            "mount",
            "umount",
            "snap",
            "clean",
            "autosnap",
            "check",
            "list",
            "remove",
            "genconf",
        ):
            errexit("Invalid command")
        if command not in ["genconf"] and args.volume != "all" and not args.volume.isdecimal():
            errexit("Volume must be 'all' or a volume number.")
        self.command = command
        self.vol_id = int(volume) if volume.isdecimal() else volume
        self.snap_set_id = args.snap_set
        self.autoclean = args.autoclean
        self.config_path = Path(args.config)
        log_levels = {
            0: logging.WARNING,
            1: logging.INFO,
            2: logging.DEBUG,
        }
        self.log_level = log_levels.get(args.verbosity, logging.DEBUG)
        self.daemon = args.daemon


def cli():
    try:
        args = CLIArgs()
        set_loglevel(args.log_level)
        if args.daemon:
            set_daemon_formatter()
        run_cmd(args)
    except Exception as ex:
        errexit("Exception", 255, ex)
