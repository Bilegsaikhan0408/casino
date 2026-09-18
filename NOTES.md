# Notes

Built with a coding agent, by prompts only. The tests were not edited.

## Rules the tests left open (the agent's choices)

- Ace is 1. A hand card takes a matching card or table cards that split into groups each adding up to it.
- Playing several hand cards at once (the tests allow it) counts their sum as one value.
- Placing is always legal, even when a capture is possible.
- After a sweep the *opponent* plays twice in a row (only while they still hold cards).
- Clearing the table with the very last card of the deal is not a sweep.
- If nobody has captured at a round change, the next player in turn order leads.

## What playing found

I played a whole deal in the browser (21 moves of mine; the computer won 11 to 7).

1. **Wrong wording after a sweep.** After the *computer* swept, the status said "the sweep gives you a second move too". Asked to say the computer swept and that I play twice. Fixed.
2. **Misleading hints.** With one hand card selected, some table cards got a dashed hint outline that the card cannot take alone. They only worked with a two-card hand play. Asked to hint only moves that use exactly the selected hand cards. Fixed.
3. **Hard to see what the computer did.** Its cards vanish, and the log is the only trace. Asked to outline the computer's moves since my last move in the log. Fixed.

## Still open

- The computer sometimes plays two hand cards at once (it swept with 3♦+K♥ = 16 taking 7♠+9♥). That is legal under the tests, but it looks odd, and it makes the hands uneven for the rest of the round.
- Cards are drawn in CSS, not with the Wikimedia deck.
- The computer is a greedy chooser. It does not count cards or plan.
