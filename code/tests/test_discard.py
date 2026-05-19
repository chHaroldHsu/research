"""Tests for the discard rate metric.

Same strategy as test_pe.py — drive everything through the real Simulator
when possible so we can't drift from EventLog semantics, and hand-roll a
SimResult only when we need exact timings (the windowed-rate test).
"""
import numpy as np
import pytest

from dyn2dbp.core.bin import BinState
from dyn2dbp.core.item import Item, Position
from dyn2dbp.core.simulator import ARRIVAL, DEPARTURE, EventLog, SimResult, Simulator
from dyn2dbp.heuristics.blf import BLF
from dyn2dbp.metrics.discard import discard_series, discard_stats


def test_discard_empty_run():
    """No items → empty cumulative series, zero stats, windowed is None."""
    bs = BinState(W=10, H=10)
    sim = Simulator(bs, BLF())
    result = sim.run([])

    cum, win = discard_series(result, window=5)
    assert cum.t.size == 0
    assert cum.value.size == 0
    assert cum.label == "discard_cumulative"
    assert win is None  # no arrivals → no windowed series even if window requested

    stats = discard_stats(result)
    assert stats.total == 0
    assert stats.rate_overall == 0.0


def test_discard_all_succeed():
    """Every arrival fits → cumulative rate is 0.0 throughout."""
    bs = BinState(W=10, H=10)
    sim = Simulator(bs, BLF())
    items = [Item(id=i, w=1, h=1, t_arrive=i, t_depart=i + 100) for i in range(1, 6)]
    result = sim.run(items)

    cum, _ = discard_series(result)
    assert cum.value.tolist() == [0.0, 0.0, 0.0, 0.0, 0.0]
    stats = discard_stats(result)
    assert stats.total == 0
    assert stats.rate_overall == 0.0


def test_discard_mixed_cumulative():
    """Mixed success/failure run: one big item blocks several small arrivals,
    then departs and one more fits.

    Expected arrivals (in heap time order):
      t=0  id=1 4×4 → success
      t=5  id=2 1×1 → FAIL (bin full)
      t=10 id=3 1×1 → FAIL
      t=15 id=4 1×1 → FAIL
      t=110 id=5 1×1 → success (big item departed at t=100)

    Cumulative rate: [0/1, 1/2, 2/3, 3/4, 3/5] = [0, .5, .667, .75, .6].
    """
    bs = BinState(W=4, H=4)
    sim = Simulator(bs, BLF())
    items = [
        Item(id=1, w=4, h=4, t_arrive=0,   t_depart=100),
        Item(id=2, w=1, h=1, t_arrive=5,   t_depart=20),
        Item(id=3, w=1, h=1, t_arrive=10,  t_depart=21),
        Item(id=4, w=1, h=1, t_arrive=15,  t_depart=22),
        Item(id=5, w=1, h=1, t_arrive=110, t_depart=120),
    ]
    result = sim.run(items)

    cum, _ = discard_series(result)
    np.testing.assert_allclose(cum.value, [0.0, 0.5, 2 / 3, 0.75, 0.6])
    assert cum.t.tolist() == [0, 5, 10, 15, 110]

    stats = discard_stats(result)
    assert stats.total == 3
    np.testing.assert_allclose(stats.rate_overall, 0.6)


def test_discard_ignores_departures():
    """DEPARTURE events must not appear in the denominator.

    Without this guard, items that succeed and then leave would inflate the
    arrival count and depress the rate. Build a hand-rolled SimResult so the
    point is unambiguous: 1 successful arrival + 1 failed arrival + 1
    departure → rate = 1/2, not 1/3.
    """
    result = SimResult(events=[
        EventLog(t=0, event_type=ARRIVAL, item_id=1, success=True,
                 position=Position(0, 0), occupancy_after=1.0),
        EventLog(t=1, event_type=ARRIVAL, item_id=2, success=False),
        EventLog(t=10, event_type=DEPARTURE, item_id=1, success=True,
                 occupancy_after=0.0),
    ])
    stats = discard_stats(result)
    assert stats.total == 1
    assert stats.rate_overall == 0.5


def test_discard_windowed_rolling():
    """Windowed rate must reflect *local* failure clustering, not history.

    Hand-built arrivals at t=0,5,10,20 with outcomes [✓, ✗, ✗, ✓]; window=6.

      t=0  → look back to t=-6: just this arrival, 0 failures → 0.0
      t=5  → look back to t=-1: arrivals at {0,5}, 1 failure → 0.5
      t=10 → look back to t=4: arrivals at {5,10}, 2 failures → 1.0
      t=20 → look back to t=14: just this arrival, 0 failures → 0.0

    Note how the windowed curve hits 1.0 at t=10 (local burst) while the
    cumulative is only 2/3 — exactly the signal we want for catching
    fragmentation buildup.
    """
    result = SimResult(events=[
        EventLog(t=0,  event_type=ARRIVAL, item_id=1, success=True,
                 position=Position(0, 0), occupancy_after=0.1),
        EventLog(t=5,  event_type=ARRIVAL, item_id=2, success=False),
        EventLog(t=10, event_type=ARRIVAL, item_id=3, success=False),
        EventLog(t=20, event_type=ARRIVAL, item_id=4, success=True,
                 position=Position(0, 0), occupancy_after=0.2),
    ])
    cum, win = discard_series(result, window=6)
    np.testing.assert_allclose(cum.value, [0.0, 0.5, 2 / 3, 0.5])
    assert win is not None
    np.testing.assert_allclose(win.value, [0.0, 0.5, 1.0, 0.0])
    assert win.label == "discard_windowed"


def test_discard_windowed_none_when_window_none():
    """``window=None`` → no windowed series; cumulative still produced."""
    result = SimResult(events=[
        EventLog(t=0, event_type=ARRIVAL, item_id=1, success=False),
    ])
    cum, win = discard_series(result, window=None)
    assert win is None
    assert cum.value.tolist() == [1.0]


def test_discard_window_must_be_positive():
    """Zero / negative window is a programming error, not silently ignored."""
    result = SimResult(events=[
        EventLog(t=0, event_type=ARRIVAL, item_id=1, success=False),
    ])
    with pytest.raises(ValueError):
        discard_series(result, window=0)
    with pytest.raises(ValueError):
        discard_series(result, window=-3)
