# ChessGame

A simplified, fully local, deterministic console chess game. The human plays
White; a basic AI using minimax with Alpha-Beta pruning plays Black. After the
board, the program prints a move recommendation for White produced by a
stronger (deeper) Alpha-Beta search.

## Usage

```bash
# Show the current board (and advice) without playing a move
python3 src/chess.py

# Play one White move (coordinate notation); the AI then replies
python3 src/chess.py e2e4
python3 src/chess.py g1f3
python3 src/chess.py e7e8q   # promotion (q, r, b, n; defaults to queen)
```

The program accepts at most one argument, never reads interactive input, prints
all messages in English, and terminates immediately. Game state is stored as a
raw 8×8 board in `game.txt` and deleted when the game ends.

`game.txt` is created in the current working directory (where you run the
command), not inside `src/`.

## Source layout

- `src/chess.py` — command-line entry point and game flow.
- `src/board.py` — board representation, display and `game.txt` persistence.
- `src/rules.py` — move generation, attacks, legality and end-state detection.
- `src/engine.py` — evaluation, Alpha-Beta search, AI move and player advice.

See `docs/CONTRACT.md`, `docs/COVERAGE.md` and `docs/VERIFICATION.md` for the implementation
contract, requirement coverage matrix and verification report.
