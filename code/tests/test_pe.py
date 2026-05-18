"""Tests for the PE metric.

Strategy: drive everything through the real Simulator rather than hand-rolling
SimResult fixtures. Two reasons —

1. The Simulator's event ordering / occupancy_after semantics are exactly
   what pe.py consumes; mocking them is how drift between the producer and
   consumer goes undetected.
2. Hand-rolling EventLog rows duplicates Simulator logic in test code, which
   is the worst place to duplicate it.

The exception is the time-weighted mean test, which builds a SimResult by
hand because we need *exact* event timings to check the arithmetic — driving
the Simulator would require constructing items whose lifetimes hit those
ticks, which is more brittle than just synthesising the events.
"""
import numpy as np

from dyn2dbp.core.bin import BinState
from dyn2dbp.core.item import Item, Position
from dyn2dbp.core.simulator import ARRIVAL, DEPARTURE, EventLog, SimResult, Simulator
from dyn2dbp.heuristics.blf import BLF
from dyn2dbp.metrics.pe import pe_series, pe_stats


def test_pe_empty_bin_no_events():
    """No items → empty series, all stats are zero, no division-by-zero."""
    bs = BinState(W=10, H=10)
    sim = Simulator(bs, BLF())
    result = sim.run([])
    series = pe_series(result)
    assert series.t.size == 0
    assert series.value.size == 0
    assert series.label == "pe"

    stats = pe_stats(result)
    assert stats.peak == 0.0
    assert stats.peak_t == 0
    assert stats.mean == 0.0
    assert stats.final == 0.0


def test_pe_full_bin_then_empty():
    """One item exactly fills the bin then leaves.

    Peak PE must equal 1.0 (item area = bin area), peak_t must be the
    arrival tick, final must be 0.0 (item departed).
    """
    bs = BinState(W=4, H=4)
    sim = Simulator(bs, BLF())
    items = [Item(id=1, w=4, h=4, t_arrive=0, t_depart=10)]
    result = sim.run(items)

    stats = pe_stats(result)
    assert stats.peak == 1.0
    assert stats.peak_t == 0
    assert stats.final == 0.0


def test_pe_excludes_failed_arrivals():
    """A failed arrival must not appear as a (t, 0.0) point in the series.

    Without this guard, EventLog's default occupancy_after=0.0 on failed
    rows would plot a spurious dip to zero, ruining the PE trace.
    """
    bs = BinState(W=4, H=4)
    sim = Simulator(bs, BLF())
    items = [
        Item(id=1, w=4, h=4, t_arrive=0, t_depart=100),  # fills bin
        Item(id=2, w=1, h=1, t_arrive=1, t_depart=10),   # must fail
    ]
    result = sim.run(items)
    series = pe_series(result)

    # Three events fire: arrival of #1 (success), arrival of #2 (FAIL),
    # departure of #1 (success). The failed arrival at t=1 must be absent —
    # if it leaked in, we'd see a point at t=1 with value 0.0 (EventLog's
    # default), spuriously dipping the trace.
    assert series.t.tolist() == [0, 100]
    assert series.value.tolist() == [1.0, 0.0]


def test_pe_time_weighted_mean():
    """Mean must integrate a step function, not average samples.

    Hand-built SimResult so the arithmetic is unambiguous. Events at
    t=0, t=1, t=10 with PE 0.5, 1.0, 0.0:

      width[0]=1, width[1]=9. Integral = 0.5·1 + 1.0·9 = 9.5.
      Span = 10. Time-weighted mean = 0.95.

    A naive sample mean would be (0.5 + 1.0 + 0.0)/3 = 0.5 — very different,
    which is the whole point of using time-weighting.
    """
    result = SimResult(events=[
        EventLog(t=0, event_type=ARRIVAL, item_id=1, success=True,
                 position=Position(0, 0), occupancy_after=0.5),
        EventLog(t=1, event_type=ARRIVAL, item_id=2, success=True,
                 position=Position(0, 0), occupancy_after=1.0),
        EventLog(t=10, event_type=DEPARTURE, item_id=1, success=True,
                 occupancy_after=0.0),
    ])
    stats = pe_stats(result)
    assert stats.peak == 1.0
    assert stats.peak_t == 1
    assert stats.final == 0.0
    np.testing.assert_allclose(stats.mean, 0.95)


def test_pe_single_event_mean_collapses_to_value():
    """One event → no interval to integrate; mean == that single value."""
    result = SimResult(events=[
        EventLog(t=5, event_type=ARRIVAL, item_id=1, success=True,
                 position=Position(0, 0), occupancy_after=0.3),
    ])
    stats = pe_stats(result)
    assert stats.peak == 0.3
    assert stats.peak_t == 5
    assert stats.mean == 0.3
    assert stats.final == 0.3
