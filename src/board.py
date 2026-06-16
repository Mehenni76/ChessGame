"""Board representation, coordinate helpers and game.txt persistence.

Responsibilities (single concern: state + storage + display):
- Internal 8x8 board representation.
- Coordinate conversions between chess notation and internal indices.
- Strict validation / loading / saving of game.txt.
- Console display with coordinates.

This module never reads interactive input and never runs a game on import.

Board orientation (mandatory specification):
- Row 0 represents rank 8.
- Row 7 represents rank 1.
- Column 0 represents file a.
- Column 7 represents file h.
"""

# Allowed raw characters inside game.txt and the internal board.
ALLOWED_CHARS = set("KQRBNPkqrbnp_")
EMPTY = "_"

# The mandatory initial position, raw 8 lines of 8 characters.
INITIAL_RAW = [
    "rnbqkbnr",
    "pppppppp",
    "________",
    "________",
    "________",
    "________",
    "PPPPPPPP",
    "RNBQKBNR",
]

GAME_FILE = "game.txt"


class CorruptSaveError(Exception):
    """Raised when game.txt exists but does not match the strict format."""


class UnreadableSaveError(Exception):
    """Raised when game.txt exists but cannot be read."""


class WriteError(Exception):
    """Raised when game.txt cannot be written."""


def initial_board():
    """Return a fresh starting board as a list of 8 lists of 8 characters."""
    return [list(row) for row in INITIAL_RAW]


def board_to_raw_lines(board):
    """Convert the internal board to the raw 8 lines of 8 characters."""
    return ["".join(row) for row in board]


# --- Coordinate helpers -----------------------------------------------------

def file_to_col(file_char):
    """Map a file character a..h to a column index 0..7."""
    return ord(file_char) - ord("a")


def rank_to_row(rank_char):
    """Map a rank character 1..8 to a row index 0..7 (rank 8 -> row 0)."""
    return 8 - int(rank_char)


def col_to_file(col):
    """Map a column index 0..7 back to a file character a..h."""
    return chr(ord("a") + col)


def row_to_rank(row):
    """Map a row index 0..7 back to a rank character 1..8."""
    return str(8 - row)


def square_to_coord(row, col):
    """Return coordinate notation (e.g. 'e4') for an internal square."""
    return col_to_file(col) + row_to_rank(row)


def in_bounds(row, col):
    """Return True if the square is on the board."""
    return 0 <= row < 8 and 0 <= col < 8


# --- Strict persistence -----------------------------------------------------

def _validate_raw_lines(lines):
    """Validate the exact line structure of a raw board.

    Rules (strict, no silent repair):
    - exactly 8 lines,
    - each line exactly 8 characters,
    - only allowed characters,
    - no empty extra line, no missing line, no extra line, no spaces.
    Raises CorruptSaveError on any violation.
    """
    if len(lines) != 8:
        raise CorruptSaveError(
            "game.txt must contain exactly 8 lines (found %d)." % len(lines)
        )
    for line in lines:
        if len(line) != 8:
            raise CorruptSaveError(
                "Each line of game.txt must contain exactly 8 characters."
            )
        for ch in line:
            if ch not in ALLOWED_CHARS:
                raise CorruptSaveError(
                    "game.txt contains an invalid character: %r." % ch
                )


def parse_raw_content(content):
    """Parse and strictly validate raw game.txt content into a board.

    A single trailing newline after the eighth line is accepted; any further
    line is rejected. Empty lines are never filtered and spaces are never
    stripped before validation.
    """
    lines = content.split("\n")
    # Accept exactly one optional trailing newline: drop a single trailing
    # empty element produced by a terminating '\n'. A second trailing newline
    # leaves an empty line in place, which validation will then reject.
    if lines and lines[-1] == "":
        lines = lines[:-1]
    _validate_raw_lines(lines)
    return [list(line) for line in lines]


def load_board(path=GAME_FILE):
    """Load and validate the board from game.txt.

    Raises:
    - UnreadableSaveError if the file exists but cannot be read,
    - CorruptSaveError if the content is invalid.
    """
    try:
        with open(path, "r", encoding="utf-8") as handle:
            content = handle.read()
    except OSError as exc:
        raise UnreadableSaveError(str(exc))
    return parse_raw_content(content)


def save_board(board, path=GAME_FILE):
    """Write the raw board (8 lines of 8 characters) to game.txt.

    Raises WriteError on any write failure.
    """
    raw = "\n".join(board_to_raw_lines(board)) + "\n"
    try:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(raw)
    except OSError as exc:
        raise WriteError(str(exc))


def delete_save(path=GAME_FILE):
    """Delete game.txt if it exists. Missing file is not an error."""
    import os

    try:
        os.remove(path)
    except FileNotFoundError:
        pass
    except OSError:
        # Deleting the save is best effort; failure must not crash the run
        # because the game-over result has already been produced.
        pass


def save_exists(path=GAME_FILE):
    """Return True if game.txt exists."""
    import os

    return os.path.exists(path)


# --- Display ----------------------------------------------------------------

def render_board(board):
    """Return the board rendered with coordinates as a single string.

    Format (mandatory):
        two spaces + 'abcdefgh'
        rank number + one space + 8 board characters, for each rank 8..1
    """
    out = ["  abcdefgh"]
    for row in range(8):
        out.append(row_to_rank(row) + " " + "".join(board[row]))
    return "\n".join(out)
