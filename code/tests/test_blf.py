"""BLF behavior: returns the lexicographically smallest (y, x) fit, or None.

These tests pin down the exact placement decisions BLF should make on tiny
hand-checkable cases. They also act as a *spec* — if a future refactor
changes BLF's scan order (e.g., to left-bottom-fill), these tests force the
change to be deliberate, not accidental.
"""
from dyn2dbp.core.bin import BinState
from dyn2dbp.core.item import Item, Position
from dyn2dbp.heuristics.blf import BLF


def test_blf_returns_origin_for_empty_bin():
    bs = BinState(W=10, H=10)
    item = Item(id=1, w=3, h=3, t_arrive=0, t_depart=10)
    assert BLF().find_position(bs, item) == Position(0, 0)


def test_blf_returns_none_when_no_fit():
    bs = BinState(W=5, H=5)
    bs.place(Item(id=1, w=5, h=5, t_arrive=0, t_depart=10), Position(0, 0))
    incoming = Item(id=2, w=1, h=1, t_arrive=0, t_depart=10)
    assert BLF().find_position(bs, incoming) is None


def test_blf_returns_none_when_item_too_large():
    bs = BinState(W=5, H=5)
    too_big = Item(id=1, w=6, h=2, t_arrive=0, t_depart=10)
    assert BLF().find_position(bs, too_big) is None


def test_blf_picks_left_corner_after_partial_fill():
    """3×3 at origin → next 2×2 should land at (3,0): bottom row, just right of the block."""
    bs = BinState(W=10, H=10)
    bs.place(Item(id=1, w=3, h=3, t_arrive=0, t_depart=10), Position(0, 0))
    pos = BLF().find_position(bs, Item(id=2, w=2, h=2, t_arrive=0, t_depart=10))
    assert pos == Position(3, 0)


def test_blf_bottom_first_not_left_first():
    """A 4×1 strip across the bottom forces the next 4×1 to land at (0,1), not (4,0).

    This pins the y-outer / x-inner scan order: if someone flips the loop,
    BLF becomes Left-Bottom-Fill and this test fails.
    """
    bs = BinState(W=4, H=10)
    bs.place(Item(id=1, w=4, h=1, t_arrive=0, t_depart=10), Position(0, 0))
    pos = BLF().find_position(bs, Item(id=2, w=4, h=1, t_arrive=0, t_depart=10))
    assert pos == Position(0, 1)
