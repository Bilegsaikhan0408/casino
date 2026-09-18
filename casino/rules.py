"""Rules of the Hungarian two-player Cassino."""
from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import combinations
from typing import NamedTuple, Optional, Sequence

RANKS = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")
SUITS = "SHDC"
DECK = tuple(rank + suit for suit in SUITS for rank in RANKS)
_VALUES = {rank: n for n, rank in enumerate(RANKS, 1)}


def value(card: str) -> int:
    return _VALUES[card[:-1]]


class Move(NamedTuple):
    hand: frozenset
    table: frozenset


@dataclass(frozen=True)
class State:
    hands: tuple
    table: tuple
    talon: tuple
    piles: tuple
    sweeps: tuple
    player: int
    last: Optional[int] = None  # who captured last
    double: bool = False  # the player to move plays twice in a row (after a sweep)


def new_deal(deck: Sequence[str], first: int = 0) -> State:
    deck = tuple(deck)
    hands = [(), ()]
    hands[first] = deck[0:3]
    hands[1 - first] = deck[3:6]
    return State(
        hands=tuple(hands),
        table=deck[6:10],
        talon=deck[10:],
        piles=((), ()),
        sweeps=(0, 0),
        player=first,
    )


def deal_over(state: State) -> bool:
    return not state.table and not state.talon and not any(state.hands)


def _splits(values: Sequence[int], target: int) -> bool:
    """Can the values be split into groups that each add up to target?"""
    total = sum(values)
    if total % target or max(values) > target:
        return False
    groups = [0] * (total // target)
    values = sorted(values, reverse=True)

    def fill(i: int) -> bool:
        if i == len(values):
            return True
        tried = set()
        for g in range(len(groups)):
            if groups[g] in tried or groups[g] + values[i] > target:
                continue
            tried.add(groups[g])
            groups[g] += values[i]
            done = fill(i + 1)
            groups[g] -= values[i]
            if done:
                return True
        return False

    return fill(0)


def legal_moves(state: State) -> list:
    if deal_over(state):
        return []
    hand = state.hands[state.player]
    moves = [Move(frozenset({card}), frozenset()) for card in hand]
    for size in range(1, len(hand) + 1):
        for played in combinations(hand, size):
            target = sum(value(c) for c in played)
            for count in range(1, len(state.table) + 1):
                for taken in combinations(state.table, count):
                    if _splits([value(c) for c in taken], target):
                        moves.append(Move(frozenset(played), frozenset(taken)))
    return moves


def play(state: State, move: Move) -> State:
    move = Move(frozenset(move.hand), frozenset(move.table))
    if move not in legal_moves(state):
        raise ValueError(f"illegal move: {sorted(move.hand)} / {sorted(move.table)}")

    me, other = state.player, 1 - state.player
    hands = list(state.hands)
    hands[me] = tuple(c for c in hands[me] if c not in move.hand)
    piles = list(state.piles)
    sweeps = list(state.sweeps)
    last = state.last

    if move.table:
        table = tuple(c for c in state.table if c not in move.table)
        taken = tuple(c for c in state.table if c in move.table)
        piles[me] = piles[me] + taken + tuple(c for c in state.hands[me] if c in move.hand)
        last = me
    else:
        table = state.table + tuple(move.hand)

    finished = not any(hands) and not state.talon
    swept = bool(move.table) and not table and not finished
    if swept:
        sweeps[me] += 1

    talon = state.talon
    double = False
    if state.double and hands[me]:
        nxt = me  # second half of the double move
    elif hands[other]:
        nxt, double = other, swept
    elif hands[me]:
        nxt = me
    else:
        # the round is over
        if talon:
            nxt = last if last is not None else other
            mine, theirs = talon[0:3], talon[3:6]
            hands[nxt], hands[1 - nxt] = mine, theirs
            talon = talon[6:]
        else:
            # the deal is over: the table goes to the last capturer
            winner = last if last is not None else me
            piles[winner] = piles[winner] + table
            table = ()
            nxt = other

    return replace(
        state,
        hands=tuple(hands),
        table=table,
        talon=talon,
        piles=tuple(piles),
        sweeps=tuple(sweeps),
        player=nxt,
        last=last,
        double=double,
    )


def points(state: State, player: int) -> dict:
    """The points of one player, itemised."""
    pile = state.piles[player]
    spades = sum(c.endswith("S") for c in pile)
    items = {
        "cards": 3 if len(pile) >= 27 else 0,
        "spades": 2 if spades >= 7 else 0,
        "aces": sum(c.startswith("A") for c in pile),
        "ten_of_diamonds": 2 if "10D" in pile else 0,
        "two_of_spades": 1 if "2S" in pile else 0,
        "sweeps": state.sweeps[player],
    }
    items["total"] = sum(items.values())
    return items


def score(state: State) -> tuple:
    return (points(state, 0)["total"], points(state, 1)["total"])
