#!/usr/bin/env python3
"""
moveRevealer.py — interactive "next move per game" stepper.

Inputs supported:
  1) File path:   python moveRevealer.py games.pgn
  2) Inline text: python moveRevealer.py --text "1.e4c52.Nf3d6..."
  3) Inline text: python moveRevealer.py "1.e4c52.Nf3d6..."   (if not an existing file)
  4) stdin:       cat games.pgn | python moveRevealer.py

Output format:
  --format MODE

MODE values:
  full   : "Game 1: 12... Nf6"
  bare   : "Nf6"
  pgn    : "12... Nf6"
  uci    : "Game 1: 12... g8f6"
  fen    : "Game 1: 12... <FEN after move>"

Commands:
  n / <enter> : print next move for each game (and advance)
  p           : show progress (ply counters) for each game
  r           : reset all games back to start
  q           : quit

Notes:
  - This script supports “squished” movetext like: 1.e4c52.Nf3d6...
  - It avoids python-chess PGN parsing warnings by detecting squished input first.
"""

from __future__ import annotations

import argparse
import io
import os
import re
import sys
from dataclasses import dataclass
from typing import List, Optional, Tuple

try:
    import chess
    import chess.pgn
except ImportError:
    print("Missing dependency: python-chess\n\nInstall with:\n  pip install python-chess\n", file=sys.stderr)
    sys.exit(1)

RESULT_TOKENS = {"1-0", "0-1", "1/2-1/2", "*"}


def _strip_noise(text: str) -> str:
    """Remove common non-movetext junk that appears in scraped pages."""
    # Drop everything after "SETTINGS" (common in scraped pages)
    text = re.split(r"\bSETTINGS\b", text, maxsplit=1, flags=re.IGNORECASE)[0]

    # Remove PGN headers like [Event "..."]
    text = re.sub(r"(?m)^\s*\[.*?\]\s*$", "", text)

    # Remove comments {...} and semicolon-to-eol comments
    text = re.sub(r"\{[^}]*\}", " ", text)
    text = re.sub(r"(?m);[^\n]*$", " ", text)

    # Remove variations (...) naively (doesn't handle deep nesting, but ok)
    while True:
        new = re.sub(r"\([^()]*\)", " ", text)
        if new == text:
            break
        text = new

    # Remove NAGs like $1
    text = re.sub(r"\$\d+", " ", text)

    return text.strip()


def _extract_movetext_blob(text: str) -> str:
    """
    Extract a best-effort movetext blob:
      - strip noise
      - keep only characters typically used in SAN + move numbers
      - collapse whitespace
    """
    text = _strip_noise(text)
    # Keep SAN-ish chars, digits, dots, slashes, hyphens, plus/hash, equals, whitespace
    text = re.sub(r"[^A-Za-z0-9\.\-xO\+#+#+#+#+=/\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _parse_squished_san(movetext: str) -> List["chess.Move"]:
    """
    Parse movetext even if moves are squished together (e.g., '1.e4c52.Nf3d6...').

    Returns list of chess.Move from the initial position.
    """
    s = movetext.replace(" ", "").strip()
    board = chess.Board()
    moves: List[chess.Move] = []

    # Consume move numbers like "12." or "12..." (both happen in messy sources)
    move_no_re = re.compile(r"^\d+\.(?:\.\.)?")
    move_no_re2 = re.compile(r"^\d+\.\.\.")

    while s:
        # Eat move numbers
        m = move_no_re2.match(s) or move_no_re.match(s)
        if m:
            s = s[m.end():]
            continue

        # Stop on result tokens
        for res in sorted(RESULT_TOKENS, key=len, reverse=True):
            if s.startswith(res):
                return moves

        # Find legal moves whose SAN is a prefix; take the longest match
        best: Optional[Tuple[str, chess.Move]] = None
        for mv in board.legal_moves:
            san = board.san(mv)
            if s.startswith(san):
                if best is None or len(san) > len(best[0]):
                    best = (san, mv)

        if best is None:
            # Forgiving match: allow missing trailing +/#
            best2: Optional[Tuple[str, chess.Move]] = None
            for mv in board.legal_moves:
                san = board.san(mv)
                san_loose = san.rstrip("+").rstrip("#")
                if s.startswith(san_loose):
                    if best2 is None or len(san_loose) > len(best2[0]):
                        best2 = (san_loose, mv)

            if best2 is None:
                context = s[:40]
                raise ValueError(
                    "Could not parse movetext at: "
                    f"{context!r}\n"
                    "Tip: ensure the input is SAN (as in PGN movetext)."
                )

            san_loose, mv = best2
            moves.append(mv)
            board.push(mv)
            s = s[len(san_loose):]
            continue

        san, mv = best
        moves.append(mv)
        board.push(mv)
        s = s[len(san):]

    return moves


def looks_like_squished_movetext(text: str) -> bool:
    """
    Heuristic: squished movetext often has move numbers like '1.' and *no* spaces
    between SAN tokens, e.g. '1.e4c52.Nf3d6...'
    """
    blob = _extract_movetext_blob(text)
    if not blob:
        return False
    has_move_numbers = re.search(r"\d+\.", blob) is not None
    has_whitespace = re.search(r"\s", blob) is not None
    return has_move_numbers and not has_whitespace


def load_games_from_text(text: str) -> List[List["chess.Move"]]:
    """
    Try:
      - If squished: parse with our squished parser (avoids python-chess PGN warnings)
      - Else: parse PGN normally (one or many games)
      - If PGN yields no games, fallback to squished parser anyway
    """
    # 1) Squished detection: bypass PGN parser so it can't emit warnings
    if looks_like_squished_movetext(text):
        blob = _extract_movetext_blob(text)
        return [_parse_squished_san(blob)] if blob else []

    # 2) Normal PGN parse
    pgn_io = io.StringIO(text)
    games_moves: List[List[chess.Move]] = []
    while True:
        game = chess.pgn.read_game(pgn_io)
        if game is None:
            break
        games_moves.append(list(game.mainline_moves()))

    if games_moves:
        return games_moves

    # 3) Fallback: treat as a single movetext blob
    blob = _extract_movetext_blob(text)
    return [_parse_squished_san(blob)] if blob else []


def ply_prefix(ply: int) -> str:
    move_no = ply // 2 + 1
    is_black = (ply % 2 == 1)
    return f"{move_no}..." if is_black else f"{move_no}."


@dataclass
class GameState:
    moves: List["chess.Move"]
    ply: int = 0

    def reset(self) -> None:
        self.ply = 0

    def finished(self) -> bool:
        return self.ply >= len(self.moves)

    def _board_before(self) -> "chess.Board":
        b = chess.Board()
        for mv in self.moves[: self.ply]:
            b.push(mv)
        return b

    def peek_san(self) -> Optional[str]:
        if self.finished():
            return None
        b = self._board_before()
        return b.san(self.moves[self.ply])

    def peek_uci(self) -> Optional[str]:
        if self.finished():
            return None
        return self.moves[self.ply].uci()

    def fen_after_next(self) -> Optional[str]:
        if self.finished():
            return None
        b = self._board_before()
        b.push(self.moves[self.ply])
        return b.fen()

    def advance(self) -> Optional["chess.Move"]:
        if self.finished():
            return None
        mv = self.moves[self.ply]
        self.ply += 1
        return mv


def format_output(mode: str, game_index_1: int, state: GameState) -> Optional[str]:
    if state.finished():
        return None

    prefix = ply_prefix(state.ply)

    if mode == "bare":
        return state.peek_san()

    if mode == "pgn":
        return f"{prefix} {state.peek_san()}"

    if mode == "full":
        return f"Game {game_index_1}: {prefix} {state.peek_san()}"

    if mode == "uci":
        return f"Game {game_index_1}: {prefix} {state.peek_uci()}"

    if mode == "fen":
        return f"Game {game_index_1}: {prefix} {state.fen_after_next()}"

    raise ValueError(f"Unknown format mode: {mode}")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "input",
        nargs="?",
        help="PGN file OR inline movetext/PGN string (if not an existing file). Reads stdin if omitted.",
    )
    ap.add_argument(
        "--text",
        help="Inline movetext/PGN string. If provided, it overrides positional input.",
    )
    ap.add_argument(
        "--format",
        default="full",
        choices=["full", "bare", "pgn", "uci", "fen"],
        help="Output format mode",
    )
    return ap.parse_args()


def read_input(args: argparse.Namespace) -> str:
    # Highest priority: explicit --text
    if args.text is not None:
        return args.text

    # Next: positional input, decide file vs inline text
    if args.input:
        if os.path.exists(args.input) and os.path.isfile(args.input):
            with open(args.input, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        return args.input  # treat as inline text

    # Fallback: stdin
    return sys.stdin.read()


def main() -> None:
    args = parse_args()
    text = read_input(args)

    games = load_games_from_text(text)
    if not games:
        print("No games found.", file=sys.stderr)
        sys.exit(1)

    states = [GameState(moves=g) for g in games]

    print(f"Loaded {len(states)} game(s). Output format: {args.format}")
    print("Commands: n/<enter>=next, p=progress, r=reset, q=quit")

    while True:
        try:
            cmd = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if cmd in {"q", "quit", "exit"}:
            return

        if cmd in {"", "n", "next"}:
            # Print *current* next move for each game, then advance.
            for i, st in enumerate(states, start=1):
                out = format_output(args.format, i, st)
                if out is None:
                    print(f"Game {i}: (finished)")
                else:
                    print(out)
                    st.advance()
            continue

        if cmd in {"p", "prog", "progress"}:
            for i, st in enumerate(states, start=1):
                print(f"Game {i}: ply {st.ply}/{len(st.moves)}")
            continue

        if cmd in {"r", "reset"}:
            for st in states:
                st.reset()
            print("Reset.")
            continue

        print("Unknown command. Use n, p, r, q.")


if __name__ == "__main__":
    main()
