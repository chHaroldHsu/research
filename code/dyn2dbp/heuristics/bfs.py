"""BFS — Best-Fit Shelf, the height-tight cousin of FFS.

Among all shelves that fit, pick the one whose **leftover height**
``shelf.height - item.h`` is smallest. The intent is to keep tall items
out of short shelves and squeeze short items into the tightest available
shelf — the height-axis analogue of classical Best-Fit bin packing.

Expected failure flavour (variant E hypothesis):
    BFS minimises per-item height waste but pays for it with shelf
    fragmentation along the height axis: many shelves end up "perfectly
    full" in height but with x-cursor gaps that no further item can
    reach (cursor monotone). Compared to FFS, BFS should look "tighter
    vertically, splotchier horizontally".

Tie-breaks:
    Ties on leftover height are broken by creation order — older shelf
    wins. Deterministic and matches FFS in the degenerate "all shelves
    same height" case.
"""
from __future__ import annotations

from typing import Optional

from ..core.bin import BinState
from ..core.item import Item, Position
from .shelf import ShelfStrategyBase


class BFS(ShelfStrategyBase):
    """Best-Fit Shelf — among fitting shelves, pick the smallest leftover height."""

    name = "BFS"

    def find_position(self, bin_state: BinState, item: Item) -> Optional[Position]:
        best_shelf = None
        best_leftover = None
        for shelf in self.shelves:
            if not self._fits_in_shelf(shelf, item, bin_state.W):
                continue
            leftover = shelf.height - item.h
            if best_leftover is None or leftover < best_leftover:
                best_shelf = shelf
                best_leftover = leftover
        if best_shelf is not None:
            return self._place_in_shelf(best_shelf, item)
        return self._try_open_new_shelf(bin_state, item)
