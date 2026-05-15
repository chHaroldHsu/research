"""BinState — the 2D grid that placements happen on.

Design choice: a dense numpy int32 array. Alternatives we deliberately rejected:

  * Empty Rectangle List (ERL): faster placement queries but ~10x more code
    to maintain invariants. Not worth it at 50×50.
  * Skyline / Z-layout: only natural for a subset of heuristics (NFDH/FFDH),
    forces every other strategy to translate back and forth.

The grid stores item ids directly (0 = empty), which means removal is a single
slice assignment and snapshots are a single ``copy()``. Both operations need
to be cheap because the Simulator captures a snapshot per event.
"""
from __future__ import annotations

from typing import Dict, Tuple

import numpy as np

from .item import Item, Position


# Cell value reserved for "empty". Item ids must be strictly positive so that
# np.count_nonzero / boolean masks work without ambiguity.
EMPTY: int = 0


class BinState:
    """Mutable 2D grid bin with item bookkeeping.

    Two parallel data structures, kept in sync by ``place`` / ``remove``:

    1. ``grid``: an H×W int32 array — fast pixel-level queries and snapshots.
    2. ``placed``: id → (Item, Position) — fast removal & enumeration.

    Anything outside these two methods is read-only; if you mutate ``grid``
    directly you'll desync the bookkeeping. Tests in ``test_bin.py`` exist
    specifically to catch that class of regression.
    """

    def __init__(self, W: int, H: int) -> None:
        if W <= 0 or H <= 0:
            raise ValueError(f"Bin dimensions must be positive (got W={W}, H={H})")
        self.W = W
        self.H = H
        # grid[y, x]: row-major, y outer. We index spatially as [y, x] because
        # that's what matplotlib's imshow expects, so debug prints line up
        # visually with rendered snapshots.
        self.grid: np.ndarray = np.zeros((H, W), dtype=np.int32)
        self.placed: Dict[int, Tuple[Item, Position]] = {}

    # ---- queries ---------------------------------------------------------

    def can_place(self, item: Item, pos: Position) -> bool:
        """Return True iff ``item`` fits at ``pos`` without overlap or OOB."""
        x, y = pos.x, pos.y
        if x < 0 or y < 0:
            return False
        if x + item.w > self.W or y + item.h > self.H:
            return False
        region = self.grid[y : y + item.h, x : x + item.w]
        return bool(np.all(region == EMPTY))

    def occupancy(self) -> float:
        """Fraction of cells occupied right now.

        This is the instantaneous PE (Packing Efficiency 裝填效率) proxy.
        Reported per snapshot so the time-series can be aggregated later.
        """
        return float(np.count_nonzero(self.grid)) / (self.W * self.H)

    def snapshot(self) -> np.ndarray:
        """Return a defensive copy of the grid for archival."""
        return self.grid.copy()

    # ---- mutations -------------------------------------------------------

    def place(self, item: Item, pos: Position) -> None:
        """Commit a placement. Raises if infeasible — never silently fails.

        The "never silently fail" rule matters because the Simulator relies
        on exception → discard semantics. A wrong-position bug that quietly
        clobbered an existing item would corrupt the entire run.
        """
        if item.id == EMPTY:
            raise ValueError(f"Item id {EMPTY} is reserved for empty cells")
        if item.id in self.placed:
            raise ValueError(f"Item {item.id} already placed")
        if not self.can_place(item, pos):
            raise ValueError(f"Cannot place item {item.id} ({item.w}x{item.h}) at {pos}")
        x, y = pos.x, pos.y
        self.grid[y : y + item.h, x : x + item.w] = item.id
        self.placed[item.id] = (item, pos)

    def remove(self, item_id: int) -> None:
        """Remove a previously placed item. Raises KeyError if unknown."""
        item, pos = self.placed.pop(item_id)
        x, y = pos.x, pos.y
        self.grid[y : y + item.h, x : x + item.w] = EMPTY
