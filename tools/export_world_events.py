from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_EVENT_FIELDS = (
    "id",
    "label",
    "duration",
    "cooldown_min",
    "cooldown_max",
    "modifiers",
    "tags",
)

EXPECTED_EVENT_IDS = (
    "mana_surge",
    "monster_frenzy",
    "sanctuary_calm",
)

DEFAULT_EVENTS = [
    {
        "id": "mana_surge",
        "label": "Mana Surge",
        "duration": 18.0,
        "cooldown_min": 28.0,
        "cooldown_max": 52.0,
        "modifiers": {
            "magic_damage_mult": 1.18,
            "magic_energy_cost_mult": 0.86,
            "raid_pressure_global_mult": 1.03,
        },
        "tags": ["arcane", "surge", "offense"],
    },
    {
        "id": "monster_frenzy",
        "label": "Monster Frenzy",
        "duration": 16.0,
        "cooldown_min": 28.0,
        "cooldown_max": 52.0,
        "modifiers": {
            "monster_melee_damage_mult": 1.14,
            "monster_speed_mult": 1.08,
            "raid_pressure_monster_mult": 1.16,
        },
        "tags": ["monster", "frenzy", "pressure"],
    },
    {
        "id": "sanctuary_calm",
        "label": "Sanctuary Calm",
        "duration": 20.0,
        "cooldown_min": 28.0,
        "cooldown_max": 52.0,
        "modifiers": {
            "human_energy_regen_per_sec": 0.55,
            "raid_pressure_global_mult": 0.90,
            "raid_pressure_monster_mult": 0.78,
        },
        "tags": ["sanctuary", "calm", "recovery"],
    },
]


def _payload_template() -> dict[str, Any]:
    return {
        "version": 1,
        "schema": "world_events_v1",
        "events": DEFAULT_EVENTS,
    }


def _validate_numeric_field(errors: list[str], ctx: str, field: str, value: Any, minimum: float) -> None:
    if not isinstance(value, (int, float)):
        errors.append(f"{ctx}.{field} must be a number")
        return
    if float(value) < minimum:
        errors.append(f"{ctx}.{field} must be >= {minimum}")


def validate_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    events = payload.get("events")
    if not isinstance(events, list):
        return ["payload.events must be a list"]

    seen_ids: set[str] = set()
    for index, event in enumerate(events):
        ctx = f"events[{index}]"
        if not isinstance(event, dict):
            errors.append(f"{ctx} must be an object")
            continue

        for field in REQUIRED_EVENT_FIELDS:
            if field not in event:
                errors.append(f"{ctx}.{field} is required")

        event_id = event.get("id")
        if isinstance(event_id, str) and event_id:
            if event_id in seen_ids:
                errors.append(f"duplicate event id: {event_id}")
            seen_ids.add(event_id)
        else:
            errors.append(f"{ctx}.id must be a non-empty string")

        if not isinstance(event.get("label"), str) or not str(event.get("label")).strip():
            errors.append(f"{ctx}.label must be a non-empty string")

        _validate_numeric_field(errors, ctx, "duration", event.get("duration"), 1.0)
        _validate_numeric_field(errors, ctx, "cooldown_min", event.get("cooldown_min"), 0.0)
        _validate_numeric_field(errors, ctx, "cooldown_max", event.get("cooldown_max"), 0.0)

        cooldown_min = event.get("cooldown_min")
        cooldown_max = event.get("cooldown_max")
        if isinstance(cooldown_min, (int, float)) and isinstance(cooldown_max, (int, float)):
            if float(cooldown_max) < float(cooldown_min):
                errors.append(f"{ctx}.cooldown_max must be >= cooldown_min")

        modifiers = event.get("modifiers")
        if not isinstance(modifiers, dict) or not modifiers:
            errors.append(f"{ctx}.modifiers must be a non-empty object")
        else:
            for key, value in modifiers.items():
                if not isinstance(key, str) or not key:
                    errors.append(f"{ctx}.modifiers keys must be non-empty strings")
                if not isinstance(value, (int, float)):
                    errors.append(f"{ctx}.modifiers.{key} must be numeric")

        tags = event.get("tags")
        if not isinstance(tags, list):
            errors.append(f"{ctx}.tags must be a list")
        else:
            for tag in tags:
                if not isinstance(tag, str) or not tag:
                    errors.append(f"{ctx}.tags values must be non-empty strings")

    expected_ids = set(EXPECTED_EVENT_IDS)
    missing_ids = sorted(expected_ids - seen_ids)
    unexpected_ids = sorted(seen_ids - expected_ids)
    if missing_ids:
        errors.append(f"missing required event ids: {', '.join(missing_ids)}")
    if unexpected_ids:
        errors.append(f"unexpected event ids: {', '.join(unexpected_ids)}")

    return errors


def write_default_events(output_path: Path) -> None:
    payload = _payload_template()
    errors = validate_payload(payload)
    if errors:
        raise ValueError("Invalid default world events: " + "; ".join(errors))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_payload(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export and validate world events JSON.")
    parser.add_argument(
        "--path",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "shared_data" / "events.json",
        help="Path to world events JSON file.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate the existing file, do not overwrite it.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    path: Path = args.path

    if args.validate_only:
        if not path.exists():
            print(f"ERROR: file not found: {path}")
            return 1
        payload = load_payload(path)
    else:
        write_default_events(path)
        payload = load_payload(path)

    errors = validate_payload(payload)
    if errors:
        print(f"ERROR: validation failed for {path}")
        for err in errors:
            print(f"- {err}")
        return 1

    events_count = len(payload.get("events", []))
    action = "validated" if args.validate_only else "written+validated"
    print(f"OK: {action} {events_count} world events at {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
