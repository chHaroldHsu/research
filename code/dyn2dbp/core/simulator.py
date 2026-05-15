"""Event-driven simulator for dynamic 2D BP.

Discrete-event simulation (DES 離散事件模擬): a priority queue of arrival /
departure events processed in time order. The simulator owns no policy — it
just executes whatever the PlacementStrategy decides and records the result.

Tie-break rule at equal timestamps: DEPARTURE before ARRIVAL.
This means an item leaving at t=5 frees its cells *before* a new item arriving
at t=5 tries to place. Without this rule, a perfectly-timed swap would
spuriously fail (the new item would see the old footprint as occupied).

Snapshot policy: store the bin grid after every successful event. At 50×50
this is 2500 int32 = 10KB per snapshot — cheap. Skipping snapshots on
failed arrivals (the bin didn't change) cuts the volume substantially.
"""
from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Tuple

import numpy as np

from ..heuristics.base import PlacementStrategy
from .bin import BinState
from .item import Item, Position


# Event type tags. Strings (not ints) so log dumps are readable without a
# legend. Cost is negligible vs. the placement scan.
ARRIVAL = "arrival"
DEPARTURE = "departure"


@dataclass
class EventLog:
    """One row per event the simulator handled.

    A "failed arrival" still produces a row (success=False, position=None)
    so downstream metrics can count discards without reconstructing them.
    """
    t: int
    event_type: str
    item_id: int
    success: bool
    position: Optional[Position] = None
    occupancy_after: float = 0.0


@dataclass
class SimResult:
    """Everything a single simulation run produces."""
    events: List[EventLog] = field(default_factory=list)
    snapshots: List[Tuple[int, np.ndarray]] = field(default_factory=list)
    discarded_count: int = 0
    final_occupancy: float = 0.0


class Simulator:
    """Plug-and-play simulator: ``Simulator(bin, strategy).run(items)``.

    Both ``bin_state`` and ``strategy`` are injected so a week-3 factorial
    sweep can hold the workload fixed and reset just the bin and strategy
    between cells of the H × W grid.
    """

    def __init__(self, bin_state: BinState, strategy: PlacementStrategy) -> None:
        self.bin_state = bin_state
        self.strategy = strategy

    def run(self, items: Iterable[Item]) -> SimResult:
        # Build the priority queue. Each entry is a 5-tuple sorted by:
        #   (1) time — events fire in chronological order
        #   (2) priority — 0=DEPARTURE before 1=ARRIVAL at the same tick
        #   (3) item id — deterministic order for reproducibility when two
        #       arrivals or two departures share a timestamp
        #   (4) event type tag — never tie-breaks because (2) already does
        #   (5) the Item itself — only payload, never compared (heapq won't
        #       compare it because (3) breaks ties first)
        queue: list = []
        for item in items:
            heapq.heappush(queue, (item.t_arrive, 1, item.id, ARRIVAL, item))
            heapq.heappush(queue, (item.t_depart, 0, item.id, DEPARTURE, item))

        result = SimResult()
        placed_ids: set[int] = set()

        while queue:
            t, _prio, _iid, event_type, item = heapq.heappop(queue)

            if event_type == ARRIVAL:
                pos = self.strategy.find_position(self.bin_state, item)
                if pos is None:
                    result.discarded_count += 1
                    result.events.append(EventLog(
                        t=t, event_type=ARRIVAL, item_id=item.id, success=False,
                    ))
                else:
                    self.bin_state.place(item, pos)
                    placed_ids.add(item.id)
                    result.events.append(EventLog(
                        t=t, event_type=ARRIVAL, item_id=item.id, success=True,
                        position=pos, occupancy_after=self.bin_state.occupancy(),
                    ))
                    result.snapshots.append((t, self.bin_state.snapshot()))

            else:  # DEPARTURE
                # An item that failed to place was never added to placed_ids,
                # so its departure is a no-op (and shouldn't appear in the log
                # — otherwise PE traces look misleading).
                if item.id in placed_ids:
                    self.bin_state.remove(item.id)
                    placed_ids.remove(item.id)
                    result.events.append(EventLog(
                        t=t, event_type=DEPARTURE, item_id=item.id, success=True,
                        occupancy_after=self.bin_state.occupancy(),
                    ))
                    result.snapshots.append((t, self.bin_state.snapshot()))

        result.final_occupancy = self.bin_state.occupancy()
        return result
