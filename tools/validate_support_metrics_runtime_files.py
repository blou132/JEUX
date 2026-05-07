from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence


STATE_OK = "ok"
STATE_WARNING = "warning"
STATE_ERROR = "error"
STATE_RANK: dict[str, int] = {STATE_OK: 0, STATE_WARNING: 1, STATE_ERROR: 2}

DEFAULT_BASELINE_PATH = Path("outputs/ci/support_metrics_baseline.jsonl")
DEFAULT_CURRENT_PATH = Path("outputs/ci/support_metrics_current.jsonl")

USEFUL_OPTIONAL_FIELDS: tuple[str, ...] = (
    "support_gate",
    "champion_support",
    "support_metrics_quality",
    "support_metrics_final_decision",
    "support_metrics_report_provenance",
)

SUPPORT_GATE_RUNTIME_KEYS: tuple[str, ...] = (
    "support_gate_run_attempts",
    "support_gate_run_success",
    "support_gate_run_success_rate",
    "support_gate_run_available_ratio",
)
CHAMPION_RUNTIME_KEYS: tuple[str, ...] = (
    "champion_support_run_attempts",
    "champion_support_run_success",
    "champion_support_run_success_rate",
)


@dataclass
class RuntimeFileValidation:
    label: str
    path: str
    state: str
    exists: bool
    readable: bool
    total_lines: int
    non_empty_lines: int
    valid_json_lines: int
    invalid_json_lines: int
    exploitable_lines: int
    objective_ids: list[str]
    useful_fields_detected: list[str]
    useful_fields_missing: list[str]
    issues: list[str]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RuntimeFilesValidationReport:
    overall: str
    baseline: RuntimeFileValidation
    current: RuntimeFileValidation
    checked_files: int
    issues_count: int
    warnings_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall": self.overall,
            "checked_files": self.checked_files,
            "issues_count": self.issues_count,
            "warnings_count": self.warnings_count,
            "baseline": self.baseline.to_dict(),
            "current": self.current.to_dict(),
        }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate runtime support metrics baseline/current JSONL files before "
            "comparison or report generation."
        )
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=DEFAULT_BASELINE_PATH,
        help="Baseline JSONL file path (default: outputs/ci/support_metrics_baseline.jsonl).",
    )
    parser.add_argument(
        "--current",
        type=Path,
        default=DEFAULT_CURRENT_PATH,
        help="Current JSONL file path (default: outputs/ci/support_metrics_current.jsonl).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Return non-zero when at least one file has blocking validation errors.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed warnings and issues.",
    )
    return parser


def _worst_state(states: Sequence[str]) -> str:
    if not states:
        return STATE_OK
    return max(states, key=lambda value: STATE_RANK.get(value, 0))


def _is_exploitable_record(record: dict[str, Any]) -> bool:
    return len(record) > 0


def _validate_runtime_file(label: str, path: Path) -> RuntimeFileValidation:
    issues: list[str] = []
    warnings: list[str] = []

    exists = path.exists()
    readable = False
    total_lines = 0
    non_empty_lines = 0
    valid_json_lines = 0
    invalid_json_lines = 0
    exploitable_lines = 0
    objective_ids: set[str] = set()
    useful_fields_detected: set[str] = set()
    records: list[dict[str, Any]] = []

    if not exists:
        issues.append("missing file: %s" % path)
        return RuntimeFileValidation(
            label=label,
            path=str(path),
            state=STATE_ERROR,
            exists=False,
            readable=False,
            total_lines=0,
            non_empty_lines=0,
            valid_json_lines=0,
            invalid_json_lines=0,
            exploitable_lines=0,
            objective_ids=[],
            useful_fields_detected=[],
            useful_fields_missing=list(USEFUL_OPTIONAL_FIELDS),
            issues=issues,
            warnings=warnings,
        )

    try:
        content = path.read_text(encoding="utf-8")
        readable = True
    except OSError as exc:
        issues.append("unable to read file: %s" % str(exc))
        return RuntimeFileValidation(
            label=label,
            path=str(path),
            state=STATE_ERROR,
            exists=True,
            readable=False,
            total_lines=0,
            non_empty_lines=0,
            valid_json_lines=0,
            invalid_json_lines=0,
            exploitable_lines=0,
            objective_ids=[],
            useful_fields_detected=[],
            useful_fields_missing=list(USEFUL_OPTIONAL_FIELDS),
            issues=issues,
            warnings=warnings,
        )

    lines = content.splitlines()
    total_lines = len(lines)

    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if line == "":
            continue

        non_empty_lines += 1
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            invalid_json_lines += 1
            issues.append("line %d contains invalid JSON" % line_number)
            continue

        if not isinstance(parsed, dict):
            invalid_json_lines += 1
            issues.append("line %d JSON root must be an object" % line_number)
            continue

        valid_json_lines += 1
        records.append(parsed)

        if _is_exploitable_record(parsed):
            exploitable_lines += 1

        objective_id_raw = parsed.get("objective_id")
        if isinstance(objective_id_raw, str):
            normalized_objective_id = objective_id_raw.strip()
            if normalized_objective_id != "":
                objective_ids.add(normalized_objective_id)

        for field_name in USEFUL_OPTIONAL_FIELDS:
            if field_name in parsed:
                useful_fields_detected.add(field_name)

    if non_empty_lines == 0:
        issues.append("file is empty (no non-empty JSONL lines)")

    if valid_json_lines == 0 and non_empty_lines > 0:
        issues.append("no valid JSON object line found")

    if exploitable_lines == 0 and valid_json_lines > 0:
        issues.append("no exploitable JSON object line found")

    has_support_gate_objective = "support_gate" in objective_ids
    has_rally_champion_objective = "rally_champion" in objective_ids

    if has_support_gate_objective != has_rally_champion_objective:
        warnings.append(
            "partial support objectives coverage (support_gate=%s, rally_champion=%s)"
            % (
                "yes" if has_support_gate_objective else "no",
                "yes" if has_rally_champion_objective else "no",
            )
        )

    if not has_support_gate_objective and not has_rally_champion_objective and exploitable_lines > 0:
        warnings.append("no support objective entries found; file may not target support metrics")

    if has_support_gate_objective:
        support_gate_records = [
            record
            for record in records
            if str(record.get("objective_id", "")).strip() == "support_gate"
        ]
        has_support_gate_runtime_metrics = any(
            any(metric_key in record for metric_key in SUPPORT_GATE_RUNTIME_KEYS)
            for record in support_gate_records
        )
        if not has_support_gate_runtime_metrics:
            warnings.append(
                "support_gate records exist but expected support_gate runtime metrics are missing"
            )

    if has_rally_champion_objective:
        rally_records = [
            record
            for record in records
            if str(record.get("objective_id", "")).strip() == "rally_champion"
        ]
        has_champion_runtime_metrics = any(
            any(metric_key in record for metric_key in CHAMPION_RUNTIME_KEYS)
            for record in rally_records
        )
        if not has_champion_runtime_metrics:
            warnings.append(
                "rally_champion records exist but expected champion_support runtime metrics are missing"
            )

    useful_fields_missing = [
        field_name for field_name in USEFUL_OPTIONAL_FIELDS if field_name not in useful_fields_detected
    ]
    if useful_fields_detected and useful_fields_missing:
        warnings.append(
            "partial optional summary fields: missing %s"
            % ", ".join(useful_fields_missing)
        )

    state = STATE_OK
    if issues:
        state = STATE_ERROR
    elif warnings:
        state = STATE_WARNING

    return RuntimeFileValidation(
        label=label,
        path=str(path),
        state=state,
        exists=exists,
        readable=readable,
        total_lines=total_lines,
        non_empty_lines=non_empty_lines,
        valid_json_lines=valid_json_lines,
        invalid_json_lines=invalid_json_lines,
        exploitable_lines=exploitable_lines,
        objective_ids=sorted(objective_ids),
        useful_fields_detected=sorted(useful_fields_detected),
        useful_fields_missing=useful_fields_missing,
        issues=issues,
        warnings=warnings,
    )


def build_runtime_files_validation_report(
    baseline_path: Path,
    current_path: Path,
) -> RuntimeFilesValidationReport:
    baseline_check = _validate_runtime_file("baseline", baseline_path)
    current_check = _validate_runtime_file("current", current_path)
    overall = _worst_state([baseline_check.state, current_check.state])
    issues_count = len(baseline_check.issues) + len(current_check.issues)
    warnings_count = len(baseline_check.warnings) + len(current_check.warnings)
    return RuntimeFilesValidationReport(
        overall=overall,
        baseline=baseline_check,
        current=current_check,
        checked_files=2,
        issues_count=issues_count,
        warnings_count=warnings_count,
    )


def _print_file_report(file_report: RuntimeFileValidation, verbose: bool) -> None:
    print("- %s: %s" % (file_report.label, file_report.state))
    print("  - path: %s" % file_report.path)
    print("  - exists: %s" % ("yes" if file_report.exists else "no"))
    print("  - readable: %s" % ("yes" if file_report.readable else "no"))
    print("  - total lines: %d" % file_report.total_lines)
    print("  - non-empty lines: %d" % file_report.non_empty_lines)
    print("  - valid JSON lines: %d" % file_report.valid_json_lines)
    print("  - invalid JSON lines: %d" % file_report.invalid_json_lines)
    print("  - exploitable lines: %d" % file_report.exploitable_lines)
    print(
        "  - objective_ids: %s"
        % (", ".join(file_report.objective_ids) if file_report.objective_ids else "none")
    )
    print(
        "  - useful fields detected: %s"
        % (
            ", ".join(file_report.useful_fields_detected)
            if file_report.useful_fields_detected
            else "none"
        )
    )

    if verbose:
        print(
            "  - useful fields missing: %s"
            % (
                ", ".join(file_report.useful_fields_missing)
                if file_report.useful_fields_missing
                else "none"
            )
        )

    if file_report.issues:
        print("  - issues:")
        for issue in file_report.issues:
            print("    - %s" % issue)
    elif verbose:
        print("  - issues: none")

    if file_report.warnings:
        print("  - warnings:")
        for warning in file_report.warnings:
            print("    - %s" % warning)
    elif verbose:
        print("  - warnings: none")


def _print_text_report(report: RuntimeFilesValidationReport, verbose: bool) -> None:
    print("Support metrics runtime files validation:")
    print("- overall: %s" % report.overall)
    print("- checked files: %d" % report.checked_files)
    print("- issues: %d" % report.issues_count)
    print("- warnings: %d" % report.warnings_count)
    _print_file_report(report.baseline, verbose=verbose)
    _print_file_report(report.current, verbose=verbose)


def main() -> int:
    args = _build_parser().parse_args()

    report = build_runtime_files_validation_report(
        baseline_path=args.baseline,
        current_path=args.current,
    )

    if args.json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        _print_text_report(report, verbose=bool(args.verbose))

    if args.check and report.overall == STATE_ERROR:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
