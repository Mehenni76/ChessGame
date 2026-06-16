"""Search and evaluation: Alpha-Beta AI move and stronger player advice.

This module provides clearly separated contracts for:
- a deterministic positional evaluation function,
- deterministic move ordering (captures first) for better pruning,
- a real minimax search with Alpha-Beta pruning using alpha/beta bounds,
- selecting the black AI move (shallower search),
- selecting the recommended white move (strictly deeper search) with
  deterministic chess-priority tie-breaking.

Determinism: no randomness is used anywhere. The same position always yields
the same AI move and the same advice.
"""

from board import EMPTY
from rules import (
    WHITE,
    BLACK,
    color_of,
    apply_move,
    in_check,
    king_missing,
    find_king,
    generate_legal_moves,
    generate_pseudo_moves,
    move_to_str,
)

# Material values (centipawns). Evaluation is positive when good for Black.
PIECE_VALUES = {
    "p": 100,
    "n": 320,
    "b": 330,
    "r": 500,
    "q": 900,
    "k": 20000,
}

# Search bounds and mate score. MATE dominates any material evaluation.
INF = 10 ** 9
MATE = 1_000_000

# AI uses a fixed shallow depth; the advice engine uses a strictly deeper one.
AI_DEPTH = 2
ADVICE_DEPTH = 3

# Central squares in internal coordinates: d5,e5 (row 3) and d4,e4 (row 4).
CENTRAL_SQUARES = {(3, 3), (3, 4), (4, 3), (4, 4)}

# Piece-square tables from White's perspective, row 0 = rank 8.
# Black reuses each table mirrored vertically (row 7-r) with a negated sign.
PST = {
    "P": [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [5, 5, 10, 27, 27, 10, 5, 5],
        [0, 0, 5, 40, 40, 5, 0, 0],
        [5, -5, -10, 0, 0, -10, -5, 5],
        [5, 10, 10, -20, -20, 10, 10, 5],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ],
    "N": [
        [-50, -40, -30, -30, -30, -30, -40, -50],
        [-40, -20, 0, 0, 0, 0, -20, -40],
        [-30, 0, 10, 15, 15, 10, 0, -30],
        [-30, 5, 15, 20, 20, 15, 5, -30],
        [-30, 0, 15, 20, 20, 15, 0, -30],
        [-30, 5, 10, 15, 15, 10, 5, -30],
        [-40, -20, 0, 5, 5, 0, -20, -40],
        [-50, -40, -30, -30, -30, -30, -40, -50],
    ],
    "B": [
        [-20, -10, -10, -10, -10, -10, -10, -20],
        [-10, 0, 0, 0, 0, 0, 0, -10],
        [-10, 0, 5, 10, 10, 5, 0, -10],
        [-10, 5, 5, 10, 10, 5, 5, -10],
        [-10, 0, 10, 10, 10, 10, 0, -10],
        [-10, 10, 10, 10, 10, 10, 10, -10],
        [-10, 5, 0, 0, 0, 0, 5, -10],
        [-20, -10, -10, -10, -10, -10, -10, -20],
    ],
    "R": [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [5, 10, 10, 10, 10, 10, 10, 5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [0, 0, 0, 5, 5, 0, 0, 0],
    ],
    "Q": [
        [-20, -10, -10, -5, -5, -10, -10, -20],
        [-10, 0, 0, 0, 0, 0, 0, -10],
        [-10, 0, 5, 5, 5, 5, 0, -10],
        [-5, 0, 5, 5, 5, 5, 0, -5],
        [0, 0, 5, 5, 5, 5, 0, -5],
        [-10, 5, 5, 5, 5, 5, 0, -10],
        [-10, 0, 5, 0, 0, 0, 0, -10],
        [-20, -10, -10, -5, -5, -10, -10, -20],
    ],
    "K": [
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-20, -30, -30, -40, -40, -30, -30, -20],
        [-10, -20, -20, -20, -20, -20, -20, -10],
        [20, 20, 0, 0, 0, 0, 20, 20],
        [20, 30, 10, 0, 0, 10, 30, 20],
    ],
}


def _pst_value(kind, row, col, side):
    """Return the piece-square bonus for a piece of the given side."""
    if side == WHITE:
        return PST[kind][row][col]
    # Mirror vertically for Black.
    return PST[kind][7 - row][col]


def evaluate(board):
    """Deterministic positional evaluation, positive when good for Black.

    Includes (as mandated for the advice engine):
    - material balance,
    - piece-square placement (center control, development, central
      occupation, edge-pawn penalties and king safety are encoded here),
    - a mobility term (difference in available moves),
    - an explicit central-square control term.
    """
    score = 0

    # Material balance plus piece-square placement.
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece == EMPTY:
                continue
            side = color_of(piece)
            kind = piece.upper()
            value = PIECE_VALUES[kind.lower()] + _pst_value(kind, row, col, side)
            if side == BLACK:
                score += value
            else:
                score -= value

    # Mobility: a side with more available moves is generally better off.
    black_mobility = len(generate_pseudo_moves(board, BLACK))
    white_mobility = len(generate_pseudo_moves(board, WHITE))
    score += (black_mobility - white_mobility) * 1

    # Explicit central-square control term, attacks count for both sides.
    from rules import square_attacked_by

    for (r, c) in CENTRAL_SQUARES:
        if square_attacked_by(board, r, c, BLACK):
            score += 6
        if square_attacked_by(board, r, c, WHITE):
            score -= 6

    return score


# --- Move ordering ----------------------------------------------------------

def order_moves(board, moves):
    """Order moves with captures first (by victim value) for better pruning.

    The ordering is a stable sort, so the underlying deterministic generation
    order is preserved among moves of equal capture priority.
    """
    def capture_score(move):
        victim = board[move[2]][move[3]]
        if victim == EMPTY:
            return -1
        return PIECE_VALUES[victim.lower()]

    return sorted(moves, key=lambda m: -capture_score(m))


# --- Alpha-Beta search ------------------------------------------------------

def alphabeta(board, depth, alpha, beta, side):
    """Minimax search with Alpha-Beta pruning.

    Black is the maximising side and White is the minimising side because the
    evaluation is positive when the position favours Black. The alpha and beta
    bounds are used to prune branches that cannot influence the result.
    """
    # King-missing is terminal and dominates.
    if find_king(board, BLACK) is None:
        return -MATE
    if find_king(board, WHITE) is None:
        return MATE

    if depth == 0:
        return evaluate(board)

    moves = order_moves(board, generate_legal_moves(board, side))

    if not moves:
        if in_check(board, side):
            # Side to move is checkmated. Prefer faster mates via depth.
            return -(MATE + depth) if side == BLACK else (MATE + depth)
        # Stalemate is a draw.
        return 0

    if side == BLACK:
        value = -INF
        for move in moves:
            child = apply_move(board, move)
            value = max(value, alphabeta(child, depth - 1, alpha, beta, WHITE))
            alpha = max(alpha, value)
            if alpha >= beta:
                break  # beta cut-off
        return value
    else:
        value = INF
        for move in moves:
            child = apply_move(board, move)
            value = min(value, alphabeta(child, depth - 1, alpha, beta, BLACK))
            beta = min(beta, value)
            if beta <= alpha:
                break  # alpha cut-off
        return value


# --- AI move selection (Black) ----------------------------------------------

def select_ai_move(board, depth=AI_DEPTH):
    """Choose Black's move using Alpha-Beta. Deterministic.

    Black maximises the evaluation. Ties are broken by the lexicographically
    smallest coordinate string so the same position always yields the same
    move.
    """
    moves = order_moves(board, generate_legal_moves(board, BLACK))
    if not moves:
        return None

    best_move = None
    best_value = -INF
    for move in moves:
        child = apply_move(board, move)
        value = alphabeta(child, depth - 1, -INF, INF, WHITE)
        if best_move is None or value > best_value or (
            value == best_value
            and move_to_str(move) < move_to_str(best_move)
        ):
            best_value = value
            best_move = move
    return best_move


# --- Advice tie-breaking (White) --------------------------------------------

def _advice_tiebreak(board, move):
    """Return a chess-priority rank for a White move (lower is preferred).

    Order: winning/equal material capture, central pawn move, knight
    development, bishop development, queen/rook activity, other moves, and
    edge-pawn pushes last.
    """
    fr, fc, tr, tc, _ = move
    piece = board[fr][fc]
    victim = board[tr][tc]
    is_edge_pawn_push = piece == "P" and fc in (0, 7) and victim == EMPTY

    base = 10 if is_edge_pawn_push else 9
    ranks = [base]

    if victim != EMPTY:
        if PIECE_VALUES[victim.lower()] >= PIECE_VALUES[piece.lower()]:
            ranks.append(2)  # winning or equal material
    if piece == "P" and (tr, tc) in CENTRAL_SQUARES:
        ranks.append(4)
    if piece == "N" and fr == 7 and tr != 7:
        ranks.append(5)  # knight development
    if piece == "B" and fr == 7 and tr != 7:
        ranks.append(6)  # bishop development
    if piece in ("Q", "R"):
        ranks.append(8)  # queen/rook activity

    return min(ranks)


def select_advice_move(board, depth=ADVICE_DEPTH):
    """Choose the recommended White move using a strictly deeper Alpha-Beta.

    White minimises the (Black-positive) evaluation. Among moves with equal
    search value, deterministic chess-priority tie-breaking is applied, then
    the lexicographically smallest coordinate string as a final tie-break.
    """
    moves = order_moves(board, generate_legal_moves(board, WHITE))
    if not moves:
        return None

    scored = []
    for move in moves:
        child = apply_move(board, move)
        value = alphabeta(child, depth - 1, -INF, INF, BLACK)
        scored.append((value, move))

    best_value = min(value for value, _ in scored)
    best = None
    best_key = None
    for value, move in scored:
        if value != best_value:
            continue
        key = (_advice_tiebreak(board, move), move_to_str(move))
        if best is None or key < best_key:
            best = move
            best_key = key
    return best
