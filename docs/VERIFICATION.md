# Final Verification Report

Date: 2026-06-16. Environment: Python 3.11.

## Implemented features

- Console chess, White = human player, Black = deterministic Alpha-Beta AI.
- Board display with coordinates; raw 8×8 persistence in `game.txt`.
- Full simplified rule set: king, queen, rook, bishop, knight and pawn moves;
  captures; pawn single/double/diagonal moves; promotion (default queen and
  underpromotion); check, checkmate and stalemate detection; king-missing
  termination.
- Strict move-notation parsing and strict `game.txt` validation.
- Minimax search with real Alpha-Beta pruning (alpha/beta bounds, beta/alpha
  cut-offs, capture-first move ordering).
- Black AI at depth 2; White advice engine at depth 3 (strictly deeper) with
  positional evaluation and chess-priority tie-breaking.
- Two modes: no argument (display + advice, no play, no file creation) and one
  argument (White move, then Black AI move, then save + display + advice).

## Manual validation commands and observed results

```
# Opening advice from the initial board
$ python3 src/chess.py
... ADVICE: Best move for White is e2e4.        # in the mandatory allowed set

# Play one move; AI replies; state persisted
$ python3 src/chess.py e2e4                          # board shown, advice g1f3, game.txt written

# Error handling
$ python3 src/chess.py e2e4 d2d4   -> "too many arguments..."        exit 1
$ python3 src/chess.py e2e4444     -> "invalid move notation ..."    exit 1
$ python3 src/chess.py z2e4        -> "invalid move notation ..."    exit 1
$ python3 src/chess.py e7e8x       -> "invalid promotion piece ..."  exit 1
$ python3 src/chess.py e3e4        -> "illegal move ..."             exit 1

# Strict game.txt validation (corrupted -> error, file preserved)
# 7 lines / blank extra line / bad char / 9-char line  -> "game.txt is corrupted." exit 1
# valid + single trailing newline -> accepted

# Promotion
$ python3 src/chess.py e7e8        -> promotes to Q
$ python3 src/chess.py e7e8n       -> promotes to N (underpromotion)

# Checkmate (back-rank): a1a8
$ python3 src/chess.py a1a8
GAME OVER: White wins.        # board shown, no advice, game.txt deleted, exit 0

# stderr empty on success: confirmed (0 bytes)
```

## Critical-bug prevention (all confirmed by assertions)

1. Pawn attack confusion — pawns attack diagonally only. ✔
2. King moving into check — rejected. ✔
3. Pinned piece exposing king — rejected. ✔
4. Sliding piece moving through another piece — stops at first occupied. ✔
5. Corrupted save silently repaired — rejected, file preserved. ✔
6. Invalid promotion accepted — rejected. ✔
7. Overlong move argument accepted — rejected. ✔
8. Alpha-Beta not implemented — real implementation in `engine.alphabeta`. ✔
9. Advice repeats edge pawn pushes — opening is central/developing; edge pawn
   pushes are ranked last and never recommended from the initial board. ✔
10. Pawn moving like a knight — impossible in pawn generation. ✔
11. Pawn diagonal move without capture — only generated onto enemy pieces. ✔
12. Pawn forward capture — forward moves only onto empty squares. ✔

## Performance

- Advice (depth 3) from the initial position: ~0.5 s.
- Advice on a busy midgame position: ~0.55 s.

Both well within an acceptable single-execution budget.

## Notes

- The program is fully deterministic and local; no randomness, no network, no
  external model.
- Threefold repetition is intentionally not implemented (out of scope per the
  specification); the AI/advice may therefore shuffle pieces in a balanced
  position, which remains legal and deterministic.
