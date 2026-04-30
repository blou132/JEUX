from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


VALID_KINDS = ("offense", "defense", "arcane")
EXPECTED_TEMPLATE_IDS = ("warlike", "steadfast", "arcane")
REQUIRED_TEMPLATE_FIELDS = (
    "id",
    "label",
    "kind",
    "raid_bias",
    "defense_bias",
    "rally_bias",
    "magic_bias",
    "tags",
)

DEFAULT_TEMPLATES = [
    {
        "id": "warlike",
        "label": "Warlike Doctrine",
        "kind": "offense",
        "raid_bias": 0.11,
        "defense_bias": -0.05,
        "rally_bias": -0.05,
        "magic_bias": 0.00,
        "tags": ["doctrine", "offense", "warband"],
    },
    {
        "id": "steadfast",
        "label": "Steadfast Doctrine",
        "kind": "defense",
        "raid_bias": -0.08,
        "defense_bias": 0.12,
        "rally_bias": 0.08,
        "magic_bias": 0.00,
        "tags": ["doctrine", "defense", "fortify"],
    },
    {
        "id": "arcane",
        "label": "Arcane Doctrine",
        "kind": "arcane",
        "raid_bias": 0.02,
        "defense_bias": 0.04,
        "rally_bias": 0.03,
        "magic_bias": 0.06,
        "tags": ["doctrine", "arcane", "ritual"],
    },
]


def _payload_template() -> dict[str, Any]:
    return {
        "version": 1,
        "schema": "doctrine_templates_v1",
        "doctrines": DEFAULT_TEMPLATES,
    }


def _validate_bias(errors: list[str], ctx: str, template: dict[str, Any], field: str, low: float, high: float) -> None:
    value = template.get(field)
    if not isinstance(value, (int, float)):
        errors.append(f"{ctx}.{field} must be numeric")
        return
    as_float = float(value)
    if as_float < low or as_float > high:
        errors.append(f"{ctx}.{field} must be between {low:.2f} and {high:.2f}")


def validate_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    doctrines = payload.get("doctrines")
    if not isinstance(doctrines, list):
        return ["payload.doctrines must be a list"]

    seen_ids: set[str] = set()
    for index, template in enumerate(doctrines):
        ctx = f"doctrines[{index}]"
        if not isinstance(template, dict):
            errors.append(f"{ctx} must be an object")
            continue

        for field in REQUIRED_TEMPLATE_FIELDS:
            if field not in template:
                errors.append(f"{ctx}.{field} is required")

        template_id = template.get("id")
        if isinstance(template_id, str) and template_id:
            if template_id in seen_ids:
                errors.append(f"duplicate doctrine template id: {template_id}")
            seen_ids.add(template_id)
        else:
            errors.append(f"{ctx}.id must be a non-empty string")

        label = template.get("label")
        if not isinstance(label, str) or not label.strip():
            errors.append(f"{ctx}.label must be a non-empty string")

        kind = template.get("kind")
        if not isinstance(kind, str) or kind not in VALID_KINDS:
            errors.append(f"{ctx}.kind must be one of: {', '.join(VALID_KINDS)}")

        _validate_bias(errors, ctx, template, "raid_bias", -0.25, 0.25)
        _validate_bias(errors, ctx, template, "defense_bias", -0.25, 0.25)
        _validate_bias(errors, ctx, template, "rally_bias", -0.25, 0.25)
        _validate_bias(errors, ctx, template, "magic_bias", -0.12, 0.12)

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
        errors.append(f"missing required doctrine template ids: {', '.join(missing_ids)}")
    if unexpected_ids:
        errors.append(f"unexpected doctrine template ids: {', '.join(unexpected_ids)}")

    return errors


def write_default_templates(output_path: Path) -> None:
    payload = _payload_template()
    errors = validate_payload(payload)
    if errors:
        raise ValueError("Invalid default doctrine templates: " + "; ".join(errors))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_payload(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export and validate doctrine templates JSON.")
    parser.add_argument(
        "--path",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "shared_data" / "doctrines.json",
        help="Path to doctrines JSON file.",
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

    templates_count = len(payload.get("doctrines", []))
    action = "validated" if args.validate_only else "written+validated"
    print(f"OK: {action} {templates_count} doctrine templates at {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
