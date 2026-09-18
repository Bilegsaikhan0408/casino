# Cassino

The Hungarian two-player version of Cassino, with a 52-card French deck, in the
browser: you against the computer.

## Play

```sh
uv run python -m casino
```

This starts the table at <http://127.0.0.1:8000/> and opens it in your browser.
Add `--port 8080` to use another port, or `--no-browser` to not open a tab.

Click one or more cards in your hand, then the table cards they take (a matching
card, or cards that add up to it), and press **Take**. A hand card alone is
**Place**d on the table. Ace is 1, King is 13.

## Tests

```sh
uv run pytest
```

Without `uv`: `python -m pip install pytest`, then `python -m pytest`. The game itself needs only Python 3.11+.

## Layout

- `casino/rules.py`: the rules (`value`, `Move`, `new_deal`, `legal_moves`, `play`, `deal_over`, `score`)
- `casino/ai.py`: the computer player (greedy, sees only its own hand and the table)
- `casino/game.py`, `casino/__main__.py`: one game in memory and a small HTTP server
- `casino/static/index.html`: the table
