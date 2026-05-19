"""FFS — First-Fit Shelf, the online cousin of FFDH.

Scan shelves in **creation order** and take the first one that fits;
open a new shelf only if none do. The creation-order bias matters: it
keeps older (lower) shelves preferred, so the bin tends to fill from
the bottom up — but exactly which shelf any given item lands in depends
on what came before it, which in dynamic settings is non-obvious.

Expected failure flavour (variant E hypothesis):
    Lower shelves get filled with mixed-width items, leaving short
    horizontal slivers as the cursors creep right. When a slim item
    arrives, FFS will happily wedge it into the first shelf with room
    even if a later shelf would have wasted less height — i.e., FFS is
    width-greedy at the cost of height utilisation.
"""
from __future__ import annotations

from typing import Optional

from ..core.bin import BinState
from ..core.item import Item, Position
from .shelf import ShelfStrategyBase


class FFS(ShelfStrategyBase):
    """First-Fit Shelf — scan shelves in creation order; first fit wins."""

    name = "FFS"

    def find_position(self, bin_state: BinState, item: Item) -> Optional[Position]:
        for shelf in self.shelves:
            if self._fits_in_shelf(shelf, item, bin_state.W):
                return self._place_in_shelf(shelf, item)
        return self._try_open_new_shelf(bin_state, item)
