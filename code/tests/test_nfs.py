"""NFS spec: only the most-recently opened shelf is a candidate.

Hand-checkable cases pin the textbook semantics. The cursor-monotonicity
test (departures don't reclaim x-cursor) guards the "ghost cell" failure
mode we want to observe — if a future refactor turns NFS into a compacting
variant, that test fails first.
"""
from dyn2dbp.core.bin import BinState
from dyn2dbp.core.item import Item, Position
from dyn2dbp.heuristics.nfs import NFS


def test_nfs_first_item_opens_shelf_at_origin():
    bs = BinState(W=10, H=10)
    pos = NFS().find_position(bs, Item(id=1, w=3, h=4, t_arrive=0, t_depart=10))
    assert pos == Position(0, 0)


def test_nfs_second_item_advances_cursor_in_same_shelf():
    bs = BinState(W=10, H=10)
    nfs = NFS()
    a = Item(id=1, w=3, h=4, t_arrive=0, t_depart=10)
    nfs.find_position(bs, a)
    bs.place(a, Position(0, 0))
    pos = nfs.find_position(bs, Item(id=2, w=2, h=2, t_arrive=1, t_depart=10))
    assert pos == Position(3, 0)


def test_nfs_taller_item_opens_new_shelf_above():
    """Shelf 0 height is locked at 2 by the opener; a 3-tall item must open shelf 1."""
    bs = BinState(W=10, H=10)
    nfs = NFS()
    a = Item(id=1, w=3, h=2, t_arrive=0, t_depart=10)
    nfs.find_position(bs, a)
    bs.place(a, Position(0, 0))
    pos = nfs.find_position(bs, Item(id=2, w=3, h=3, t_arrive=1, t_depart=10))
    assert pos == Position(0, 2)


def test_nfs_ignores_older_shelf_even_when_it_has_room():
    """After opening shelf 1, NFS never looks back at shelf 0."""
    bs = BinState(W=10, H=10)
    nfs = NFS()
    a = Item(id=1, w=3, h=2, t_arrive=0, t_depart=10)  # opens shelf 0
    bs.place(a, nfs.find_position(bs, a))
    b = Item(id=2, w=3, h=3, t_arrive=1, t_depart=10)  # opens shelf 1
    bs.place(b, nfs.find_position(bs, b))
    # A 2-wide 2-tall item could fit shelf 0 at (3,0) but NFS must put it in shelf 1.
    pos = nfs.find_position(bs, Item(id=3, w=2, h=2, t_arrive=2, t_depart=10))
    assert pos == Position(3, 2)


def test_nfs_returns_none_when_new_shelf_overflows_top():
    """Shelf 0 fills the bin both horizontally and vertically; no room for a new shelf."""
    bs = BinState(W=10, H=5)
    nfs = NFS()
    a = Item(id=1, w=10, h=5, t_arrive=0, t_depart=10)  # fills shelf 0 entirely
    bs.place(a, nfs.find_position(bs, a))
    pos = nfs.find_position(bs, Item(id=2, w=3, h=1, t_arrive=1, t_depart=10))
    assert pos is None


def test_nfs_returns_none_when_item_wider_than_bin():
    bs = BinState(W=5, H=10)
    pos = NFS().find_position(bs, Item(id=1, w=6, h=2, t_arrive=0, t_depart=10))
    assert pos is None


def test_nfs_cursor_does_not_retreat_on_departure():
    """Ghost-cell invariant: when item 1 leaves, its cells are empty in the
    grid but NFS's shelf 0 cursor stays put. The next arrival lands beside
    the ghost, not on top of it."""
    bs = BinState(W=10, H=10)
    nfs = NFS()
    a = Item(id=1, w=3, h=2, t_arrive=0, t_depart=5)
    bs.place(a, nfs.find_position(bs, a))
    b = Item(id=2, w=2, h=2, t_arrive=1, t_depart=10)
    bs.place(b, nfs.find_position(bs, b))
    bs.remove(1)  # item 1 leaves; cells (0..3, 0..2) now empty
    pos = nfs.find_position(bs, Item(id=3, w=2, h=2, t_arrive=6, t_depart=10))
    assert pos == Position(5, 0)  # cursor was at 5 (3 + 2), not reclaimed to 0
