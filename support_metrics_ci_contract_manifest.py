from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MANIFEST_RELATIVE_PATH = (
    Path("tests") / "fixtures" / "support_metrics_ci_contract_manifest.json"
)
REQUIRED_MANIFEST_KEYS: tuple[str, ...] = (
    "tools",
    "artifacts",
    "fragment_categories",
    "workflow_steps",
    "expected_invariants",
    "report_modes",
)


@dataclass
class SupportMetricsContractManifestLoadResult:
    path: Path
    manifest: dict[str, Any] | None
    issues: list[str]

    @property
    def is_valid(self) -> bool:
        return len(self.issues) == 0 and self.manifest is not None


def _validate_string_list(manifest: dict[str, Any], key: str) -> list[str]:
    issues: list[str] = []
    value = manifest.get(key)
    if not isinstance(value, list):
        return ["manifest key must be a list: %s" % key]
    if len(value) == 0:
        return ["manifest key list is empty: %s" % key]

    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str):
            issues.append("manifest key list contains non-string item: %s" % key)
            continue
        normalized = item.strip()
        if normalized == "":
            issues.append("manifest key list contains empty string item: %s" % key)
            continue
        if normalized in seen:
            issues.append("manifest key list contains duplicate item: %s -> %s" % (key, normalized))
            continue
        seen.add(normalized)
    return issues


def validate_support_metrics_contract_manifest(manifest: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for key in REQUIRED_MANIFEST_KEYS:
        if key not in manifest:
            issues.append("manifest missing required key: %s" % key)
    if issues:
        return issues

    for key in REQUIRED_MANIFEST_KEYS:
        issues.extend(_validate_string_list(manifest, key))
    return issues


def load_support_metrics_contract_manifest(
    root: Path | None = None,
) -> SupportMetricsContractManifestLoadResult:
    repo_root = root if root is not None else Path(__file__).resolve().parent
    manifest_path = repo_root / MANIFEST_RELATIVE_PATH
    issues: list[str] = []

    if not manifest_path.exists():
        return SupportMetricsContractManifestLoadResult(
            path=manifest_path,
            manifest=None,
            issues=["manifest file is missing: %s" % str(MANIFEST_RELATIVE_PATH)],
        )

    try:
        parsed = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return SupportMetricsContractManifestLoadResult(
            path=manifest_path,
            manifest=None,
            issues=["manifest is unreadable or invalid JSON: %s" % str(exc)],
        )

    if not isinstance(parsed, dict):
        return SupportMetricsContractManifestLoadResult(
            path=manifest_path,
            manifest=None,
            issues=["manifest root must be an object"],
        )

    issues.extend(validate_support_metrics_contract_manifest(parsed))
    return SupportMetricsContractManifestLoadResult(
        path=manifest_path,
        manifest=parsed,
        issues=issues,
    )
