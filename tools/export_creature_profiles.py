from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_PROFILE_FIELDS = (
    "id",
    "kind",
    "hp",
    "speed",
    "melee_damage",
    "magic_damage",
    "magic_range",
    "role",
    "tags",
)

EXPECTED_PROFILE_IDS = (
    "human_fighter",
    "human_mage",
    "human_scout",
    "monster_standard",
    "monster_brute",
    "monster_ranged",
)

DEFAULT_PROFILES = [
    {
        "id": "human_fighter",
        "kind": "human",
        "role": "fighter",
        "hp": 144.0,
        "speed": 4.7,
        "melee_damage": 16.0,
        "magic_damage": 10.0,
        "magic_range": 12.2,
        "tags": ["human", "frontline", "melee"],
    },
    {
        "id": "human_mage",
        "kind": "human",
        "role": "mage",
        "hp": 122.0,
        "speed": 4.8,
        "melee_damage": 11.0,
        "magic_damage": 13.0,
        "magic_range": 14.6,
        "tags": ["human", "caster", "control"],
    },
    {
        "id": "human_scout",
        "kind": "human",
        "role": "scout",
        "hp": 128.0,
        "speed": 5.3,
        "melee_damage": 12.0,
        "magic_damage": 10.5,
        "magic_range": 13.6,
        "tags": ["human", "skirmisher", "mobile"],
    },
    {
        "id": "monster_standard",
        "kind": "monster",
        "role": "standard",
        "hp": 142.0,
        "speed": 4.4,
        "melee_damage": 16.0,
        "magic_damage": 0.0,
        "magic_range": 0.0,
        "tags": ["monster", "melee"],
    },
    {
        "id": "monster_brute",
        "kind": "monster",
        "role": "brute",
        "hp": 198.0,
        "speed": 3.7,
        "melee_damage": 22.0,
        "magic_damage": 0.0,
        "magic_range": 0.0,
        "tags": ["monster", "brute", "tank"],
    },
    {
        "id": "monster_ranged",
        "kind": "monster",
        "role": "ranged",
        "hp": 114.0,
        "speed": 4.8,
        "melee_damage": 8.0,
        "magic_damage": 10.0,
        "magic_range": 16.0,
        "tags": ["monster", "ranged", "caster"],
    },
]


def _payload_template() -> dict[str, Any]:
    return {
        "version": 1,
        "schema": "creature_profiles_v1",
        "profiles": DEFAULT_PROFILES,
    }


def validate_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    profiles = payload.get("profiles")
    if not isinstance(profiles, list):
        return ["payload.profiles must be a list"]

    seen_ids: set[str] = set()
    for index, profile in enumerate(profiles):
        ctx = f"profiles[{index}]"
        if not isinstance(profile, dict):
            errors.append(f"{ctx} must be an object")
            continue

        for field in REQUIRED_PROFILE_FIELDS:
            if field not in profile:
                errors.append(f"{ctx}.{field} is required")

        profile_id = profile.get("id")
        if isinstance(profile_id, str) and profile_id:
            if profile_id in seen_ids:
                errors.append(f"duplicate profile id: {profile_id}")
            seen_ids.add(profile_id)
        else:
            errors.append(f"{ctx}.id must be a non-empty string")

        if not isinstance(profile.get("kind"), str):
            errors.append(f"{ctx}.kind must be a string")
        if not isinstance(profile.get("role"), str):
            errors.append(f"{ctx}.role must be a string")
        if not isinstance(profile.get("tags"), list):
            errors.append(f"{ctx}.tags must be a list")
        else:
            for tag in profile["tags"]:
                if not isinstance(tag, str) or not tag:
                    errors.append(f"{ctx}.tags values must be non-empty strings")

        for field in ("hp", "speed", "melee_damage", "magic_damage", "magic_range"):
            value = profile.get(field)
            if not isinstance(value, (int, float)):
                errors.append(f"{ctx}.{field} must be a number")
            elif float(value) < 0.0:
                errors.append(f"{ctx}.{field} must be >= 0")

    expected_ids = set(EXPECTED_PROFILE_IDS)
    missing_ids = sorted(expected_ids - seen_ids)
    unexpected_ids = sorted(seen_ids - expected_ids)
    if missing_ids:
        errors.append(f"missing required profile ids: {', '.join(missing_ids)}")
    if unexpected_ids:
        errors.append(f"unexpected profile ids: {', '.join(unexpected_ids)}")

    return errors


def write_default_profiles(output_path: Path) -> None:
    payload = _payload_template()
    errors = validate_payload(payload)
    if errors:
        raise ValueError("Invalid default profiles: " + "; ".join(errors))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_payload(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export and validate creature profiles JSON.")
    parser.add_argument(
        "--path",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "shared_data" / "creatures.json",
        help="Path to creatures JSON file.",
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
        write_default_profiles(path)
        payload = load_payload(path)

    errors = validate_payload(payload)
    if errors:
        print(f"ERROR: validation failed for {path}")
        for err in errors:
            print(f"- {err}")
        return 1

    profiles_count = len(payload.get("profiles", []))
    action = "validated" if args.validate_only else "written+validated"
    print(f"OK: {action} {profiles_count} creature profiles at {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
