"""Simulator integration tests: arrivals + departures + tie-break order.

The single most important behavior to guard: at the same timestamp,
DEPARTURE fires before ARRIVAL. Without this rule, the "swap at t=N"
pattern (one item leaves, another arrives, same tick) spuriously fails.
"""
from dyn2dbp.core.bin import BinState
from dyn2dbp.core.item import Item
from dyn2dbp.core.simulator import ARRIVAL, DEPARTURE, Simulator
from dyn2dbp.heuristics.blf import BLF


def test_simulator_single_item():
    bs = BinState(W=10, H=10)
    sim = Simulator(bs, BLF())
    items = [Item(id=1, w=3, h=3, t_arrive=0, t_depart=5)]
    result = sim.run(items)
    assert result.discarded_count == 0
    assert result.final_occupancy == 0.0  # placed then departed
    arrivals = [e for e in result.events if e.event_type == ARRIVAL]
    departures = [e for e in result.events if e.event_type == DEPARTURE]
    assert len(arrivals) == 1 and arrivals[0].success
    assert len(departures) == 1 and departures[0].success


def test_simulator_discards_when_full():
    """Bin fills exactly; next arrival must be discarded, not crash."""
    bs = BinState(W=4, H=4)
    sim = Simulator(bs, BLF())
    items = [
        Item(id=1, w=4, h=4, t_arrive=0, t_depart=100),
        Item(id=2, w=1, h=1, t_arrive=1, t_depart=10),
    ]
    result = sim.run(items)
    assert result.discarded_count == 1
    # The discarded item must have an explicit failed-arrival row.
    failed = [e for e in result.events if not e.success]
    assert len(failed) == 1
    assert failed[0].item_id == 2


def test_departure_before_arrival_at_same_tick():
    """At t=5, item #1's departure must clear the bin BEFORE item #2 arrives.

    Item #1 fills the bin (4×4 of 4×4). Item #2 also 4×4, arrival at t=5,
    same tick as #1's departure. If departure fires first, #2 places. If
    the order is wrong, #2 is discarded.
    """
    bs = BinState(W=4, H=4)
    sim = Simulator(bs, BLF())
    items = [
        Item(id=1, w=4, h=4, t_arrive=0, t_depart=5),
        Item(id=2, w=4, h=4, t_arrive=5, t_depart=10),
    ]
    result = sim.run(items)
    assert result.discarded_count == 0
    assert result.final_occupancy == 0.0


def test_snapshots_captured_on_every_successful_event():
    """One snapshot per successful arrival + one per successful departure."""
    bs = BinState(W=10, H=10)
    sim = Simulator(bs, BLF())
    items = [
        Item(id=1, w=3, h=3, t_arrive=0, t_depart=5),
        Item(id=2, w=2, h=2, t_arrive=1, t_depart=8),
    ]
    result = sim.run(items)
    # 2 successful arrivals + 2 successful departures = 4 snapshots
    assert len(result.snapshots) == 4
