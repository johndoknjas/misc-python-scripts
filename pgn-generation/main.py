import argparse
import chess
import chess.pgn

nodes_written = 0

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a legal chess PGN variation tree stress test.",
        usage="python main.py <max_nodes> <branches_per_position> <max_fullmove_number>",
    )
    parser.add_argument(
        "max_nodes",
        type=int,
        help="Maximum number of move nodes to write, e.g. 50000",
    )
    parser.add_argument(
        "branches_per_position",
        type=int,
        help="Maximum number of legal moves to branch at each position, e.g. 4",
    )
    parser.add_argument(
        "max_fullmove_number",
        type=int,
        help="Maximum fullmove number to generate up to, e.g. 20",
    )
    args = parser.parse_args()
    if any(
        x <= 0 for x in (
            args.max_nodes, args.branches_per_position, args.max_fullmove_number
        )
    ):
        parser.error("only positive cli arguments allowed")
    return args

def move_sort_key(board: chess.Board, move: chess.Move) -> tuple:
    """
    Stable-ish ordering that avoids always picking weird UCI-first moves.
    """
    san = board.san(move)
    is_capture = board.is_capture(move)
    gives_check = board.gives_check(move)
    return (
        not gives_check,
        not is_capture,
        san,
        move.uci(),
    )

def add_variations(
    node: chess.pgn.GameNode,
    board: chess.Board,
    max_nodes: int,
    branches_per_position: int,
    max_fullmove_number: int,
) -> None:
    """
    Recursively add legal moves as PGN variations under `node`.
    The first move added becomes the mainline; later moves become side variations.
    """
    global nodes_written

    if nodes_written >= max_nodes or board.is_game_over() or board.fullmove_number > max_fullmove_number:
        return

    chosen_moves = sorted(
        list(board.legal_moves), key=lambda m: move_sort_key(board, m)
    )[:branches_per_position]

    for move in chosen_moves:
        if nodes_written >= max_nodes:
            break

        child_board = board.copy()
        child_board.push(move)

        child_node = node.add_variation(move)
        nodes_written += 1

        add_variations(
            child_node,
            child_board,
            max_nodes,
            branches_per_position,
            max_fullmove_number,
        )

def main() -> None:
    global nodes_written
    nodes_written = 0
    args = parse_args()
    game = chess.pgn.Game()
    board = chess.Board()
    add_variations(
        game,
        board,
        args.max_nodes,
        args.branches_per_position,
        args.max_fullmove_number,
    )
    exporter = chess.pgn.StringExporter(
        headers=True,
        variations=True,
        comments=True,
        columns=120,
    )
    pgn_text = game.accept(exporter)
    with open("legal_variation_tree.pgn", "w", encoding="utf-8") as f:
        f.write(pgn_text)
        f.write("\n")
    print(f"Wrote legal_variation_tree.pgn with {nodes_written} move nodes.")
    print(f"Max nodes: {args.max_nodes}")
    print(f"Branches per position: {args.branches_per_position}")
    print(f"Max fullmove number: {args.max_fullmove_number}")

if __name__ == "__main__":
    main()