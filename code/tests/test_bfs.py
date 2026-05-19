"""BFS spec: among shelves that fit, smallest leftover height wins.

The defining test contrasts BFS with FFS: given two open shelves where
both fit the item but one is a tighter height match, BFS picks the tight
one (FFS would pick the older one). Tie-break is creation order.
"""
from dyn2dbp.core.bin import BinState
from dyn2dbp.core.item import Item, Position
from dyn2dbp.heuristics.bfs import BFS


def test_bfs_first_item_opens_shelf_at_origin():
    bs = BinState(W=10, H=10)
    pos = BFS().find_position(bs, Item(id=1, w=3, h=4, t_arrive=0, t_depart=10))
    assert pos == Position(0, 0)


def test_bfs_picks_tightest_leftover_height():
    """Three shelves of heights 5, 3, 4 all with room. A 3-tall item should
    land in the height-3 shelf (zero leftover) — even though it fits in all
    three. FFS would have picked the height-5 shelf (creation order).

    Setup forces each shelf-opener to leave horizontal room (w=15 of W=20),
    while the next opener's w=15 won't fit beside the previous one (only
    5 left), so each new opener creates a new shelf instead of slotting in.
    """
    bs = BinState(W=20, H=15)
    bfs = BFS()
    a = Item(id=1, w=15, h=5, t_arrive=0, t_depart=10)  # shelf 0 (h=5), cursor=15
    bs.place(a, bfs.find_position(bs, a))
    b = Item(id=2, w=15, h=3, t_arrive=1, t_depart=10)  # opens shelf 1 (h=3), cursor=15
    bs.place(b, bfs.find_position(bs, b))
    c = Item(id=3, w=15, h=4, t_arrive=2, t_depart=10)  # opens shelf 2 (h=4), cursor=15
    bs.place(c, bfs.find_position(bs, c))
    # shelves: y=0 h=5 cur=15, y=5 h=3 cur=15, y=8 h=4 cur=15.
    # Item 4 (w=2, h=3) fits all three; leftover heights = 2, 0, 1 → pick shelf 1.
    pos = bfs.find_position(bs, Item(id=4, w=2, h=3, t_arrive=3, t_depart=10))
    assert pos == Position(15, 5)


def test_bfs_breaks_ties_by_creation_order():
    """Two shelves of equal height: older shelf wins."""
    bs = BinState(W=20, H=10)
    bfs = BFS()
    a = Item(id=1, w=3, h=3, t_arrive=0, t_depart=10)  # shelf 0
    bs.place(a, bfs.find_position(bs, a))
    b = Item(id=2, w=3, h=3, t_arrive=1, t_depart=10)  # forced to shelf 0 (older)
    pos = bfs.find_position(bs, b)
    assert pos == Position(3, 0)


def test_bfs_skips_shelves_too_short_for_item():
    """A 4-tall item can't go in a height-3 shelf, even if that's tighter.

    Setup uses wide openers (w=15 of W=20) so the second opener has to
    create its own shelf rather than reusing shelf 0.
    """
    bs = BinState(W=20, H=15)
    bfs = BFS()
    a = Item(id=1, w=15, h=5, t_arrive=0, t_depart=10)  # shelf 0 (h=5), cursor=15
    bs.place(a, bfs.find_position(bs, a))
    b = Item(id=2, w=15, h=3, t_arrive=1, t_depart=10)  # opens shelf 1 (h=3)
    bs.place(b, bfs.find_position(bs, b))
    # 4-tall item: shelf 1 (h=3) too short → must use shelf 0 (h=5).
    pos = bfs.find_position(bs, Item(id=3, w=2, h=4, t_arrive=2, t_depart=10))
    assert pos == Position(15, 0)


def test_bfs_opens_new_shelf_when_no_existing_fits():
    bs = BinState(W=10, H=10)
    bfs = BFS()
    a = Item(id=1, w=10, h=2, t_arrive=0, t_depart=10)  # fills shelf 0 horizontally
    bs.place(a, bfs.find_position(bs, a))
    pos = bfs.find_position(bs, Item(id=2, w=3, h=3, t_arrive=1, t_depart=10))
    assert pos == Position(0, 2)


def test_bfs_returns_none_when_nothing_fits_and_no_room_above():
    bs = BinState(W=10, H=2)
    bfs = BFS()
    a = Item(id=1, w=10, h=2, t_arrive=0, t_depart=10)
    bs.place(a, bfs.find_position(bs, a))
    pos = bfs.find_position(bs, Item(id=2, w=1, h=1, t_arrive=1, t_depart=10))
    assert pos is None
