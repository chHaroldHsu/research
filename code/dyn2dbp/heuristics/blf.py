"""BLF — Bottom-Left-Fill, the textbook 2D packing baseline.

Why BLF is the natural first heuristic for variant E:

  * It's the Hopper-Turton (1999) benchmark default — all comparable papers
    report against it, so we inherit a calibration anchor for free.
  * Its failure pattern under departures is the most intuitive: items pile
    at the bottom-left, so when a long-lived bottom-left item leaves it
    creates an empty pocket surrounded by later arrivals. That's the
    candidate "Inland Island" mode we expect to validate first.

This implementation is brute force: scan every (x, y) bottom-up / left-right
and return the first fit. O(W·H · w·h) per call. For 50×50 bins with ≤ a
few hundred items it runs in single-digit milliseconds — fine for Special
Topic. If/when it becomes the bottleneck (large bins, long workloads), the
upgrade path is a skyline/staircase data structure.
"""
from __future__ import annotations

from typing import Optional

from ..core.bin import BinState
from ..core.item import Item, Position
from .base import PlacementStrategy


class BLF(PlacementStrategy):
    """Lexicographically smallest feasible (y, x) — y outer (bottom first)."""

    name = "BLF"

    def find_position(self, bin_state: BinState, item: Item) -> Optional[Position]:
        # y outer makes this "bottom-fill"; x inner makes it "left-fill".
        # The order matters — swapping them gives Left-Bottom-Fill, which
        # produces meaningfully different empty-pocket shapes.
        for y in range(bin_state.H - item.h + 1):
            for x in range(bin_state.W - item.w + 1):
                pos = Position(x, y)
                if bin_state.can_place(item, pos):
                    return pos
        return None
