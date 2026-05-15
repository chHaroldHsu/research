"""BinState invariants: place / remove must round-trip, queries must respect bounds.

These tests are intentionally tight on the *accounting* layer because every
heuristic and every metric reads from BinState. A regression here cascades
silently into bad mode classifications four weeks downstream.
"""
import numpy as np
import pytest

from dyn2dbp.core.bin import EMPTY, BinState
from dyn2dbp.core.item import Item, Position


def test_empty_bin_zero_occupancy():
    bs = BinState(W=10, H=10)
    assert bs.occupancy() == 0.0
    assert np.all(bs.grid == EMPTY)
    assert bs.placed == {}


def test_place_and_remove_round_trip():
    """Bin grid + bookkeeping must be byte-identical after place→remove."""
    bs = BinState(W=10, H=10)
    item = Item(id=1, w=3, h=4, t_arrive=0, t_depart=10)
    before = bs.grid.copy()
    bs.place(item, Position(2, 1))
    assert bs.occupancy() == pytest.approx(12 / 100)
    bs.remove(item.id)
    assert np.array_equal(bs.grid, before)
    assert bs.placed == {}


def test_cannot_place_overlapping():
    bs = BinState(W=10, H=10)
    a = Item(id=1, w=5, h=5, t_arrive=0, t_depart=10)
    b = Item(id=2, w=3, h=3, t_arrive=0, t_depart=10)
    bs.place(a, Position(0, 0))
    assert not bs.can_place(b, Position(2, 2))
    with pytest.raises(ValueError):
        bs.place(b, Position(2, 2))


def test_cannot_place_out_of_bounds():
    bs = BinState(W=10, H=10)
    item = Item(id=1, w=3, h=3, t_arrive=0, t_depart=10)
    assert not bs.can_place(item, Position(8, 8))  # x extent overflows
    assert not bs.can_place(item, Position(0, 8))  # y extent overflows
    assert not bs.can_place(item, Position(-1, 0))


def test_place_at_boundary_is_allowed():
    """A 3×3 item should fit exactly into a 3×3 bin starting at (0,0)."""
    bs = BinState(W=3, H=3)
    item = Item(id=1, w=3, h=3, t_arrive=0, t_depart=10)
    assert bs.can_place(item, Position(0, 0))
    bs.place(item, Position(0, 0))
    assert bs.occupancy() == 1.0


def test_double_place_same_item_raises():
    bs = BinState(W=10, H=10)
    item = Item(id=1, w=2, h=2, t_arrive=0, t_depart=10)
    bs.place(item, Position(0, 0))
    with pytest.raises(ValueError):
        bs.place(item, Position(5, 5))


def test_remove_unknown_raises():
    bs = BinState(W=10, H=10)
    with pytest.raises(KeyError):
        bs.remove(999)


def test_reserved_id_zero_rejected():
    bs = BinState(W=10, H=10)
    bad = Item(id=0, w=2, h=2, t_arrive=0, t_depart=10)
    with pytest.raises(ValueError):
        bs.place(bad, Position(0, 0))


def test_invalid_bin_dims_raise():
    with pytest.raises(ValueError):
        BinState(W=0, H=10)
    with pytest.raises(ValueError):
        BinState(W=10, H=-1)
