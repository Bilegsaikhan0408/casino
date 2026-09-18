"""One game against the computer: keeps the state and a log, and builds what the browser may see."""
from __future__ import annotations

import random

from . import ai
from .rules import DECK, Move, State, deal_over, legal_moves, new_deal, play, points

HUMAN, COMPUTER = 0, 1


class Game:
    def __init__(self, rng: random.Random | None = None):
        self.rng = rng or random.Random()
        self.state: State
        self.log: list = []
        self.start()

    def start(self) -> None:
        deck = list(DECK)
        self.rng.shuffle(deck)
        self.state = new_deal(deck, first=self.rng.choice((HUMAN, COMPUTER)))
        self.log = [{"text": "New deal. " + (
            "You lead." if self.state.player == HUMAN else "The computer leads.")}]
        self._computer_moves()

    def move(self, hand, table) -> None:
        if self.state.player != HUMAN or deal_over(self.state):
            raise ValueError("it is not your turn")
        self._apply(Move(frozenset(hand), frozenset(table)))
        self._computer_moves()

    def _apply(self, move: Move) -> None:
        before = self.state
        who = before.player
        after = play(before, move)
        name = "You" if who == HUMAN else "The computer"
        played = " + ".join(sorted(move.hand))
        if move.table:
            text = f"{name} played {played} and took {' '.join(sorted(move.table))}."
        else:
            text = f"{name} placed {played}."
        entry = {"who": "you" if who == HUMAN else "computer", "text": text,
                 "hand": sorted(move.hand), "table": sorted(move.table)}
        if after.sweeps[who] > before.sweeps[who]:
            entry["text"] += " Sweep!"
            entry["sweep"] = True
        self.log.append(entry)
        if len(after.talon) < len(before.talon):
            self.log.append({"text": "New round: three cards each."})
        if deal_over(after):
            leftover = set(before.table) - set(move.table)
            if leftover or not move.table:
                taker = "You" if after.last == HUMAN else "The computer"
                self.log.append({"text": f"{taker} took the cards left on the table."})
        self.state = after

    def _computer_moves(self) -> None:
        while not deal_over(self.state) and self.state.player == COMPUTER:
            self._apply(ai.choose(self.state, self.rng))

    def view(self) -> dict:
        s = self.state
        over = deal_over(s)
        view = {
            "hand": list(s.hands[HUMAN]),
            "opponent_cards": len(s.hands[COMPUTER]),
            "table": list(s.table),
            "talon": len(s.talon),
            "you": {"pile": len(s.piles[HUMAN]), "sweeps": s.sweeps[HUMAN]},
            "computer": {"pile": len(s.piles[COMPUTER]), "sweeps": s.sweeps[COMPUTER]},
            "your_turn": s.player == HUMAN and not over,
            "double": s.double and s.player == HUMAN,
            "over": over,
            "log": self.log[-40:],
            "legal": [],
        }
        if view["your_turn"]:
            view["legal"] = [
                {"hand": sorted(m.hand), "table": sorted(m.table)} for m in legal_moves(s)
            ]
        if over:
            you, computer = points(s, HUMAN), points(s, COMPUTER)
            view["result"] = {
                "you": {**you, "pile": len(s.piles[HUMAN]),
                        "spade_cards": sum(c.endswith("S") for c in s.piles[HUMAN])},
                "computer": {**computer, "pile": len(s.piles[COMPUTER]),
                             "spade_cards": sum(c.endswith("S") for c in s.piles[COMPUTER])},
                "winner": ("you" if you["total"] > computer["total"]
                           else "computer" if computer["total"] > you["total"] else "tie"),
            }
        return view
