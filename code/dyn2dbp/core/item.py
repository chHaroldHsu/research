"""Item and Position — the two atomic value objects for the whole simulation.

Both are frozen dataclasses so they can be hashed and used as dict keys, and
so a stray mutation can't silently break the bin's accounting (a class of bug
that bit early dynamic-BP papers).
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    """Lower-left corner of a placed item, in bin coordinates.

    Convention throughout the codebase: origin at bottom-left, x grows right,
    y grows up. This matches matplotlib's default and the Hopper-Turton paper,
    so visualisations stay legible without flipping axes.
    """
    x: int
    y: int


@dataclass(frozen=True)
class Item:
    """A rectangular item with a lifetime [t_arrive, t_depart).

    The lifetime is what makes the problem *dynamic*: in static / online 2D BP
    items never leave, so all the failure modes we're hunting (Inland Island,
    Boundary Lockout, ...) are by definition impossible to observe there.

    Attributes
    ----------
    id : int
        Strictly positive. 0 is reserved by BinState for empty cells.
    w, h : int
        Width (x extent) and height (y extent), in grid cells.
    t_arrive : int
        Tick at which the item asks to be placed. Discrete time.
    t_depart : int
        Tick at which the item leaves. Exclusive — the item still occupies
        the bin during tick t_depart-1 and is removed before tick t_depart's
        arrivals fire. The Simulator's tie-break rule depends on this.
    """
    id: int
    w: int
    h: int
    t_arrive: int
    t_depart: int

    @property
    def area(self) -> int:
        return self.w * self.h

    @property
    def lifetime(self) -> int:
        return self.t_depart - self.t_arrive
