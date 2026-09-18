"""The computer player: a greedy chooser that only looks at its own hand and the table."""
from __future__ import annotations

import random

from .rules import Move, State, legal_moves, value


def card_worth(card: str) -> float:
    worth = 1.0  # every card counts towards the 27
    if card.endswith("S"):
        worth += 0.6
    if card.startswith("A"):
        worth += 1.0
    if card == "10D":
        worth += 2.0
    if card == "2S":
        worth += 1.0
    return worth


def rate(state: State, move: Move) -> float:
    me = state.player
    if move.table:
        gained = sum(card_worth(c) for c in move.hand | move.table)
        left = len(state.table) - len(move.table)
        cards_left = len(state.hands[me]) + len(state.hands[1 - me]) + len(state.talon)
        sweep = 1.5 if left == 0 and cards_left > len(move.hand) else 0.0
        # keep strong hand cards when a weaker move does nearly as well
        return gained + sweep - 0.05 * sum(value(c) for c in move.hand)
    (card,) = move.hand
    # placing: give away as little as possible, and don't feed a sweep
    exposed = card_worth(card)
    table_total = sum(value(c) for c in state.table) + value(card)
    feeds_sweep = 0.5 if len(state.table) <= 1 and table_total <= 13 else 0.0
    return -exposed - feeds_sweep - 0.02 * value(card)


def choose(state: State, rng: random.Random | None = None) -> Move:
    rng = rng or random
    moves = legal_moves(state)
    return max(moves, key=lambda m: rate(state, m) + rng.random() * 0.01)
