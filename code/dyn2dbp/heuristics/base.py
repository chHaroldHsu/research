"""PlacementStrategy — abstract base for every heuristic in the H × W scan.

The interface is intentionally minimal: a strategy takes a bin and an item,
and returns where to put it (or None). It owns no state across calls. That
constraint is what lets week 3's factorial sweep swap strategies trivially
without touching the simulator or the workload generator.

If a future strategy needs state across calls (e.g., Shelf-based that
remembers shelf y-coordinates), it should keep that state on ``self`` and
reset it at construction time — never carry implicit state through the bin.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from ..core.bin import BinState
from ..core.item import Item, Position


class PlacementStrategy(ABC):
    """Stateless (or self-contained) placement decision rule."""

    #: Human-readable identifier used in logs / plots / experiment tables.
    name: str = "abstract"

    @abstractmethod
    def find_position(self, bin_state: BinState, item: Item) -> Optional[Position]:
        """Return a feasible position for ``item``, or None.

        Must not mutate ``bin_state``. Read-only contract — the Simulator
        commits the actual placement after seeing the returned Position.
        """
        raise NotImplementedError
