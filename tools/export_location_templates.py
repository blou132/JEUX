from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


VALID_KINDS = ("camp", "ruins", "rift_gate")
VALID_FACTION_AFFINITIES = ("human", "monster", "neutral")
VALID_UPGRADE_TARGETS = ("", "human_outpost", "monster_lair")
REQUIRED_TEMPLATE_FIELDS = (
    "id",
    "label",
    "kind",
    "faction_affinity",
    "influence_radius",
    "alert_radius",
    "can_upgrade_to",
    "tags",
)
EXPECTED_TEMPLATE_IDS = ("camp", "ruins", "rift_gate")

DEFAULT_TEMPLATES = [
    {
        "id": "camp",
        "label": "Camp",
        "kind": "camp",
        "faction_affinity": "human",
        "influence_radius": 8.0,
        "alert_radius": 13.0,
        "can_upgrade_to": "human_outpost",
        "tags": ["poi", "anchor", "human", "upgrade_human_outpost"],
    },
    {
        "id": "ruins",
        "label": "Ruins",
        "kind": "ruins",
        "faction_affinity": "monster",
        "influence_radius": 8.0,
        "alert_radius": 13.0,
        "can_upgrade_to": "monster_lair",
        "tags": ["poi", "anchor", "monster", "upgrade_monster_lair"],
    },
    {
        "id": "rift_gate",
        "label": "Rift Gate",
        "kind": "rift_gate",
        "faction_affinity": "neutral",
        "influence_radius": 7.2,
        "alert_radius": 16.5,
        "can_upgrade_to": "",
        "tags": ["poi", "neutral", "gate", "volatile"],
    },
]


def _payload_template() -> dict[str, Any]:
    return {
        "version": 1,
        "schema": "location_templates_v1",
        "locations": DEFAULT_TEMPLATES,
    }


def validate_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    locations = payload.get("locations")
    if not isinstance(locations, list):
        return ["payload.locations must be a list"]

    seen_ids: set[str] = set()
    seen_kinds: set[str] = set()
    for index, template in enumerate(locations):
        ctx = f"locations[{index}]"
        if not isinstance(template, dict):
            errors.append(f"{ctx} must be an object")
            continue

        for field in REQUIRED_TEMPLATE_FIELDS:
            if field not in template:
                errors.append(f"{ctx}.{field} is required")

        template_id = template.get("id")
        if isinstance(template_id, str) and template_id:
            if template_id in seen_ids:
                errors.append(f"duplicate location template id: {template_id}")
            seen_ids.add(template_id)
        else:
            errors.append(f"{ctx}.id must be a non-empty string")

        label = template.get("label")
        if not isinstance(label, str) or not label.strip():
            errors.append(f"{ctx}.label must be a non-empty string")

        kind = template.get("kind")
        if not isinstance(kind, str) or kind not in VALID_KINDS:
            errors.append(f"{ctx}.kind must be one of: {', '.join(VALID_KINDS)}")
        else:
            seen_kinds.add(kind)

        faction_affinity = template.get("faction_affinity")
        if not isinstance(faction_affinity, str) or faction_affinity not in VALID_FACTION_AFFINITIES:
            errors.append(
                f"{ctx}.faction_affinity must be one of: {', '.join(VALID_FACTION_AFFINITIES)}"
            )

        for numeric_field in ("influence_radius", "alert_radius"):
            numeric_value = template.get(numeric_field)
            if not isinstance(numeric_value, (int, float)):
                errors.append(f"{ctx}.{numeric_field} must be numeric")
                continue
            if float(numeric_value) <= 0.0:
                errors.append(f"{ctx}.{numeric_field} must be > 0")

        can_upgrade_to = template.get("can_upgrade_to")
        if not isinstance(can_upgrade_to, str):
            errors.append(f"{ctx}.can_upgrade_to must be a string")
        elif can_upgrade_to not in VALID_UPGRADE_TARGETS:
            errors.append(f"{ctx}.can_upgrade_to must be one of: {', '.join(VALID_UPGRADE_TARGETS)}")

        tags = template.get("tags")
        if not isinstance(tags, list):
            errors.append(f"{ctx}.tags must be a list")
        else:
            for tag in tags:
                if not isinstance(tag, str) or not tag:
                    errors.append(f"{ctx}.tags values must be non-empty strings")

    expected_ids = set(EXPECTED_TEMPLATE_IDS)
    missing_ids = sorted(expected_ids - seen_ids)
    unexpected_ids = sorted(seen_ids - expected_ids)
    if missing_ids:
        errors.append(f"missing required location template ids: {', '.join(missing_ids)}")
    if unexpected_ids:
        errors.append(f"unexpected location template ids: {', '.join(unexpected_ids)}")

    missing_kinds = sorted(set(VALID_KINDS) - seen_kinds)
    if missing_kinds:
        errors.append(f"missing required kinds: {', '.join(missing_kinds)}")

    camp = next((entry for entry in locations if isinstance(entry, dict) and entry.get("id") == "camp"), {})
    ruins = next((entry for entry in locations if isinstance(entry, dict) and entry.get("id") == "ruins"), {})
    rift_gate = next((entry for entry in locations if isinstance(entry, dict) and entry.get("id") == "rift_gate"), {})
    if isinstance(camp, dict) and camp and camp.get("can_upgrade_to") != "human_outpost":
        errors.append("locations[camp].can_upgrade_to must be human_outpost")
    if isinstance(ruins, dict) and ruins and ruins.get("can_upgrade_to") != "monster_lair":
        errors.append("locations[ruins].can_upgrade_to must be monster_lair")
    if isinstance(rift_gate, dict) and rift_gate and rift_gate.get("can_upgrade_to") != "":
        errors.append("locations[rift_gate].can_upgrade_to must be empty")

    return errors


def write_default_templates(output_path: Path) -> None:
    payload = _payload_template()
    errors = validate_payload(payload)
    if errors:
        raise ValueError("Invalid default location templates: " + "; ".join(errors))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_payload(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export and validate location templates JSON.")
    parser.add_argument(
        "--path",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "shared_data" / "locations.json",
        help="Path to locations JSON file.",
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
        write_default_templates(path)
        payload = load_payload(path)

    errors = validate_payload(payload)
    if errors:
        print(f"ERROR: validation failed for {path}")
        for err in errors:
            print(f"- {err}")
        return 1

    templates_count = len(payload.get("locations", []))
    action = "validated" if args.validate_only else "written+validated"
    print(f"OK: {action} {templates_count} location templates at {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
