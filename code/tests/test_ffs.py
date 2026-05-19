"""FFS spec: scan shelves in creation order, first fit wins.

The defining test is "shelf 0 has room → use it, even after shelf 1 is
open" — that's what makes FFS different from NFS. The fallback test pins
what happens when the oldest shelf is full but a later one still fits.
"""
from dyn2dbp.core.bin import BinState
from dyn2dbp.core.item import Item, Position
from dyn2dbp.heuristics.ffs import FFS


def test_ffs_first_item_opens_shelf_at_origin():
    bs = BinState(W=10, H=10)
    pos = FFS().find_position(bs, Item(id=1, w=3, h=4, t_arrive=0, t_depart=10))
    assert pos == Position(0, 0)


def test_ffs_prefers_older_shelf_when_both_fit():
    """After opening shelf 1 with a taller item, a short item that could
    live in either shelf 0 or shelf 1 must go to shelf 0 (creation order)."""
    bs = BinState(W=10, H=10)
    ffs = FFS()
    a = Item(id=1, w=3, h=2, t_arrive=0, t_depart=10)  # opens shelf 0 (h=2)
    bs.place(a, ffs.find_position(bs, a))
    b = Item(id=2, w=3, h=3, t_arrive=1, t_depart=10)  # opens shelf 1 (h=3)
    bs.place(b, ffs.find_position(bs, b))
    pos = ffs.find_position(bs, Item(id=3, w=2, h=2, t_arrive=2, t_depart=10))
    assert pos == Position(3, 0)


def test_ffs_falls_back_when_oldest_shelf_too_short():
    """A 3-tall item can't go in shelf 0 (height 2); FFS must scan to shelf 1."""
    bs = BinState(W=10, H=10)
    ffs = FFS()
    a = Item(id=1, w=3, h=2, t_arrive=0, t_depart=10)  # shelf 0, h=2
    bs.place(a, ffs.find_position(bs, a))
    b = Item(id=2, w=3, h=4, t_arrive=1, t_depart=10)  # shelf 1, h=4
    bs.place(b, ffs.find_position(bs, b))
    pos = ffs.find_position(bs, Item(id=3, w=2, h=3, t_arrive=2, t_depart=10))
    assert pos == Position(3, 2)  # shelf 1, after item 2


def test_ffs_falls_back_when_oldest_shelf_too_narrow():
    """Shelf 0's cursor is at the right edge; new item must skip to shelf 1."""
    bs = BinState(W=5, H=10)
    ffs = FFS()
    a = Item(id=1, w=5, h=2, t_arrive=0, t_depart=10)  # shelf 0 cursor → 5
    bs.place(a, ffs.find_position(bs, a))
    b = Item(id=2, w=3, h=3, t_arrive=1, t_depart=10)  # opens shelf 1
    bs.place(b, ffs.find_position(bs, b))
    pos = ffs.find_position(bs, Item(id=3, w=2, h=2, t_arrive=2, t_depart=10))
    assert pos == Position(3, 2)  # shelf 1, since shelf 0 has no horizontal room


def test_ffs_opens_new_shelf_when_no_existing_fits():
    bs = BinState(W=10, H=10)
    ffs = FFS()
    a = Item(id=1, w=10, h=2, t_arrive=0, t_depart=10)  # fully fills shelf 0
    bs.place(a, ffs.find_position(bs, a))
    pos = ffs.find_position(bs, Item(id=2, w=3, h=3, t_arrive=1, t_depart=10))
    assert pos == Position(0, 2)


def test_ffs_returns_none_when_nothing_fits_and_no_room_above():
    bs = BinState(W=10, H=2)
    ffs = FFS()
    a = Item(id=1, w=10, h=2, t_arrive=0, t_depart=10)
    bs.place(a, ffs.find_position(bs, a))
    pos = ffs.find_position(bs, Item(id=2, w=1, h=1, t_arrive=1, t_depart=10))
    assert pos is None
