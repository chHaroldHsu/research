"""Shelf base — online (non-DH) shelf-packing heuristics.

Why "online" (no DH = Decreasing Height):
    Textbook NFDH / FFDH require sorting all items by decreasing height
    up front — an offline assumption the dynamic+departure setting can't
    satisfy (we don't see future arrivals). NFS / FFS / BFS are the online
    counterparts: open shelves greedily, decide per-arrival.

Shelf semantics — *textbook pure*, not compacting:
    Each shelf has an x-cursor that **only advances**. When an item inside
    a shelf departs, its cells are freed in the bin grid but the cursor
    does not retreat — so those cells are visible-empty but unreachable
    by the shelf strategy. That "departed-item ghost" pattern is exactly
    one of the candidate failure modes variant E wants to name; a
    compacting variant would erase the very signal we're after.

State lives on the instance:
    PlacementStrategy is meant to be self-contained (see base.py). Shelf
    strategies are the canonical example: the open-shelf list is per-run
    state. Construct a fresh strategy per simulation; don't reuse across
    cells of the H × W sweep.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from ..core.bin import BinState
from ..core.item import Item, Position
from .base import PlacementStrategy


@dataclass
class Shelf:
    """One open horizontal strip.

    ``height`` is locked by the first item placed into the shelf — the
    item that "opened" it. Subsequent items must satisfy ``item.h <= height``,
    otherwise they don't belong here and the strategy must try another
    shelf or open a new one above.
    """
    y_low: int
    height: int
    x_cursor: int


class ShelfStrategyBase(PlacementStrategy):
    """Bookkeeping shared by NFS / FFS / BFS.

    Subclasses override only the shelf-selection rule inside
    ``find_position``; opening a new shelf and advancing the cursor are
    identical across the family.
    """

    def __init__(self) -> None:
        self.shelves: List[Shelf] = []

    # ---- shared helpers --------------------------------------------------

    def _fits_in_shelf(self, shelf: Shelf, item: Item, bin_W: int) -> bool:
        """Item fits horizontally AFTER the cursor AND vertically under the shelf height."""
        return item.w <= bin_W - shelf.x_cursor and item.h <= shelf.height

    def _place_in_shelf(self, shelf: Shelf, item: Item) -> Position:
        """Mutates ``shelf.x_cursor`` — call this only when returning a position."""
        pos = Position(x=shelf.x_cursor, y=shelf.y_low)
        shelf.x_cursor += item.w
        return pos

    def _try_open_new_shelf(
        self, bin_state: BinState, item: Item
    ) -> Optional[Position]:
        """Open a new shelf at the top stack, or None if it wouldn't fit."""
        new_y = sum(s.height for s in self.shelves)
        if new_y + item.h > bin_state.H:
            return None
        if item.w > bin_state.W:
            return None
        shelf = Shelf(y_low=new_y, height=item.h, x_cursor=item.w)
        self.shelves.append(shelf)
        return Position(x=0, y=new_y)
