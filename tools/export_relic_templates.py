from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


VALID_RARITIES = ("common", "uncommon", "rare", "epic")
VALID_FACTIONS = ("human", "monster")
REQUIRED_TEMPLATE_FIELDS = (
    "id",
    "label",
    "kind",
    "rarity",
    "modifiers",
    "eligible_profiles",
    "tags",
)
REQUIRED_ELIGIBILITY_FIELDS = (
    "required_world_event_id",
    "required_structure_state",
    "faction",
    "prefer_special_arrival",
    "require_magic",
)
EXPECTED_TEMPLATE_IDS = ("arcane_sigil", "oath_standard")

DEFAULT_TEMPLATES = [
    {
        "id": "arcane_sigil",
        "label": "Arcane Sigil",
        "kind": "arcane_focus",
        "rarity": "rare",
        "modifiers": {
            "magic_damage_mult": 1.10,
            "magic_energy_cost_mult": 0.90,
        },
        "eligible_profiles": {
            "required_world_event_id": "mana_surge",
            "required_structure_state": "human_outpost",
            "faction": "human",
            "prefer_special_arrival": True,
            "require_magic": True,
        },
        "tags": ["relic", "arcane", "caster", "human"],
    },
    {
        "id": "oath_standard",
        "label": "Oath Standard",
        "kind": "war_banner",
        "rarity": "rare",
        "modifiers": {
            "melee_damage_mult": 1.08,
            "energy_regen_per_sec_bonus": 0.22,
        },
        "eligible_profiles": {
            "required_world_event_id": "monster_frenzy",
            "required_structure_state": "monster_lair",
            "faction": "monster",
            "prefer_special_arrival": True,
            "require_magic": False,
        },
        "tags": ["relic", "war", "banner", "monster"],
    },
]


def _payload_template() -> dict[str, Any]:
    return {
        "version": 1,
        "schema": "relic_templates_v1",
        "relics": DEFAULT_TEMPLATES,
    }


def _validate_modifiers(errors: list[str], ctx: str, modifiers: Any) -> None:
    if not isinstance(modifiers, dict) or not modifiers:
        errors.append(f"{ctx}.modifiers must be a non-empty object")
        return

    for key, value in modifiers.items():
        if not isinstance(key, str) or not key:
            errors.append(f"{ctx}.modifiers keys must be non-empty strings")
            continue
        if not isinstance(value, (int, float)):
            errors.append(f"{ctx}.modifiers.{key} must be numeric")
            continue
        as_float = float(value)
        if key.endswith("_mult") and as_float <= 0.0:
            errors.append(f"{ctx}.modifiers.{key} must be > 0")
        if key.endswith("_bonus") and as_float < 0.0:
            errors.append(f"{ctx}.modifiers.{key} must be >= 0")


def _validate_eligibility(errors: list[str], ctx: str, eligibility: Any) -> None:
    if not isinstance(eligibility, dict):
        errors.append(f"{ctx}.eligible_profiles must be an object")
        return

    for field in REQUIRED_ELIGIBILITY_FIELDS:
        if field not in eligibility:
            errors.append(f"{ctx}.eligible_profiles.{field} is required")

    world_event_id = eligibility.get("required_world_event_id")
    if not isinstance(world_event_id, str) or not world_event_id:
        errors.append(f"{ctx}.eligible_profiles.required_world_event_id must be a non-empty string")

    structure_state = eligibility.get("required_structure_state")
    if not isinstance(structure_state, str) or not structure_state:
        errors.append(f"{ctx}.eligible_profiles.required_structure_state must be a non-empty string")

    faction = eligibility.get("faction")
    if not isinstance(faction, str) or faction not in VALID_FACTIONS:
        errors.append(f"{ctx}.eligible_profiles.faction must be one of: {', '.join(VALID_FACTIONS)}")

    for bool_field in ("prefer_special_arrival", "require_magic"):
        if not isinstance(eligibility.get(bool_field), bool):
            errors.append(f"{ctx}.eligible_profiles.{bool_field} must be a boolean")


def validate_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    relics = payload.get("relics")
    if not isinstance(relics, list):
        return ["payload.relics must be a list"]

    seen_ids: set[str] = set()
    for index, relic in enumerate(relics):
        ctx = f"relics[{index}]"
        if not isinstance(relic, dict):
            errors.append(f"{ctx} must be an object")
            continue

        for field in REQUIRED_TEMPLATE_FIELDS:
            if field not in relic:
                errors.append(f"{ctx}.{field} is required")

        relic_id = relic.get("id")
        if isinstance(relic_id, str) and relic_id:
            if relic_id in seen_ids:
                errors.append(f"duplicate relic template id: {relic_id}")
            seen_ids.add(relic_id)
        else:
            errors.append(f"{ctx}.id must be a non-empty string")

        label = relic.get("label")
        if not isinstance(label, str) or not label.strip():
            errors.append(f"{ctx}.label must be a non-empty string")

        kind = relic.get("kind")
        if not isinstance(kind, str) or not kind.strip():
            errors.append(f"{ctx}.kind must be a non-empty string")

        rarity = relic.get("rarity")
        if not isinstance(rarity, str) or rarity not in VALID_RARITIES:
            errors.append(f"{ctx}.rarity must be one of: {', '.join(VALID_RARITIES)}")

        _validate_modifiers(errors, ctx, relic.get("modifiers"))
        _validate_eligibility(errors, ctx, relic.get("eligible_profiles"))

        tags = relic.get("tags")
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
        errors.append(f"missing required relic template ids: {', '.join(missing_ids)}")
    if unexpected_ids:
        errors.append(f"unexpected relic template ids: {', '.join(unexpected_ids)}")

    return errors


def write_default_templates(output_path: Path) -> None:
    payload = _payload_template()
    errors = validate_payload(payload)
    if errors:
        raise ValueError("Invalid default relic templates: " + "; ".join(errors))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_payload(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export and validate relic templates JSON.")
    parser.add_argument(
        "--path",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "shared_data" / "relics.json",
        help="Path to relics JSON file.",
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

    templates_count = len(payload.get("relics", []))
    action = "validated" if args.validate_only else "written+validated"
    print(f"OK: {action} {templates_count} relic templates at {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
