from __future__ import annotations

import argparse

from debug_tools.export_analysis import load_export_payload, summarize_export_payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze an exported simulation summary.")
    parser.add_argument("input_path", type=str, help="Path to exported JSON/CSV file")
    parser.add_argument(
        "--format",
        dest="input_format",
        choices=("auto", "json", "csv"),
        default="auto",
        help="Input format (default: auto from extension)",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    payload = load_export_payload(args.input_path, input_format=args.input_format)
    print(summarize_export_payload(payload))


if __name__ == "__main__":
    main()
