"""Chess rules engine: move generation, attacks, check, legality, end states.

This module keeps strictly separate, clearly named contracts for:
- strict move-notation parsing,
- pseudo-legal move generation,
- attacked-square / attack detection,
- legal-move filtering,
- check / checkmate / stalemate detection,
- applying a move (including promotion),
- game-over status.

Pseudo-legal moves and attacked squares are NOT confused. In particular pawn
movement squares are computed separately from pawn attack squares.

A move is represented as a 5-tuple:
    (from_row, from_col, to_row, to_col, promo)
where promo is None for a normal move, or the (correctly cased) piece letter
to promote to for a pawn-promotion move.
"""

from board import (
    EMPTY,
    in_bounds,
    file_to_col,
    rank_to_row,
    square_to_coord,
)

WHITE = "w"
BLACK = "b"

# Knight and king relative offsets.
KNIGHT_OFFSETS = [
    (-2, -1), (-2, 1), (-1, -2), (-1, 2),
    (1, -2), (1, 2), (2, -1), (2, 1),
]
KING_OFFSETS = [
    (-1, -1), (-1, 0), (-1, 1), (0, -1),
    (0, 1), (1, -1), (1, 0), (1, 1),
]
ROOK_DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
BISHOP_DIRS = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

PROMO_PIECES = set("qrbnQRBN")


class InvalidNotationError(Exception):
    """Raised when the move argument is not valid coordinate notation."""


class IllegalMoveError(Exception):
    """Raised when a syntactically valid move is not legal in the position."""


# --- Piece helpers ----------------------------------------------------------

def color_of(piece):
    """Return WHITE, BLACK or None for a board character."""
    if piece == EMPTY:
        return None
    return WHITE if piece.isupper() else BLACK


def is_enemy(piece, side):
    """True if piece belongs to the opponent of side."""
    c = color_of(piece)
    return c is not None and c != side


def is_friend(piece, side):
    """True if piece belongs to side."""
    return color_of(piece) == side


def find_king(board, side):
    """Return (row, col) of side's king, or None if it is missing."""
    target = "K" if side == WHITE else "k"
    for row in range(8):
        for col in range(8):
            if board[row][col] == target:
                return (row, col)
    return None


# --- Strict move-notation parsing ------------------------------------------

def parse_move(arg):
    """Strictly parse coordinate notation into a move tuple.

    Accepts exactly 4 characters (normal move) or 5 characters (promotion).
    The promotion letter, if present, must be one of q, r, b, n (any case).
    Any other length, file, rank or suffix is rejected. The returned promo is
    kept exactly as written; callers normalise its case for the moving side.
    """
    if not isinstance(arg, str) or len(arg) not in (4, 5):
        raise InvalidNotationError("invalid move notation %r." % arg)

    f_file, f_rank, t_file, t_rank = arg[0], arg[1], arg[2], arg[3]
    if f_file not in "abcdefgh" or t_file not in "abcdefgh":
        raise InvalidNotationError("invalid move notation %r." % arg)
    if f_rank not in "12345678" or t_rank not in "12345678":
        raise InvalidNotationError("invalid move notation %r." % arg)

    promo = None
    if len(arg) == 5:
        if arg[4] not in PROMO_PIECES:
            raise InvalidNotationError("invalid promotion piece in %r." % arg)
        promo = arg[4]

    fr = rank_to_row(f_rank)
    fc = file_to_col(f_file)
    tr = rank_to_row(t_rank)
    tc = file_to_col(t_file)
    return (fr, fc, tr, tc, promo)


def move_to_str(move):
    """Render a move tuple back to coordinate notation."""
    fr, fc, tr, tc, promo = move
    text = square_to_coord(fr, fc) + square_to_coord(tr, tc)
    if promo is not None:
        text += promo.lower()
    return text


# --- Attack detection (separate from movement) -----------------------------

def square_attacked_by(board, row, col, attacker):
    """Return True if square (row, col) is attacked by the attacker side.

    Attack rules are computed directly and independently from movement rules.
    Crucially, pawns attack diagonally only and never attack the square in
    front of them.
    """
    # Pawn attacks. A white pawn sits one row below the square it attacks; a
    # black pawn sits one row above.
    if attacker == WHITE:
        for dc in (-1, 1):
            r, c = row + 1, col + dc
            if in_bounds(r, c) and board[r][c] == "P":
                return True
    else:
        for dc in (-1, 1):
            r, c = row - 1, col + dc
            if in_bounds(r, c) and board[r][c] == "p":
                return True

    # Knight attacks.
    knight = "N" if attacker == WHITE else "n"
    for dr, dc in KNIGHT_OFFSETS:
        r, c = row + dr, col + dc
        if in_bounds(r, c) and board[r][c] == knight:
            return True

    # King attacks.
    king = "K" if attacker == WHITE else "k"
    for dr, dc in KING_OFFSETS:
        r, c = row + dr, col + dc
        if in_bounds(r, c) and board[r][c] == king:
            return True

    # Sliding attacks: rook/queen orthogonally, bishop/queen diagonally.
    rook = "R" if attacker == WHITE else "r"
    bishop = "B" if attacker == WHITE else "b"
    queen = "Q" if attacker == WHITE else "q"

    for dr, dc in ROOK_DIRS:
        r, c = row + dr, col + dc
        while in_bounds(r, c):
            cell = board[r][c]
            if cell != EMPTY:
                if cell == rook or cell == queen:
                    return True
                break
            r += dr
            c += dc

    for dr, dc in BISHOP_DIRS:
        r, c = row + dr, col + dc
        while in_bounds(r, c):
            cell = board[r][c]
            if cell != EMPTY:
                if cell == bishop or cell == queen:
                    return True
                break
            r += dr
            c += dc

    return False


def in_check(board, side):
    """Return True if side's king is currently attacked."""
    king_pos = find_king(board, side)
    if king_pos is None:
        # No king on the board: treated as a terminal/king-missing condition
        # elsewhere; for check purposes report False.
        return False
    opponent = BLACK if side == WHITE else WHITE
    return square_attacked_by(board, king_pos[0], king_pos[1], opponent)


# --- Pseudo-legal move generation -------------------------------------------

def _add_pawn_promotions(moves, fr, fc, tr, tc, side):
    """Append all four promotion moves for a pawn reaching the last rank."""
    pieces = "QRBN" if side == WHITE else "qrbn"
    for piece in pieces:
        moves.append((fr, fc, tr, tc, piece))


def _gen_pawn(board, row, col, side, moves):
    """Generate pseudo-legal pawn moves (movement and diagonal captures)."""
    if side == WHITE:
        direction = -1
        start_row = 6
        last_row = 0
    else:
        direction = 1
        start_row = 1
        last_row = 7

    # Single forward move to an empty square (never diagonal, never a capture).
    one = row + direction
    if in_bounds(one, col) and board[one][col] == EMPTY:
        if one == last_row:
            _add_pawn_promotions(moves, row, col, one, col, side)
        else:
            moves.append((row, col, one, col, None))
        # Initial double move, only from the starting rank and over empty path.
        two = row + 2 * direction
        if row == start_row and board[two][col] == EMPTY:
            moves.append((row, col, two, col, None))

    # Diagonal captures only, and only onto an enemy piece.
    for dc in (-1, 1):
        r, c = row + direction, col + dc
        if in_bounds(r, c) and is_enemy(board[r][c], side):
            if r == last_row:
                _add_pawn_promotions(moves, row, col, r, c, side)
            else:
                moves.append((row, col, r, c, None))


def _gen_step(board, row, col, side, offsets, moves):
    """Generate single-step moves (knight, king) onto empty or enemy squares."""
    for dr, dc in offsets:
        r, c = row + dr, col + dc
        if in_bounds(r, c) and not is_friend(board[r][c], side):
            moves.append((row, col, r, c, None))


def _gen_slide(board, row, col, side, dirs, moves):
    """Generate sliding moves, stopping at the first occupied square."""
    for dr, dc in dirs:
        r, c = row + dr, col + dc
        while in_bounds(r, c):
            cell = board[r][c]
            if cell == EMPTY:
                moves.append((row, col, r, c, None))
            else:
                if is_enemy(cell, side):
                    moves.append((row, col, r, c, None))
                break
            r += dr
            c += dc


def generate_pseudo_moves(board, side):
    """Generate all pseudo-legal moves for side (own-king safety not checked)."""
    moves = []
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if color_of(piece) != side:
                continue
            kind = piece.upper()
            if kind == "P":
                _gen_pawn(board, row, col, side, moves)
            elif kind == "N":
                _gen_step(board, row, col, side, KNIGHT_OFFSETS, moves)
            elif kind == "K":
                _gen_step(board, row, col, side, KING_OFFSETS, moves)
            elif kind == "R":
                _gen_slide(board, row, col, side, ROOK_DIRS, moves)
            elif kind == "B":
                _gen_slide(board, row, col, side, BISHOP_DIRS, moves)
            elif kind == "Q":
                _gen_slide(board, row, col, side, ROOK_DIRS + BISHOP_DIRS, moves)
    return moves


# --- Applying moves ---------------------------------------------------------

def apply_move(board, move):
    """Return a new board with move applied (promotion handled)."""
    fr, fc, tr, tc, promo = move
    new_board = [row[:] for row in board]
    piece = new_board[fr][fc]
    new_board[fr][fc] = EMPTY

    side = color_of(piece)
    if piece.upper() == "P" and (tr == 0 or tr == 7):
        # Promotion. Use the requested piece if any, defaulting to a queen,
        # always cased for the moving side.
        letter = promo if promo is not None else "q"
        letter = letter.upper() if side == WHITE else letter.lower()
        new_board[tr][tc] = letter
    else:
        new_board[tr][tc] = piece
    return new_board


# --- Legal-move filtering ---------------------------------------------------

def generate_legal_moves(board, side):
    """Return pseudo-legal moves that do not leave side's own king in check.

    This single filter simultaneously covers:
    - a king never moving onto an attacked square,
    - pinned pieces never exposing their own king,
    - any move that would leave the king in check being rejected.
    """
    legal = []
    for move in generate_pseudo_moves(board, side):
        after = apply_move(board, move)
        if not in_check(after, side):
            legal.append(move)
    return legal


# --- End-of-game detection --------------------------------------------------

def king_missing(board):
    """Return True if either king has been removed from the board."""
    return find_king(board, WHITE) is None or find_king(board, BLACK) is None


def is_checkmate(board, side):
    """True if side is in check and has no legal move."""
    return in_check(board, side) and not generate_legal_moves(board, side)


def is_stalemate(board, side):
    """True if side is not in check but has no legal move."""
    return not in_check(board, side) and not generate_legal_moves(board, side)


# Game status outcome strings.
ONGOING = "ongoing"
WHITE_WINS = "white_wins"
BLACK_WINS = "black_wins"
STALEMATE = "stalemate"


def game_status(board, side_to_move):
    """Classify the position for the given side to move.

    Returns one of ONGOING, WHITE_WINS, BLACK_WINS, STALEMATE.
    A missing king is treated as an immediate loss for the missing side.
    """
    white_king = find_king(board, WHITE)
    black_king = find_king(board, BLACK)
    if black_king is None:
        return WHITE_WINS
    if white_king is None:
        return BLACK_WINS

    if generate_legal_moves(board, side_to_move):
        return ONGOING

    # No legal move available for the side to move.
    if in_check(board, side_to_move):
        return BLACK_WINS if side_to_move == WHITE else WHITE_WINS
    return STALEMATE
