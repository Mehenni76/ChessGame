OBJECTIVE
Develop a simplified chess game playable in console mode, in which the player faces a basic AI using the Alpha-Beta pruning algorithm.

The program must implement a robust functional subset of chess rules sufficient to play complete games in console mode.
The AI does not need to be perfect, but it must use a minimax search with Alpha-Beta pruning.

The program must also display a move recommendation for the player after the board.
The recommendation must be stronger than the opponent AI, so that a human tester can follow the suggested moves and have a better chance of winning.

The program must be deterministic and fully local.

OUTPUT CONSTRAINTS (MANDATORY)

- The delivered program must NEVER request interactive input from the user:
  no input(), no keyboard reading, no user prompt.
- The program must execute and terminate immediately after displaying the expected result,
  regardless of the situation, success or error.
- The program must operate exclusively via command-line arguments.
- The game script chess.py must accept AT MOST ONE command-line argument:
  - a single move written in coordinate notation, for example:
    e2e4
    g1f3
    e7e8q
- In case of an error, such as invalid argument, illegal move, corrupted save file, unreadable save file, or write error, the program must:
  1) display a clear error message IN ENGLISH,
  2) display the current board state if possible,
  3) then terminate immediately.
- ALL messages, outputs, error messages, game over messages, and advice messages must be written IN ENGLISH.

GAME SPECIFICATION

Board representation

- The board is an 8×8 chessboard.
- Internally and in game.txt, the board is represented as exactly 8 lines of 8 characters.
- Row 0 represents rank 8.
- Row 7 represents rank 1.
- Column 0 represents file a.
- Column 7 represents file h.

Characters:

- White pieces, controlled by the player:
  - K : white king
  - Q : white queen
  - R : white rook
  - B : white bishop
  - N : white knight
  - P : white pawn

- Black pieces, controlled by the AI:
  - k : black king
  - q : black queen
  - r : black rook
  - b : black bishop
  - n : black knight
  - p : black pawn

- Empty square:
  - _

Initial raw board:

rnbqkbnr
pppppppp
________
________
________
________
PPPPPPPP
RNBQKBNR

BOARD DISPLAY WITH COORDINATES (MANDATORY)

The board display must include chess coordinates to make the game readable in console mode.

The board must be displayed with:
- file coordinates at the top: abcdefgh
- rank coordinates on the left: 8 to 1

The displayed board must use this exact format:

  abcdefgh
8 rnbqkbnr
7 pppppppp
6 ________
5 ________
4 ________
3 ________
2 PPPPPPPP
1 RNBQKBNR

Display rules:
- The first line must be exactly:
  two spaces followed by abcdefgh
- Each board row must start with the rank number, then one space, then exactly 8 board characters.
- No coordinates must be stored in game.txt.
- game.txt must still contain only the raw 8 lines of 8 board characters.

PERSISTENT GAME STATE

- The game state is stored in a file named game.txt in the current directory.
- The program is responsible for creating and deleting this file.
- Storage format of game.txt:
  - exactly 8 lines of 8 characters,
  - same raw board format as the internal board,
  - allowed characters only:
    KQRBNPkqrbnp_
- game.txt must NEVER contain:
  - coordinate headers,
  - rank numbers,
  - spaces,
  - advice text,
  - game over text,
  - debug text.
- At startup:
  - if game.txt exists, the board must be loaded from this file;
  - otherwise, the initial board is used.
- The program must NEVER assume that game.txt exists.
- If game.txt exists but is invalid or corrupted, this is an error case.

STRICT SAVE FILE VALIDATION (MANDATORY)

When reading game.txt, the program must validate the raw file exactly.
It must not silently repair, trim away, ignore, or normalize invalid board content.

Valid game.txt format:
- exactly 8 lines,
- each line must contain exactly 8 characters,
- allowed characters only: KQRBNPkqrbnp_
- no empty extra line,
- no missing line,
- no extra line,
- no coordinate line,
- no spaces.

Implementation requirement:
- Do not filter out empty lines.
- Do not use logic equivalent to ignoring blank lines.
- Do not strip meaningful spaces before validation.
- Read the raw file content and validate the exact line structure.
- If the file has a trailing newline after the eighth line, it is acceptable.
- Any additional line after the eighth board line must be rejected.

If the file does not strictly match this format, it must be treated as corrupted.

MODE WITHOUT ARGUMENT

When the program is launched with no argument:
- the current board is displayed with coordinates;
- NO move is played, neither player nor AI;
- game.txt must NOT be created if it does not already exist;
- the program must display a move recommendation under the board if the game is not over;
- the program terminates immediately.

MODE WITH ONE ARGUMENT

When the program is launched with exactly one argument:
- load the board from game.txt if it exists, otherwise initialize the starting board;
- validate the player move;
- apply the player move;
- immediately check whether the game is over;
- if the game is not over, the AI automatically plays one legal black move;
- immediately check whether the game is over after the AI move;
- if the game is not over, save the updated raw board to game.txt;
- display the board with coordinates;
- display a move recommendation under the board if the game is not over;
- terminate immediately.

MOVE NOTATION

Moves must use coordinate notation:
- source square + destination square

Examples:
- e2e4
- g1f3
- a7a8q

Files are:
a, b, c, d, e, f, g, h

Ranks are:
1, 2, 3, 4, 5, 6, 7, 8

Promotion may be specified by appending one lowercase or uppercase piece letter:
- q, r, b, n
- Q, R, B, N

If a white pawn reaches rank 8 without a promotion suffix, it must promote to queen by default.
If a black pawn reaches rank 1, the AI must promote to queen by default.

STRICT MOVE PARSING (MANDATORY)

The move argument must be either:
- exactly 4 characters for a normal move,
- exactly 5 characters for a promotion move.

Valid normal move format:
- file rank file rank
- example: e2e4

Valid promotion move format:
- file rank file rank promotion_piece
- example: e7e8q

The only valid promotion pieces are:
- q, r, b, n
- Q, R, B, N

Any other length, character, file, rank, or promotion suffix must be rejected with an error.
The program must not ignore extra characters.

SIMPLIFIED CHESS RULES

The program must implement the following rules:
- Normal legal moves for:
  - king,
  - queen,
  - rook,
  - bishop,
  - knight,
  - pawn.
- Captures.
- Pawn single move.
- Pawn initial double move.
- Pawn diagonal capture.
- Pawn promotion.
- Check detection.
- A move that leaves the moving side’s own king in check is illegal.
- Checkmate detection.
- Stalemate detection.

The program is NOT required to implement:
- castling,
- en passant,
- fifty-move rule,
- threefold repetition,
- insufficient material detection,
- chess clock,
- algebraic notation.

TURN MODEL

- The player always controls white.
- The AI always controls black.
- Each execution with one argument represents:
  1) one white move by the player,
  2) then one black move by the AI if the game is not over.
- The program does not need to store whose turn it is, because the turn order is fixed.

ROBUSTNESS REQUIREMENT (MANDATORY)

This program must not be a superficial chess-like prototype.
It must implement the specified rules rigorously enough for automated validation to detect incorrect chess behavior.

Before writing the final code, the agent must reason about and implement separate logic for:
- move generation,
- attack detection,
- check detection,
- legal move filtering,
- checkmate detection,
- stalemate detection,
- board persistence,
- command-line parsing,
- AI search,
- Alpha-Beta pruning,
- player move recommendation.

Pseudo-legal moves and attacked squares must NOT be confused.

In particular:
- pawn movement squares are not the same as pawn attack squares;
- pawns attack diagonally only;
- kings may not move onto attacked squares;
- a move leaving the moving side's king in check is illegal;
- pinned pieces must not be allowed to expose their own king;
- sliding pieces must not move through occupied squares;
- corrupted game.txt content must not be silently repaired;
- invalid promotion pieces must not be accepted;
- overlong move arguments must not be accepted.

The implementation must include dedicated functions or clearly separated internal contracts for:
- generating pseudo-legal moves,
- generating attacked squares or testing whether a square is attacked,
- filtering legal moves,
- detecting check,
- detecting checkmate,
- detecting stalemate,
- parsing move notation strictly,
- validating game.txt strictly,
- selecting the AI move,
- selecting the recommended player move.

CRITICAL BUGS TO PREVENT (MANDATORY)

The implementation must explicitly prevent these bugs:

Bug 1: Pawn attack confusion
- A pawn must not attack the square directly in front of it.
- A pawn attacks diagonally only.

Bug 2: King moving into check
- A king must never be allowed to move onto a square attacked by an enemy piece.

Bug 3: Pinned piece exposing king
- A piece pinned to its own king must not be allowed to move if doing so exposes the king.

Bug 4: Sliding piece moving through another piece
- Rooks, bishops, and queens must stop at the first occupied square.

Bug 5: Corrupted save file silently repaired
- game.txt must be validated exactly.
- The program must not ignore empty lines, extra lines, missing lines, spaces, or invalid characters.

Bug 6: Invalid promotion accepted
- A promotion suffix other than q, r, b, n, Q, R, B, N must be rejected.

Bug 7: Overlong move argument accepted
- Moves longer than 5 characters must be rejected.

Bug 8: Alpha-Beta not actually implemented
- The task is incomplete if the AI does not contain a real Alpha-Beta pruning implementation.

Bug 9: Advice chooses repeated edge pawn pushes
- The advice must not recommend repeated rook pawn pushes in the opening when central or developing moves are available.

Bug 10: Pawn moving like a knight
- A pawn must never be allowed to move in a knight-shaped pattern.
- Knight-shaped movement is valid only for knights.

Bug 11: Pawn diagonal move without capture
- A pawn must not move diagonally to an empty square.
- Pawn diagonal movement is legal only when capturing an opposing piece, except for en passant which is not implemented.

Bug 12: Pawn forward capture
- A pawn must not capture a piece directly in front of it.
- Pawn forward movement is legal only to an empty square.

END OF GAME

The game continues as long as:
- neither king is checkmated,
- the side to move is not stalemated,
- both kings are still present on the board.

As soon as one of the following is detected:
- white checkmates black,
- black checkmates white,
- stalemate,
- one king is missing due to a capture in simplified logic,

the program must:
- display an explicit GAME OVER message IN ENGLISH;
- display the final board with coordinates;
- delete game.txt;
- terminate immediately;
- display no move recommendation after GAME OVER.

Required GAME OVER messages:
- If white wins:
  GAME OVER: White wins.
- If black wins:
  GAME OVER: Black wins.
- If stalemate:
  GAME OVER: Stalemate.

OUTPUT DISPLAY RULES

Normal non-error, non-game-over output must contain:
1) exactly one coordinate header line,
2) exactly 8 board lines with rank coordinates,
3) exactly one advice line.

Example:

  abcdefgh
8 rnbqkbnr
7 pppppppp
6 ________
5 ________
4 ________
3 ________
2 PPPPPPPP
1 RNBQKBNR
ADVICE: Best move for White is e2e4.

Rules:
- The board must always be displayed with coordinates.
- No extra blank lines.
- No extraneous text before or after the expected output.
- On success, stderr must be empty.
- The advice line must appear only if the game is not over.
- The advice line must start exactly with:
  ADVICE: 
- If no legal move is available, no advice line must be displayed and the game must be reported as GAME OVER.

Game-over output must contain:
1) exactly one GAME OVER line,
2) exactly one coordinate header line,
3) exactly 8 board lines with rank coordinates.

Example:

GAME OVER: White wins.
  abcdefgh
8 ____k___
7 ________
6 ________
5 ________
4 ________
3 ________
2 ________
1 ____K___

AI SPECIFICATION

General AI behavior:
- The AI must play black.
- The AI must always choose a legal move.
- The AI must never make a move that leaves the black king in check.
- The AI does not need to be perfect.
- The AI must be deterministic.

Search algorithm:
- The AI must use minimax with Alpha-Beta pruning.
- The function implementing the search must clearly use alpha and beta bounds.
- The AI search depth must be at least 2 plies.
- A fixed depth of 2 plies is acceptable for the opponent AI.
- The AI must not use randomness.
- The same board position must always produce the same AI move.

Move ordering:
- The AI should evaluate captures before non-captures when possible.
- This is intended to make Alpha-Beta pruning more effective.
- The ordering must remain deterministic.

Position evaluation:

The AI evaluation function must be deterministic and based at least on material values:

- pawn: 100
- knight: 320
- bishop: 330
- rook: 500
- queen: 900
- king: 20000

The evaluation must be positive when the position is better for black.
The evaluation must be negative when the position is better for white.

The evaluation may also include simple positional bonuses, but this is optional.

Alpha-Beta pruning requirement:
- The source code must contain an actual Alpha-Beta pruning implementation.
- The Alpha-Beta implementation must use alpha and beta bounds in the recursive search.
- The implementation must be structured so automated validation can inspect or exercise the pruning logic.
- The program output must not display debug counters during normal execution.

PLAYER ADVICE SPECIFICATION

General advice behavior:
- After displaying the board, the program must display one advice line if the game is not over.
- The advice must recommend the best move for White from the current displayed position.
- The advice must be deterministic.
- The advice must be legal.
- The advice must use the same coordinate notation accepted by the program.
- The advice must be generated after the AI move, so that it recommends the next White move.

Advice output format:

ADVICE: Best move for White is <move>.

Example:

ADVICE: Best move for White is e2e4.

The recommended move must be playable directly as the next command-line argument.

Advice engine strength:
- The advice engine must be stronger than the opponent AI.
- The opponent AI may use Alpha-Beta depth 2.
- The advice engine must use Alpha-Beta with a strictly greater search depth than the opponent AI.
- The advice engine depth must be at least 3 plies.
- Depth 4 is preferred if performance remains acceptable.
- The advice engine must search from White’s perspective.
- The advice engine must use the same legal move generation as the game engine.
- The advice engine must never recommend an illegal move.
- The advice engine must never recommend a move that leaves the White king in check.

Advice purpose:
- The advice is intended to help the user test a winning or strong game without having to think.
- Following the advice should generally produce better play than choosing random legal moves.
- If a forced win is visible within the advice search depth, the advice should choose the winning line.
- If an immediate checkmate move is available for White, the advice must recommend it.
- If White is in check, the advice must recommend a legal move that gets out of check.
- If White can capture a high-value undefended piece and no immediate tactical loss is detected within search depth, the advice should prefer that capture.

PLAYER ADVICE QUALITY REQUIREMENT (MANDATORY)

The advice engine must not rely only on material evaluation.
It must include deterministic positional evaluation so that opening and quiet positions produce sensible chess moves.

The evaluation used by the advice engine must include at least:
- material balance,
- center control,
- piece development,
- mobility,
- king safety,
- pawn advancement penalties for edge pawns in the opening,
- bonus for developing knights and bishops,
- bonus for occupying or attacking central squares.

Opening behavior requirement:
- From the initial board, the advice must recommend one of these moves:
  - e2e4
  - d2d4
  - g1f3
  - c2c4

- The advice must not recommend:
  - a2a3
  - h2h3
  - a2a4
  - h2h4

from the initial board.

Repeated edge pawn pushing prevention:
- The advice must not repeatedly recommend pushing the same rook pawn in the opening unless it wins material or avoids immediate tactical loss.
- The advice must not recommend a2a3 from the initial position.
- The advice must not recommend a3a4 immediately after a2a3 if stronger developing or central moves are available.
- The advice must not recommend a4a5 immediately after a2a3 and a3a4 if stronger developing or central moves are available.

Advice tie-breaking:

If several moves have the same evaluation, the advice engine must use deterministic chess-priority tie-breaking in this order:

1) immediate checkmate,
2) winning material safely,
3) escaping check,
4) central pawn moves,
5) developing knights,
6) developing bishops,
7) castling is ignored because castling is not implemented,
8) improving queen or rook activity,
9) other legal moves,
10) edge pawn moves last.

ERROR HANDLING

Invalid argument count:
- If more than one command-line argument is provided:
  - display an error message in English,
  - display the current board state with coordinates if possible,
  - terminate immediately with a non-zero exit code.

Invalid move notation:
- If the argument is not valid coordinate notation:
  - display an error message in English,
  - display the current board with coordinates,
  - terminate immediately with a non-zero exit code.

Illegal move:
- If the requested move is illegal:
  - display an error message in English,
  - display the current board with coordinates,
  - terminate immediately with a non-zero exit code.

Corrupted game.txt:
- If game.txt exists but does not respect the required format:
  - display an error message in English,
  - display the raw board state if possible,
  - terminate immediately with a non-zero exit code,
  - do NOT overwrite or delete game.txt.

Unreadable game.txt:
- If game.txt cannot be read:
  - display an error message in English,
  - terminate immediately with a non-zero exit code.

File write error:
- If game.txt cannot be written:
  - display an error message in English,
  - terminate immediately with a non-zero exit code.

IMPLEMENTATION DISCIPLINE (MANDATORY)

The agent must not consider the task complete until:
- chess.py exists.
- chess.py is the only command-line entry point executed directly by the user.
- the implementation source files declared by the planning phase exist.
- the declared implementation source files together contain the complete implementation.
- the program can be executed from the command line through chess.py.
- the program respects the full functional specification above.
- the final answer lists the implemented features and the commands used to manually validate the program.

If Alpha-Beta pruning is not implemented, the task is incomplete.
If the advice engine is missing, the task is incomplete.
If the advice opening quality rules are ignored, the task is incomplete.
If mandatory chess rules are omitted, the task is incomplete.
If any declared implementation source file is missing, the task is incomplete.
If unauthorized temporary Python source files remain in the workspace, the task is incomplete.

BUG FIXING CONSTRAINT

When fixing a bug:
- do not break existing behavior that already works,
- modify only what is strictly necessary to fix the observed failure.

SOURCE FILE CONSTRAINT

- The implementation must be split into a small number of cohesive Python source files.
- The planning phase must determine the exact source file list before implementation begins.
- The source decomposition must keep each file cognitively limited and focused on one responsibility.
- The implementation must include exactly one command-line entry point named chess.py.
- chess.py must be the only script executed directly by the user.
- Supporting source files may be created only if they are declared in the implementation contract produced by the planning.
- Supporting source files must not request interactive input and must not execute a game run on import.
- No unnecessary or temporary Python source files may remain in the workspace after execution.
- Automated test files are handled by validation tasks and are not part of the deliverable source file count.
- Additional non-Python files may be created only if they are required by the program behavior, such as game.txt during execution or validation artifacts during validation tasks.

DELIVERABLES

- chess.py
- implementation contract artifact declaring the complete source file list
- requirement coverage matrix
- all supporting source files declared by the implementation contract artifact
- validation artifacts produced by validation tasks
- final verification report

ABSOLUTE PROHIBITIONS

- Do NOT use input().
- Do NOT request any information from the user.
- Do NOT use random behavior.
- Do NOT use network access.
- Do NOT use any external AI model.
- Do NOT implement superficial placeholder chess logic.
- Do NOT rely on hardcoded move scripts instead of legal move generation.