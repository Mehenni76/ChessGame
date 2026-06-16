# CLAUDE.md

Guidance for working in this repository.

## Project

A simplified, fully local, deterministic **console chess game**. The human
plays White; a minimax + Alpha-Beta AI plays Black. After the board, the
program prints a stronger (deeper) move recommendation for White.

The full functional specification lives in `src/Instruction.md` and is the
source of truth — read it before changing behavior.

## Run / validate

```bash
python3 chess.py            # show board (+ advice), no move played
python3 chess.py e2e4       # play one White move; AI replies as Black
python3 chess.py e7e8q      # promotion (q,r,b,n; defaults to queen)
python3 -m py_compile chess.py board.py rules.py engine.py   # compile check
```

There is no test framework or linter configured; validation is manual via the
commands above. `VERIFICATION.md` records the validation suite and results.

## Architecture

Four cohesive source files; `chess.py` is the **only** script run directly.

- `chess.py` — CLI dispatch (0 or 1 arg), game flow, error output, exits.
- `board.py` — 8×8 board, coordinate conversions, coordinate display, strict
  `game.txt` load/save/validate/delete.
- `rules.py` — strict move parsing, pseudo-legal generation, attack detection,
  legal-move filtering, check/checkmate/stalemate, move application, status.
- `engine.py` — evaluation (material + PST + mobility + center), move ordering,
  `alphabeta`, Black AI (`select_ai_move`, depth 2), White advice
  (`select_advice_move`, depth 3).

## Conventions and invariants (do not break)

- **Board orientation**: row 0 = rank 8, row 7 = rank 1; col 0 = file a,
  col 7 = file h. A move is the 5-tuple `(fr, fc, tr, tc, promo)`.
- **Evaluation sign**: positive favors Black, negative favors White. Black
  maximizes, White minimizes in `alphabeta`.
- **No interactive input** (`input()` is forbidden), **no randomness**, **no
  network**, **no external model**. Everything must stay deterministic.
- **All user-facing text in English.** Errors go to stderr; success keeps
  stderr empty. The board (with coordinates) prints to stdout.
- **Pseudo-legal moves and attacked squares are distinct** — keep
  `square_attacked_by` independent of move generation (pawns attack diagonally
  only).
- **Strict `game.txt`**: exactly 8 lines × 8 allowed chars (`KQRBNPkqrbnp_`),
  one optional trailing newline. Never silently repair; never overwrite or
  delete a corrupted save.
- **Advice must stay stronger than the AI**: keep `ADVICE_DEPTH > AI_DEPTH`.
  From the initial board the advice must be one of `e2e4/d2d4/g1f3/c2c4` and
  never an edge-pawn push — PST values in `engine.py` are tuned for this, so
  re-validate the opening advice after touching the tables.
- Supporting files must never run a game on import.
- `game.txt` and `__pycache__/` are gitignored; do not commit them.

## When fixing bugs

Modify only what is strictly necessary; do not break behavior that already
works. The 12 mandatory "critical bugs" and their guards are listed in
`COVERAGE.md` / `VERIFICATION.md` — preserve those guarantees.

## Git

Development branch: `claude/python-dev-instructions-cu9ek9`. Do not push to
other branches without explicit permission, and do not open a PR unless asked.
