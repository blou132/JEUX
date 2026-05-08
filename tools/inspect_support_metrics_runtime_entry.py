from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_BASELINE_PATH = Path("outputs/ci/support_metrics_baseline.jsonl")
DEFAULT_CURRENT_PATH = Path("outputs/ci/support_metrics_current.jsonl")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect the latest support metrics runtime JSONL entry for baseline/current. "
            "Debug/observation only."
        )
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=DEFAULT_BASELINE_PATH,
        help="Baseline runtime JSONL path.",
    )
    parser.add_argument(
        "--current",
        type=Path,
        default=DEFAULT_CURRENT_PATH,
        help="Current runtime JSONL path.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Return non-zero if a file is missing, unreadable, or has no valid JSON object entry.",
    )
    return parser


def _find_key_paths(value: Any, target_key: str, current_path: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key_name, child in value.items():
            next_path = key_name if current_path == "" else f"{current_path}.{key_name}"
            if key_name == target_key:
                paths.append(next_path)
            paths.extend(_find_key_paths(child, target_key, next_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            next_path = f"{current_path}[{index}]" if current_path else f"[{index}]"
            paths.extend(_find_key_paths(child, target_key, next_path))
    return paths


def _format_paths(paths: list[str]) -> str:
    if not paths:
        return "none"
    return ", ".join(paths)


def _as_list_of_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    normalized: list[str] = []
    for item in value:
        text = str(item).strip()
        if text != "":
            normalized.append(text)
    return normalized


def _read_jsonl(path: Path) -> tuple[list[dict[str, Any]], int]:
    records: list[dict[str, Any]] = []
    invalid_lines = 0
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line == "":
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            invalid_lines += 1
            continue
        if not isinstance(parsed, dict):
            invalid_lines += 1
            continue
        records.append(parsed)
    return records, invalid_lines


def _inspect_latest_entry(label: str, path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError("%s file not found: %s" % (label, path))
    try:
        records, invalid_lines = _read_jsonl(path)
    except OSError as exc:
        raise RuntimeError("unable to read %s file: %s" % (label, str(exc))) from exc
    if not records:
        raise RuntimeError("%s file has no valid JSON object entry: %s" % (label, path))

    entry = records[-1]
    support_gate_paths = _find_key_paths(entry, "support_gate")
    champion_support_paths = _find_key_paths(entry, "champion_support")
    champion_resolution_paths = _find_key_paths(entry, "champion_resolution")
    missing_payload_fields_paths = _find_key_paths(entry, "missing_payload_fields")
    payload_has_support_gate_paths = _find_key_paths(entry, "payload_has_support_gate")
    payload_has_champion_support_paths = _find_key_paths(entry, "payload_has_champion_support")
    payload_has_champion_resolution_paths = _find_key_paths(entry, "payload_has_champion_resolution")

    return {
        "label": label,
        "path": str(path),
        "entries_read": len(records),
        "invalid_json_lines": invalid_lines,
        "top_level_keys": sorted(entry.keys()),
        "top_level_keys_count": len(entry.keys()),
        "has_support_gate": len(support_gate_paths) > 0,
        "has_champion_support": len(champion_support_paths) > 0,
        "has_champion_resolution": len(champion_resolution_paths) > 0,
        "paths": {
            "support_gate": support_gate_paths,
            "champion_support": champion_support_paths,
            "champion_resolution": champion_resolution_paths,
            "missing_payload_fields": missing_payload_fields_paths,
            "payload_has_support_gate": payload_has_support_gate_paths,
            "payload_has_champion_support": payload_has_champion_support_paths,
            "payload_has_champion_resolution": payload_has_champion_resolution_paths,
            "export_trigger": _find_key_paths(entry, "export_trigger"),
            "debug_export_on_quit": _find_key_paths(entry, "debug_export_on_quit"),
            "gameplay_change_allowed": _find_key_paths(entry, "gameplay_change_allowed"),
        },
        "export_trigger": str(entry.get("export_trigger", "")),
        "debug_export_on_quit": bool(entry.get("debug_export_on_quit", False)),
        "gameplay_change_allowed": bool(entry.get("gameplay_change_allowed", False)),
        "missing_payload_fields": _as_list_of_strings(entry.get("missing_payload_fields")),
        "payload_has_support_gate": entry.get("payload_has_support_gate"),
        "payload_has_champion_support": entry.get("payload_has_champion_support"),
        "payload_has_champion_resolution": entry.get("payload_has_champion_resolution"),
    }


def _print_entry_report(entry_report: dict[str, Any]) -> None:
    print("- label: %s" % str(entry_report.get("label", "unknown")))
    print("- path: %s" % str(entry_report.get("path", "")))
    print("- entries_read: %d" % int(entry_report.get("entries_read", 0)))
    print("- invalid_json_lines: %d" % int(entry_report.get("invalid_json_lines", 0)))
    print("- top_level_keys_count: %d" % int(entry_report.get("top_level_keys_count", 0)))
    top_level_keys = entry_report.get("top_level_keys", [])
    if isinstance(top_level_keys, list) and top_level_keys:
        print("- top_level_keys: %s" % ", ".join(str(key) for key in top_level_keys))
    else:
        print("- top_level_keys: none")
    print("- has_support_gate: %s" % ("yes" if bool(entry_report.get("has_support_gate")) else "no"))
    print("- has_champion_support: %s" % ("yes" if bool(entry_report.get("has_champion_support")) else "no"))
    print("- has_champion_resolution: %s" % ("yes" if bool(entry_report.get("has_champion_resolution")) else "no"))
    print("- export_trigger: %s" % str(entry_report.get("export_trigger", "")))
    print("- debug_export_on_quit: %s" % str(entry_report.get("debug_export_on_quit", False)).lower())
    print(
        "- gameplay_change_allowed: %s"
        % str(entry_report.get("gameplay_change_allowed", False)).lower()
    )
    missing_payload_fields = entry_report.get("missing_payload_fields", [])
    if isinstance(missing_payload_fields, list) and missing_payload_fields:
        print("- missing_payload_fields: %s" % ", ".join(str(value) for value in missing_payload_fields))
    else:
        print("- missing_payload_fields: none")
    print("- payload_has_support_gate: %s" % str(entry_report.get("payload_has_support_gate")))
    print("- payload_has_champion_support: %s" % str(entry_report.get("payload_has_champion_support")))
    print("- payload_has_champion_resolution: %s" % str(entry_report.get("payload_has_champion_resolution")))
    paths_block = entry_report.get("paths", {})
    if not isinstance(paths_block, dict):
        paths_block = {}
    print("- field_paths.support_gate: %s" % _format_paths(paths_block.get("support_gate", [])))
    print("- field_paths.champion_support: %s" % _format_paths(paths_block.get("champion_support", [])))
    print(
        "- field_paths.champion_resolution: %s"
        % _format_paths(paths_block.get("champion_resolution", []))
    )
    print(
        "- field_paths.export_trigger: %s"
        % _format_paths(paths_block.get("export_trigger", []))
    )
    print(
        "- field_paths.debug_export_on_quit: %s"
        % _format_paths(paths_block.get("debug_export_on_quit", []))
    )
    print(
        "- field_paths.gameplay_change_allowed: %s"
        % _format_paths(paths_block.get("gameplay_change_allowed", []))
    )
    print(
        "- field_paths.missing_payload_fields: %s"
        % _format_paths(paths_block.get("missing_payload_fields", []))
    )
    print(
        "- field_paths.payload_has_support_gate: %s"
        % _format_paths(paths_block.get("payload_has_support_gate", []))
    )
    print(
        "- field_paths.payload_has_champion_support: %s"
        % _format_paths(paths_block.get("payload_has_champion_support", []))
    )
    print(
        "- field_paths.payload_has_champion_resolution: %s"
        % _format_paths(paths_block.get("payload_has_champion_resolution", []))
    )


def main() -> int:
    args = _build_parser().parse_args()
    try:
        baseline_report = _inspect_latest_entry("baseline", args.baseline)
        current_report = _inspect_latest_entry("current", args.current)
    except RuntimeError as exc:
        print("ERROR: %s" % str(exc))
        return 1 if args.check else 0

    payload = {
        "baseline": baseline_report,
        "current": current_report,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("Support metrics runtime entry inspection")
        _print_entry_report(baseline_report)
        _print_entry_report(current_report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
