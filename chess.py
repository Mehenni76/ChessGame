#!/usr/bin/env python3
"""Console chess game entry point (the only script run directly by the user).

Usage:
    python3 chess.py            # show the board (and advice) without playing
    python3 chess.py <move>     # play one White move, then one Black AI move

The program never reads interactive input, operates exclusively through the
single optional command-line argument, prints all messages in English, and
terminates immediately after producing its output.

Persistent state lives in game.txt in the current directory. The board is
loaded from it when present and saved back after a completed pair of moves;
it is deleted when the game ends.
"""

import sys

import board as board_mod
import rules
import engine


def _print_board(board):
    """Print the board with coordinates to stdout."""
    print(board_mod.render_board(board))


def _print_advice(board):
    """Print the advice line for White if a legal move exists."""
    move = engine.select_advice_move(board)
    if move is not None:
        print("ADVICE: Best move for White is %s." % rules.move_to_str(move))


def _game_over_message(status):
    """Map a status constant to its mandatory GAME OVER message."""
    if status == rules.WHITE_WINS:
        return "GAME OVER: White wins."
    if status == rules.BLACK_WINS:
        return "GAME OVER: Black wins."
    return "GAME OVER: Stalemate."


def _emit_game_over(board, status):
    """Print the game-over output, delete the save, and exit successfully."""
    print(_game_over_message(status))
    _print_board(board)
    board_mod.delete_save()
    sys.exit(0)


def _emit_normal(board):
    """Print the ongoing-game output (board plus advice) and exit."""
    _print_board(board)
    _print_advice(board)
    sys.exit(0)


def _error(message, board=None, exit_code=1):
    """Report an error in English, optionally show the board, then exit."""
    print("Error: " + message, file=sys.stderr)
    if board is not None:
        _print_board(board)
    sys.exit(exit_code)


def _load_or_initial():
    """Return the board from game.txt if present, else the initial board.

    Corrupted or unreadable saves raise the corresponding exceptions, which
    the caller turns into the proper error output.
    """
    if board_mod.save_exists():
        return board_mod.load_board()
    return board_mod.initial_board()


def _resolve_player_move(board, parsed):
    """Match a parsed move against White's legal moves, handling promotion.

    Returns the concrete legal move to apply, or raises IllegalMoveError.
    """
    fr, fc, tr, tc, promo = parsed
    candidates = [
        m for m in rules.generate_legal_moves(board, rules.WHITE)
        if m[0] == fr and m[1] == fc and m[2] == tr and m[3] == tc
    ]
    if not candidates:
        raise rules.IllegalMoveError("illegal move.")

    if promo is None:
        # A non-promotion move yields a single candidate with promo None.
        for m in candidates:
            if m[4] is None:
                return m
        # Otherwise this is a promotion square; default to a queen.
        for m in candidates:
            if m[4] == "Q":
                return m
        raise rules.IllegalMoveError("illegal move.")

    target = promo.upper()
    for m in candidates:
        if m[4] == target:
            return m
    raise rules.IllegalMoveError("illegal move.")


def _run_no_argument():
    """No-argument mode: show the board (and advice) without playing.

    game.txt is never created here if it does not already exist.
    """
    try:
        board = _load_or_initial()
    except board_mod.CorruptSaveError:
        _error("game.txt is corrupted.")
    except board_mod.UnreadableSaveError:
        _error("game.txt cannot be read.")

    status = rules.game_status(board, rules.WHITE)
    if status != rules.ONGOING:
        _emit_game_over(board, status)
    _emit_normal(board)


def _run_with_move(arg):
    """One-argument mode: play one White move then one Black AI move."""
    # Load the board first so it can be shown alongside any later error.
    try:
        board = _load_or_initial()
    except board_mod.CorruptSaveError:
        _error("game.txt is corrupted.")
    except board_mod.UnreadableSaveError:
        _error("game.txt cannot be read.")

    # Strictly parse the move notation.
    try:
        parsed = rules.parse_move(arg)
    except rules.InvalidNotationError as exc:
        _error(str(exc), board)

    # Resolve and validate legality, then apply the White move.
    try:
        player_move = _resolve_player_move(board, parsed)
    except rules.IllegalMoveError:
        _error("illegal move %r." % arg, board)

    board = rules.apply_move(board, player_move)

    # Game may end immediately after White's move (Black to move next).
    status = rules.game_status(board, rules.BLACK)
    if status != rules.ONGOING:
        _emit_game_over(board, status)

    # The AI plays one legal Black move via Alpha-Beta search.
    ai_move = engine.select_ai_move(board)
    if ai_move is None:
        # No legal Black move: classify and end the game.
        _emit_game_over(board, rules.game_status(board, rules.BLACK))
    board = rules.apply_move(board, ai_move)

    # Game may end after the AI move (White to move next).
    status = rules.game_status(board, rules.WHITE)
    if status != rules.ONGOING:
        _emit_game_over(board, status)

    # Ongoing: persist the new state, then display board and advice.
    try:
        board_mod.save_board(board)
    except board_mod.WriteError:
        _error("game.txt cannot be written.")

    _emit_normal(board)


def main(argv):
    """Dispatch on the argument count, enforcing at most one move argument."""
    args = argv[1:]
    if len(args) == 0:
        _run_no_argument()
    elif len(args) == 1:
        _run_with_move(args[0])
    else:
        # More than one argument: show the current board if it can be loaded.
        board = None
        try:
            board = _load_or_initial()
        except (board_mod.CorruptSaveError, board_mod.UnreadableSaveError):
            board = None
        _error("too many arguments; provide at most one move.", board)


if __name__ == "__main__":
    main(sys.argv)
