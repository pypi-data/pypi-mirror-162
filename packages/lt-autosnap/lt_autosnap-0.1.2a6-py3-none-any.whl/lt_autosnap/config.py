"""Configuration file parser and data structures"""
import shlex
from configparser import SectionProxy
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, List, Optional, Union

from .errors import AutosnapConfigError, AutosnapError
from .lvs import LVS
from .subproc import check_output

if TYPE_CHECKING:
    # Don't require typing_extensions for runtime
    from typing_extensions import Literal

    NOMOUNT_S = Literal["NOMOUNT"]
else:
    NOMOUNT_S = str


@dataclass
class Volume:
    """Dataclass for volume entries in ltautosnap.conf

    Attributes
    ----------
    vg
        Volume group name
    lv
        Logical volume name
    snap_mount_options
        Options to provide after `mount -o` when mounting snapshots of the volume. Typically nouuid for XFS
        snapshots
    snap_sets
        List of integer keys to snap sets defined in ltautosnap.conf
    snap_mount_point
        Optional path under which the snapshots of this volume should be mounted. If missing or empty, the
        mount point of this volume is used.
    warning_pct
        Optional. When running check command emit a warning if the pool is this full or more. If not
        provided, the check command will error.

    """

    vg: str
    lv: str
    snap_mount_options: str = ""
    snap_sets: List[int] = field(default_factory=list)
    snap_mount_point: Union[Path, None, NOMOUNT_S] = None
    warning_pct: Optional[float] = None

    @classmethod
    def from_parser_section(cls, section: SectionProxy):
        """Create a Volume instance from a ConfigParser section from a parsed autosnap.py"""
        vg, lv = section["lv"].split("/")
        if not section["snap_sets"]:
            raise AutosnapConfigError("A volume must have snap sets to be in the config.")
        snap_mount_point = section.get("snap_mount_point") or None  # None if empty string
        if snap_mount_point is not None:
            snap_mount_point = "NOMOUNT" if snap_mount_point.upper() == "NOMOUNT" else Path(snap_mount_point)
        if "warning_pct" in section:
            warning_pct = float(section["warning_pct"])
            if warning_pct > 100:
                raise AutosnapConfigError("warning_pct cannot be greater than 100.0")
        else:
            warning_pct = None
        return cls(
            vg=vg,
            lv=lv,
            snap_mount_options=section["snap_mount_options"],
            snap_sets=[int(i) for i in section["snap_sets"].split(",")],
            snap_mount_point=snap_mount_point,
            warning_pct=warning_pct,
        )

    @property
    def dev_path(self) -> Path:
        """Mountable device path to the volume"""
        return Path(f"/dev/{self.vg}/{self.lv}")

    def is_thin(self, lvs: LVS) -> bool:
        """Is the volume reported as thin in lvs?"""
        lvs_entry = lvs.find(self.vg, self.lv)
        if lvs_entry:
            return lvs_entry.is_thin()
        raise AutosnapError(f"{self.vg}/{self.lv} not found in lvs")

    def get_snapset_lvs(self, set_i: int) -> List[str]:
        """Get the names of every lv that is a snapshot of this volume"""
        return [
            line.strip()
            for line in check_output(
                shlex.split(
                    f"lvs -o lv_name --noheadings -S 'lv_name =~ ^{self.lv}-set{set_i:02d}.+' {self.vg}"
                )
            )
            .decode("utf-8")
            .splitlines()
        ]


@dataclass
class SnapSet:
    """Dataclass for snap set entries in ltautosnap.conf

    Attributes
    ----------
    unit
        unit for period, e.g. minutes, hours, days, weeks
    period
        How often to create a snapshot in this set
    count
        Maximum number of snapshots to keep in this set
    """

    unit: str
    period: float
    count: int

    _ok_units: ClassVar[List[str]] = ["minutes", "hours", "days", "weeks"]

    @classmethod
    def from_parser_section(cls, section: SectionProxy):
        """Create a SnapSet instance from a ConfigParser section from a parsed autosnap.py"""
        unit = section["unit"].lower()
        if unit not in cls._ok_units:
            # Try adding an s
            unit += "s"
        if unit not in cls._ok_units:
            raise AutosnapConfigError(f"snap set unit must be one of {cls._ok_units}")
        return cls(
            unit=unit,
            period=float(section["period"]),
            count=int(section["count"]),
        )

    @property
    def period_td(self):
        """The period as a timedelta"""
        td_kwargs = {self.unit: self.period}
        return timedelta(**td_kwargs)
