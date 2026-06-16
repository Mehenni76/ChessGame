# Implementation Contract

This artifact declares the complete and exact source file list for the console
chess game. No source file outside this list is part of the deliverable, and
every file declared here exists and is required.

## Command-line entry point (the only script run directly)

| File | Responsibility |
|------|----------------|
| `chess.py` | Single CLI entry point. Argument dispatch (0 or 1 argument), high-level game flow, error handling, and all console output. |

## Supporting source files (declared, cohesive, single-responsibility)

| File | Responsibility |
|------|----------------|
| `board.py` | Internal 8×8 board representation, coordinate conversions, strict `game.txt` validation / load / save / delete, and coordinate-aware display. |
| `rules.py` | Strict move-notation parsing, pseudo-legal move generation, attack detection, legal-move filtering, check / checkmate / stalemate detection, move application (including promotion), and game-status classification. |
| `engine.py` | Deterministic positional evaluation, deterministic move ordering, minimax search with Alpha-Beta pruning, Black AI move selection (depth 2), and stronger White advice selection (depth 3) with chess-priority tie-breaking. |

## Guarantees

- None of the supporting files request interactive input.
- None of the supporting files run a game on import.
- `chess.py` is the only script executed directly by the user.
- No temporary or unauthorized Python source files remain in the workspace.
- The only non-Python file created at runtime is `game.txt` (the save file).

## Separation of internal contracts (mandatory)

- Pseudo-legal move generation: `rules.generate_pseudo_moves`.
- Attack detection (independent of movement): `rules.square_attacked_by`.
- Legal-move filtering: `rules.generate_legal_moves`.
- Check / checkmate / stalemate: `rules.in_check`, `rules.is_checkmate`, `rules.is_stalemate`, `rules.game_status`.
- Strict move parsing: `rules.parse_move`.
- Strict `game.txt` validation: `board.parse_raw_content` / `board.load_board`.
- AI move selection: `engine.select_ai_move`.
- Advice move selection: `engine.select_advice_move`.
- Alpha-Beta search: `engine.alphabeta`.
