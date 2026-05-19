"""NFS — Next-Fit Shelf, the online cousin of NFDH.

The decision rule is one line: try the most recently opened shelf; if the
item doesn't fit there, open a new shelf above. Older shelves are never
revisited, even if they still have horizontal room.

Expected failure flavour (variant E hypothesis):
    "Top-Shelf Waste" — each closed shelf locks in whatever empty
    horizontal strip was on it when the next-tall item showed up, plus
    whatever cursor gap the last item left. With departures, the lower
    shelves also accumulate "departed-item ghost" cells the strategy can
    never come back for.
"""
from __future__ import annotations

from typing import Optional

from ..core.bin import BinState
from ..core.item import Item, Position
from .shelf import ShelfStrategyBase


class NFS(ShelfStrategyBase):
    """Next-Fit Shelf — only the most recently opened shelf is a candidate."""

    name = "NFS"

    def find_position(self, bin_state: BinState, item: Item) -> Optional[Position]:
        if self.shelves:
            current = self.shelves[-1]
            if self._fits_in_shelf(current, item, bin_state.W):
                return self._place_in_shelf(current, item)
        return self._try_open_new_shelf(bin_state, item)
