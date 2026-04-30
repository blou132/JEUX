from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


VALID_KINDS = ("human", "monster")
VALID_DOCTRINES = ("warlike", "steadfast", "arcane")
VALID_PROJECT_BIASES = ("fortify", "warband_muster", "ritual_focus")
REQUIRED_TEMPLATE_FIELDS = (
    "id",
    "label",
    "kind",
    "default_doctrine_pool",
    "tags",
)
EXPECTED_TEMPLATE_IDS = ("human_core", "monster_core")

DEFAULT_TEMPLATES = [
    {
        "id": "human_core",
        "label": "Human Coalition",
        "kind": "human",
        "default_doctrine_pool": ["steadfast", "arcane"],
        "project_bias": "fortify",
        "raid_bias": 0.0,
        "defense_bias": 0.0,
        "rally_bias": 0.0,
        "tags": ["human", "baseline", "outpost"],
    },
    {
        "id": "monster_core",
        "label": "Monster Horde",
        "kind": "monster",
        "default_doctrine_pool": ["warlike", "arcane"],
        "project_bias": "warband_muster",
        "raid_bias": 0.0,
        "defense_bias": 0.0,
        "rally_bias": 0.0,
        "tags": ["monster", "baseline", "lair"],
    },
]


def _payload_template() -> dict[str, Any]:
    return {
        "version": 1,
        "schema": "faction_templates_v1",
        "factions": DEFAULT_TEMPLATES,
    }


def _validate_optional_bias(errors: list[str], ctx: str, template: dict[str, Any], field: str) -> None:
    value = template.get(field, 0.0)
    if not isinstance(value, (int, float)):
        errors.append(f"{ctx}.{field} must be numeric")
        return
    if float(value) < -0.25 or float(value) > 0.25:
        errors.append(f"{ctx}.{field} must be between -0.25 and 0.25")


def validate_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    factions = payload.get("factions")
    if not isinstance(factions, list):
        return ["payload.factions must be a list"]

    seen_ids: set[str] = set()
    seen_kinds: set[str] = set()
    for index, template in enumerate(factions):
        ctx = f"factions[{index}]"
        if not isinstance(template, dict):
            errors.append(f"{ctx} must be an object")
            continue

        for field in REQUIRED_TEMPLATE_FIELDS:
            if field not in template:
                errors.append(f"{ctx}.{field} is required")

        template_id = template.get("id")
        if isinstance(template_id, str) and template_id:
            if template_id in seen_ids:
                errors.append(f"duplicate faction template id: {template_id}")
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

        doctrine_pool = template.get("default_doctrine_pool")
        if not isinstance(doctrine_pool, list) or not doctrine_pool:
            errors.append(f"{ctx}.default_doctrine_pool must be a non-empty list")
        else:
            for doctrine in doctrine_pool:
                if not isinstance(doctrine, str) or doctrine not in VALID_DOCTRINES:
                    errors.append(
                        f"{ctx}.default_doctrine_pool entries must be one of: {', '.join(VALID_DOCTRINES)}"
                    )

        project_bias = template.get("project_bias", "")
        if project_bias != "":
            if not isinstance(project_bias, str) or project_bias not in VALID_PROJECT_BIASES:
                errors.append(f"{ctx}.project_bias must be one of: {', '.join(VALID_PROJECT_BIASES)}")

        _validate_optional_bias(errors, ctx, template, "raid_bias")
        _validate_optional_bias(errors, ctx, template, "defense_bias")
        _validate_optional_bias(errors, ctx, template, "rally_bias")

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
        errors.append(f"missing required faction template ids: {', '.join(missing_ids)}")
    if unexpected_ids:
        errors.append(f"unexpected faction template ids: {', '.join(unexpected_ids)}")

    missing_kinds = sorted(set(VALID_KINDS) - seen_kinds)
    if missing_kinds:
        errors.append(f"missing required kinds: {', '.join(missing_kinds)}")

    return errors


def write_default_templates(output_path: Path) -> None:
    payload = _payload_template()
    errors = validate_payload(payload)
    if errors:
        raise ValueError("Invalid default faction templates: " + "; ".join(errors))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_payload(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export and validate faction templates JSON.")
    parser.add_argument(
        "--path",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "shared_data" / "factions.json",
        help="Path to factions JSON file.",
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

    templates_count = len(payload.get("factions", []))
    action = "validated" if args.validate_only else "written+validated"
    print(f"OK: {action} {templates_count} faction templates at {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
