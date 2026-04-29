from __future__ import annotations

import argparse

from legacy_python.debug_tools import format_batch_history_summary, load_batch_history


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze archived batch experiment history.")
    parser.add_argument("history_path", type=str, help="Path to batch history JSON file")
    parser.add_argument("--max", type=int, default=20, help="Maximum number of recent entries to display")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    history = load_batch_history(args.history_path)
    print(format_batch_history_summary(history, max_entries=args.max))


if __name__ == "__main__":
    main()

