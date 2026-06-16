# Requirement Coverage Matrix

Each mandatory requirement from `src/Instruction.md` is mapped to the code that
implements it and the validation that exercises it.

## Output & CLI constraints

| Requirement | Implementation | Validation |
|-------------|----------------|------------|
| Never request interactive input | No `input()` anywhere; CLI only | Source inspection |
| At most one command-line argument | `chess.py:main` | "too many args" test |
| Terminate immediately after output | `sys.exit` in every path | All runs exit promptly |
| All messages in English | All `print` strings | Output inspection |
| Error → message + board (if possible) + exit non-zero | `chess.py:_error` | Invalid notation / illegal move tests |

## Board, display & persistence

| Requirement | Implementation | Validation |
|-------------|----------------|------------|
| 8×8 board, row 0 = rank 8, col 0 = file a | `board.py` orientation | Display tests |
| Display: `  abcdefgh`, rank + space + 8 chars | `board.render_board` | Output matches spec example |
| `game.txt` raw 8×8 only, no coordinates | `board.save_board` | `cat game.txt` after a move |
| Strict validation (no silent repair) | `board.parse_raw_content` | 7-line, blank-extra, bad-char, 9-char tests |
| Trailing newline accepted, extra line rejected | `board.parse_raw_content` | Valid-with-newline & blank-extra tests |
| No-arg mode never creates `game.txt` | `chess._run_no_argument` (no save) | "not created" test |
| Corrupted file not overwritten/deleted | error paths never save/delete | "still present" test |
| Unreadable file → error, exit non-zero | `board.load_board` → `UnreadableSaveError` | directory-as-file test |

## Move parsing & rules

| Requirement | Implementation | Validation |
|-------------|----------------|------------|
| Strict 4/5-char parsing, reject overlong | `rules.parse_move` | `e2e4444` rejected |
| Valid promotion pieces only (q,r,b,n) | `rules.parse_move` | `e7e8x` rejected |
| Default promotion to queen | `rules.apply_move` | `e7e8` → Q |
| Underpromotion honored | `_resolve_player_move` | `e7e8n` → N |
| Pawn diagonal only when capturing (Bug 11) | `rules._gen_pawn` | rule assertion |
| Pawn never captures forward (Bug 12) | `rules._gen_pawn` | rule assertion |
| Pawn never knight-shaped (Bug 10) | `rules._gen_pawn` | rule assertion |
| Pawn attacks diagonally only (Bug 1) | `rules.square_attacked_by` | king-into-check test |
| King never moves into check (Bug 2) | `rules.generate_legal_moves` | king test |
| Pinned piece cannot expose king (Bug 3) | `rules.generate_legal_moves` | pinned-knight test |
| Sliding pieces stop at first occupied (Bug 4) | `rules._gen_slide` | blocked-rook test |
| Check / checkmate / stalemate detection | `rules.in_check` / `is_checkmate` / `is_stalemate` | end-state assertions |
| King-missing = loss | `rules.game_status` | end-state assertion |

## AI & advice

| Requirement | Implementation | Validation |
|-------------|----------------|------------|
| Real Alpha-Beta with alpha/beta bounds (Bug 8) | `engine.alphabeta` | source + self-play |
| AI plays Black, deterministic, depth ≥ 2 | `engine.select_ai_move` (depth 2) | repeatable runs |
| Move ordering captures first | `engine.order_moves` | source |
| Material values per spec | `engine.PIECE_VALUES` | source |
| Eval positive for Black, negative for White | `engine.evaluate` | source |
| Advice deeper than AI (≥ 3, AI = 2) | `engine.ADVICE_DEPTH = 3` | source |
| Advice legal, never leaves White in check | `generate_legal_moves` only | self-play |
| Advice eval incl. material, center, development, mobility, king safety, edge-pawn penalty | `engine.evaluate` + PST + mobility + center term | source |
| Opening ∈ {e2e4,d2d4,g1f3,c2c4} | PST tuning | initial-board test → `e2e4` |
| Opening never a2a3/h2h3/a2a4/h2h4 | PST + tie-break | initial-board test |
| Mate-in-1 recommended | mate scoring in `alphabeta` | back-rank mate test |
| Deterministic tie-breaking | `engine._advice_tiebreak` + lex order | repeatable runs |

## End of game

| Requirement | Implementation | Validation |
|-------------|----------------|------------|
| GAME OVER messages exact wording | `chess._game_over_message` | mate test |
| Game over: message + board, no advice | `chess._emit_game_over` | mate test |
| Delete `game.txt` on game over | `chess._emit_game_over` | "deleted" test |
| Advice only when game not over | `chess._emit_normal` vs `_emit_game_over` | mate test (no advice) |
| stderr empty on success | errors go to stderr only | "stderr bytes: 0" test |
