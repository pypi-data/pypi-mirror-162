"""Classes for accessing data from the LVM lvs command"""
import json
import shlex
from dataclasses import dataclass
from typing import Dict, List, Optional

from .subproc import check_output


@dataclass
class LVSEntry:
    """Dataclass for an entry in the output of `lvs`

    Attributes
    ----------
    lv
        Name of the LV
    vg
        Name of the VG
    lv_attr
        Attributes of the LV. See `man lvs`.
    lv_size
        Size of the LV in <lv_sizeunit>bytes
    lv_sizeunit
        Unit for lv_size, e.g. b, k, m, g, etc.
    pool_lv
        Name of the pool LV of which this LV is a member, if any
    origin
        For snapshots and thins, the origin device of this LV.
    data_percent
        For snapshot, cache and thin pools and volumes, the percentage full if LV is active.
    metadata_percent
        For cache and thin pools, the percentage of metadata full if LV is active.
    """

    lv: str
    vg: str
    attr: str
    size: int
    sizeunit: str
    pool_lv: str
    origin: str
    data_percent: Optional[float]
    metadata_percent: Optional[float]

    @classmethod
    def from_lvdict(cls, lvdict: Dict[str, str]):
        """Create an LVData instance from a dict of parsed JSON data from lvs"""
        return cls(
            lv=lvdict["lv_name"],
            vg=lvdict["vg_name"],
            attr=lvdict["lv_attr"],
            size=int(lvdict["lv_size"][:-1]),
            sizeunit=lvdict["lv_size"][-1],
            pool_lv=lvdict["pool_lv"],
            origin=lvdict["origin"],
            data_percent=float(lvdict["data_percent"]) if lvdict["data_percent"] else None,
            metadata_percent=float(lvdict["metadata_percent"]) if lvdict["metadata_percent"] else None,
        )

    def is_thin(self) -> bool:
        return self.attr[0] == "V"

    def is_snapshot_of(self, volume_name: str) -> bool:
        return self.origin == volume_name


class LVS:
    """Auto-updating wrapper for a list of lvs entries"""

    _table: List[LVSEntry]

    def __init__(self):
        self.update()

    @property
    def table(self):
        self.update()
        return self._table

    def update(self):
        lvs_json = check_output(shlex.split("/sbin/lvs --reportformat json --units b"), log=False)
        lvs_dict = json.loads(lvs_json)
        self._table = [LVSEntry.from_lvdict(lv_dict) for lv_dict in lvs_dict["report"][0]["lv"]]

    def find(self, vg: str, lv: str) -> Optional[LVSEntry]:
        """Find a logical volume in the lvs data from vg name and lv name"""
        return next((entry for entry in self.table if entry.vg == vg and entry.lv == lv), None)
