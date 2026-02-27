import os
import sys
import threading
from typing import Dict, List, Optional

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from ERROR.error import NotEnoughSpaceError, ProductNotExistError
from main import main as MainWCS

VALID_ALGORITHM_MODES = ("FF", "AO", "RL", "LA", "RA")


class WarehouseRuntime:
    def __init__(self, container_name: str = "default", algorithm_mode: str = "FF"):
        self._lock = threading.RLock()
        self._container_name = container_name
        self._algorithm_mode = self._normalize_mode(algorithm_mode)
        self._wcs = self._build_wcs()

    def _normalize_mode(self, mode: str) -> str:
        normalized = (mode or "FF").upper()
        if normalized not in VALID_ALGORITHM_MODES:
            raise ValueError(
                "Invalid algorithm mode. Use one of: {0}".format(
                    ", ".join(VALID_ALGORITHM_MODES)
                )
            )
        return normalized

    def _build_wcs(self):
        wcs = MainWCS(op_mode="n")
        wcs.default_setting(container_name=self._container_name)
        wcs.mode = self._algorithm_mode
        return wcs

    def _inventory_area(self):
        return self._wcs.WH_dict[self._wcs.WH_name].Zone_dict[self._wcs.Zone_name].Area_dict[
            self._wcs.Area_name
        ]

    def _inventory_counts(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        area = self._inventory_area()
        for lot in area.inventory.keys():
            product_name = self._wcs.product_I_dict.get(lot, {}).get("product_name", "unknown")
            counts[product_name] = counts.get(product_name, 0) + 1
        return dict(sorted(counts.items()))

    def _summary_unlocked(self) -> Dict[str, object]:
        area = self._inventory_area()
        total_inventory = len(area.inventory)
        capacity = area.INVENTORY_CRITICAL_LIMIT
        return {
            "warehouse": self._wcs.WH_name,
            "zone": self._wcs.Zone_name,
            "area": self._wcs.Area_name,
            "algorithm_mode": self._algorithm_mode,
            "container_name": self._container_name,
            "total_inventory": total_inventory,
            "capacity_limit": capacity,
            "available_capacity": max(capacity - total_inventory, 0),
            "product_counts": self._inventory_counts(),
        }

    def health(self) -> Dict[str, object]:
        with self._lock:
            summary = self._summary_unlocked()
            summary["status"] = "ok"
            summary["sim_skip"] = bool(getattr(self._wcs, "sim_skip", False))
            return summary

    def summary(self) -> Dict[str, object]:
        with self._lock:
            return self._summary_unlocked()

    def reset(self, container_name: Optional[str] = None) -> Dict[str, object]:
        with self._lock:
            if container_name:
                self._container_name = container_name
            self._wcs.reset(container_name=self._container_name)
            self._wcs.mode = self._algorithm_mode
            return self._summary_unlocked()

    def set_algorithm_mode(self, mode: str) -> Dict[str, object]:
        with self._lock:
            self._algorithm_mode = self._normalize_mode(mode)
            self._wcs.mode = self._algorithm_mode
            return self._summary_unlocked()

    def list_product_templates(self) -> List[str]:
        with self._lock:
            return sorted(self._wcs.product_templet_dict.keys())

    def list_inventory(
        self, product_name: Optional[str] = None, limit: int = 100
    ) -> Dict[str, object]:
        with self._lock:
            if limit < 1:
                raise ValueError("limit must be >= 1")
            safe_limit = min(limit, 1000)
            area = self._inventory_area()
            lots = list(area.inventory.keys())

            if product_name:
                if product_name not in self._wcs.product_templet_dict:
                    raise ValueError("Unknown product_name: {0}".format(product_name))
                lots = [
                    lot
                    for lot in lots
                    if self._wcs.product_I_dict.get(lot, {}).get("product_name") == product_name
                ]

            lots = sorted(lots)
            shown_lots = lots[:safe_limit]
            return {
                "requested_product": product_name,
                "total_matches": len(lots),
                "returned_count": len(shown_lots),
                "lots": shown_lots,
                "product_counts": self._inventory_counts(),
            }

    def inbound(self, product_name: str = "default", quantity: int = 1) -> Dict[str, object]:
        with self._lock:
            if quantity < 1:
                raise ValueError("quantity must be >= 1")
            if product_name not in self._wcs.product_templet_dict:
                raise ValueError("Unknown product_name: {0}".format(product_name))

            moved_xy = 0.0
            moved_z = 0.0
            lots = []
            processed = 0

            for _ in range(quantity):
                try:
                    moved_distance, lot = self._wcs.Inbound(
                        product_name=product_name, testing_mode=True
                    )
                except NotEnoughSpaceError:
                    break

                moved_xy += float(moved_distance[0])
                moved_z += float(moved_distance[1])
                lots.append(lot)
                processed += 1

            return {
                "ok": processed == quantity,
                "requested_quantity": quantity,
                "processed_quantity": processed,
                "stopped_reason": None if processed == quantity else "not_enough_space",
                "product_name": product_name,
                "lots": lots,
                "moved_distance": [moved_xy, moved_z],
                "summary": self._summary_unlocked(),
            }

    def outbound(
        self,
        quantity: int = 1,
        product_name: Optional[str] = None,
        lot: Optional[str] = None,
    ) -> Dict[str, object]:
        with self._lock:
            if quantity < 1:
                raise ValueError("quantity must be >= 1")
            if lot and quantity != 1:
                raise ValueError("quantity must be 1 when lot is specified")
            if product_name and product_name not in self._wcs.product_templet_dict:
                raise ValueError("Unknown product_name: {0}".format(product_name))

            moved_xy = 0.0
            moved_z = 0.0
            lots = []
            processed = 0
            stop_reason = None

            for index in range(quantity):
                lot_arg = lot if index == 0 else None
                try:
                    moved_distance, lot_id = self._wcs.Outbound(
                        lot=lot_arg, product_name=product_name, testing_mode=True
                    )
                except ProductNotExistError:
                    stop_reason = "product_not_found"
                    break

                moved_xy += float(moved_distance[0])
                moved_z += float(moved_distance[1])
                lots.append(lot_id)
                processed += 1

            return {
                "ok": processed == quantity,
                "requested_quantity": quantity,
                "processed_quantity": processed,
                "stopped_reason": stop_reason,
                "product_name": product_name,
                "requested_lot": lot,
                "lots": lots,
                "moved_distance": [moved_xy, moved_z],
                "summary": self._summary_unlocked(),
            }
