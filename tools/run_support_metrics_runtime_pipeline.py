from __future__ import annotations

import argparse
import json
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
from typing import Any


DEFAULT_BASELINE_OUTPUT = Path("outputs/ci/support_metrics_baseline.jsonl")
DEFAULT_CURRENT_OUTPUT = Path("outputs/ci/support_metrics_current.jsonl")
DEFAULT_REPORT_OUTPUT = Path("outputs/ci/support_metrics_runtime_comparison.md")
DEFAULT_DECISION_OUTPUT = Path("outputs/ci/support_metrics_runtime_decision.md")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run local runtime support metrics pipeline: collect baseline/current, "
            "validate runtime files, compare results, and generate a Markdown report."
        )
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Number of runtime runs for baseline/current collection (default: 5).",
    )
    parser.add_argument(
        "--seed-start",
        type=int,
        default=1000,
        help="Seed start for runtime collection (default: 1000).",
    )
    parser.add_argument(
        "--baseline-output",
        type=Path,
        default=DEFAULT_BASELINE_OUTPUT,
        help="Baseline output JSONL path.",
    )
    parser.add_argument(
        "--current-output",
        type=Path,
        default=DEFAULT_CURRENT_OUTPUT,
        help="Current output JSONL path.",
    )
    parser.add_argument(
        "--report-output",
        type=Path,
        default=DEFAULT_REPORT_OUTPUT,
        help="Markdown comparison report output path.",
    )
    parser.add_argument(
        "--decision-output",
        type=Path,
        default=DEFAULT_DECISION_OUTPUT,
        help="Markdown runtime decision report output path.",
    )
    parser.add_argument(
        "--decision-json-output",
        type=Path,
        default=None,
        help="Optional JSON runtime decision output path.",
    )
    parser.add_argument(
        "--min-runs",
        type=int,
        default=5,
        help="Minimum runs required per side for runtime decision protocol (default: 5).",
    )
    parser.add_argument(
        "--godot-bin",
        type=str,
        default="godot",
        help="Godot executable path or command name (default: godot).",
    )
    parser.add_argument(
        "--objective",
        type=str,
        default="",
        help=(
            "Optional runtime objective override forwarded to runtime collection "
            "(example: rally_champion)."
        ),
    )
    parser.add_argument(
        "--export-on-quit",
        action="store_true",
        help=(
            "Debug/CI only: forward export-on-quit mode to runtime collection so Godot "
            "forces runtime export at controlled quit."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned commands only and exit with code 0.",
    )
    parser.add_argument(
        "--skip-collect",
        action="store_true",
        help="Skip runtime collection and use existing baseline/current files.",
    )
    parser.add_argument(
        "--skip-decision",
        action="store_true",
        help="Skip runtime tuning decision report generation.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "Fail on validation warnings and enable strict regression check in the "
            "comparative analysis."
        ),
    )
    return parser


def _format_command(command: list[str]) -> str:
    if sys.platform.startswith("win"):
        return subprocess.list2cmdline(command)
    return shlex.join(command)


def _set_command_option_value(command: list[str], option_name: str, option_value: str) -> None:
    try:
        option_index = command.index(option_name)
    except ValueError:
        return
    value_index = option_index + 1
    if value_index >= len(command):
        return
    command[value_index] = option_value


def _resolve_godot_executable(godot_bin: str) -> str | None:
    candidate_path = Path(godot_bin)
    if candidate_path.exists():
        return str(candidate_path)
    resolved = shutil.which(godot_bin)
    if resolved is not None:
        return resolved
    return None


def _collect_script_path() -> Path:
    return Path(__file__).with_name("collect_support_metrics_runtime.py")


def _validate_script_path() -> Path:
    return Path(__file__).with_name("validate_support_metrics_runtime_files.py")


def _analyze_script_path() -> Path:
    return Path(__file__).with_name("analyze_run_metrics_history.py")


def _decide_script_path() -> Path:
    return Path(__file__).with_name("decide_support_metrics_runtime_tuning.py")


def _build_collect_command(
    mode: str,
    output_path: Path,
    runs: int,
    seed_start: int,
    godot_bin: str,
    objective: str,
    export_on_quit: bool,
) -> list[str]:
    command = [
        sys.executable,
        str(_collect_script_path()),
        "--mode",
        mode,
        "--runs",
        str(runs),
        "--seed-start",
        str(seed_start),
        "--output",
        str(output_path),
        "--godot-bin",
        godot_bin,
    ]
    objective_value = objective.strip()
    if objective_value != "":
        command.extend(["--objective", objective_value])
    if export_on_quit:
        command.append("--export-on-quit")
    return command


def _collect_forwarded_godot_flags(command: list[str]) -> list[str]:
    forwarded: list[str] = []
    if "--objective" in command:
        objective_index = command.index("--objective")
        objective_value_index = objective_index + 1
        if objective_value_index < len(command):
            forwarded.extend(
                ["--support-metrics-objective", str(command[objective_value_index])]
            )
    if "--export-on-quit" in command:
        forwarded.append("--support-metrics-export-on-quit")
    return forwarded


def _build_validate_command(
    baseline_output: Path,
    current_output: Path,
) -> list[str]:
    return [
        sys.executable,
        str(_validate_script_path()),
        "--baseline",
        str(baseline_output),
        "--current",
        str(current_output),
        "--check",
        "--json",
    ]


def _build_analyze_command(
    baseline_output: Path,
    current_output: Path,
    report_output: Path,
    strict: bool,
) -> list[str]:
    command = [
        sys.executable,
        str(_analyze_script_path()),
        "--input",
        str(baseline_output),
        "--compare-input",
        str(current_output),
        "--report-mode",
        "runtime",
        "--ci-check",
        "--format",
        "markdown",
        "--output",
        str(report_output),
    ]
    if strict:
        command.append("--fail-on-regression")
    return command


def _build_decision_command(
    baseline_output: Path,
    current_output: Path,
    decision_output: Path,
    min_runs: int,
    with_json_output: bool,
) -> list[str]:
    command = [
        sys.executable,
        str(_decide_script_path()),
        "--baseline",
        str(baseline_output),
        "--current",
        str(current_output),
        "--min-runs",
        str(min_runs),
        "--markdown-output",
        str(decision_output),
    ]
    if with_json_output:
        command.append("--json")
    return command


def _print_planned_commands(
    collect_commands: list[list[str]],
    validate_command: list[str],
    analyze_command: list[str],
    decision_command: list[str],
    skip_collect: bool,
    skip_decision: bool,
) -> None:
    print("Support metrics runtime pipeline")
    print("- dry_run: yes")
    print("- skip_collect: %s" % ("yes" if skip_collect else "no"))
    print("- skip_decision: %s" % ("yes" if skip_decision else "no"))
    print("DRY-RUN: planned commands")
    if skip_collect:
        print("- collect: skipped (--skip-collect)")
    else:
        for index, command in enumerate(collect_commands, start=1):
            print("- collect %d: %s" % (index, _format_command(command)))
            forwarded_flags = _collect_forwarded_godot_flags(command)
            if forwarded_flags:
                print("- collect %d forwarded Godot flags: %s" % (index, " ".join(forwarded_flags)))
    print("- validate: %s" % _format_command(validate_command))
    print("- analyze: %s" % _format_command(analyze_command))
    if skip_decision:
        print("- decision: skipped (--skip-decision)")
    else:
        print("- decision: %s" % _format_command(decision_command))
    print("Dry-run completed. No command was executed.")


def _run_command(command: list[str], step_name: str) -> subprocess.CompletedProcess[str]:
    print("Running %s:" % step_name)
    print("- command: %s" % _format_command(command))
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    return result


def _load_validation_report(validation_stdout: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(validation_stdout)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    return parsed


def _run_validation(
    baseline_output: Path,
    current_output: Path,
    strict: bool,
) -> int:
    validate_command = _build_validate_command(baseline_output, current_output)
    validate_result = _run_command(validate_command, "runtime file validation")
    if validate_result.returncode != 0:
        print(
            "Runtime file validation failed. Ensure baseline/current files exist and are valid JSONL.",
            file=sys.stderr,
        )
        return validate_result.returncode

    report = _load_validation_report(validate_result.stdout)
    if report is None:
        print(
            "Runtime file validation returned invalid JSON output.",
            file=sys.stderr,
        )
        return 1

    overall = str(report.get("overall", "error")).strip().lower()
    issues_count = int(report.get("issues_count", 0))
    warnings_count = int(report.get("warnings_count", 0))
    print(
        "Validation summary: overall=%s issues=%d warnings=%d"
        % (overall, issues_count, warnings_count)
    )

    if strict and overall != "ok":
        print(
            "Strict mode: runtime file validation warnings/errors are treated as failure.",
            file=sys.stderr,
        )
        return 1
    return 0


def _ensure_skip_collect_files_exist(
    baseline_output: Path,
    current_output: Path,
) -> int:
    missing: list[str] = []
    if not baseline_output.exists():
        missing.append(str(baseline_output))
    if not current_output.exists():
        missing.append(str(current_output))
    if not missing:
        return 0

    print(
        "skip-collect requires existing runtime files; missing: %s"
        % ", ".join(missing),
        file=sys.stderr,
    )
    return 2


def _write_decision_json_output(
    decision_json_output: Path,
    decision_stdout: str,
) -> int:
    try:
        parsed = json.loads(decision_stdout)
    except json.JSONDecodeError:
        print(
            "Runtime decision output is not valid JSON; unable to write --decision-json-output.",
            file=sys.stderr,
        )
        return 1
    if not isinstance(parsed, dict):
        print(
            "Runtime decision output JSON must be an object; unable to write --decision-json-output.",
            file=sys.stderr,
        )
        return 1
    decision_json_output.parent.mkdir(parents=True, exist_ok=True)
    decision_json_output.write_text(
        json.dumps(parsed, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


def main() -> int:
    args = _build_parser().parse_args()

    if args.runs <= 0:
        print("--runs must be greater than 0.", file=sys.stderr)
        return 2
    if args.min_runs <= 0:
        print("--min-runs must be greater than 0.", file=sys.stderr)
        return 2

    baseline_output = args.baseline_output
    current_output = args.current_output
    report_output = args.report_output
    decision_output = args.decision_output

    collect_baseline_command = _build_collect_command(
        mode="baseline",
        output_path=baseline_output,
        runs=args.runs,
        seed_start=args.seed_start,
        godot_bin=args.godot_bin,
        objective=str(args.objective),
        export_on_quit=bool(args.export_on_quit),
    )
    collect_current_command = _build_collect_command(
        mode="current",
        output_path=current_output,
        runs=args.runs,
        seed_start=args.seed_start,
        godot_bin=args.godot_bin,
        objective=str(args.objective),
        export_on_quit=bool(args.export_on_quit),
    )
    validate_command = _build_validate_command(baseline_output, current_output)
    analyze_command = _build_analyze_command(
        baseline_output=baseline_output,
        current_output=current_output,
        report_output=report_output,
        strict=bool(args.strict),
    )
    decision_command = _build_decision_command(
        baseline_output=baseline_output,
        current_output=current_output,
        decision_output=decision_output,
        min_runs=int(args.min_runs),
        with_json_output=args.decision_json_output is not None,
    )

    if args.dry_run:
        _print_planned_commands(
            collect_commands=[collect_baseline_command, collect_current_command],
            validate_command=validate_command,
            analyze_command=analyze_command,
            decision_command=decision_command,
            skip_collect=bool(args.skip_collect),
            skip_decision=bool(args.skip_decision),
        )
        return 0

    if args.skip_collect:
        missing_check_status = _ensure_skip_collect_files_exist(
            baseline_output=baseline_output,
            current_output=current_output,
        )
        if missing_check_status != 0:
            return missing_check_status
    else:
        resolved_godot = _resolve_godot_executable(args.godot_bin)
        if resolved_godot is None:
            print(
                (
                    "Godot binary not found: '%s'. Install Godot or use --skip-collect "
                    "with existing runtime files."
                )
                % args.godot_bin,
                file=sys.stderr,
            )
            return 2

        _set_command_option_value(collect_baseline_command, "--godot-bin", resolved_godot)
        _set_command_option_value(collect_current_command, "--godot-bin", resolved_godot)

        baseline_result = _run_command(collect_baseline_command, "runtime collection (baseline)")
        if baseline_result.returncode != 0:
            print("Baseline runtime collection failed.", file=sys.stderr)
            return baseline_result.returncode

        current_result = _run_command(collect_current_command, "runtime collection (current)")
        if current_result.returncode != 0:
            print("Current runtime collection failed.", file=sys.stderr)
            return current_result.returncode

    validation_status = _run_validation(
        baseline_output=baseline_output,
        current_output=current_output,
        strict=bool(args.strict),
    )
    if validation_status != 0:
        return validation_status

    report_output.parent.mkdir(parents=True, exist_ok=True)
    analyze_result = _run_command(analyze_command, "comparative analysis")
    if analyze_result.returncode != 0:
        print("Comparative analysis failed.", file=sys.stderr)
        return analyze_result.returncode

    if not args.skip_decision:
        decision_output.parent.mkdir(parents=True, exist_ok=True)
        decision_result = _run_command(decision_command, "runtime tuning decision")
        if decision_result.returncode != 0:
            print("Runtime tuning decision failed.", file=sys.stderr)
            return decision_result.returncode
        if args.decision_json_output is not None:
            json_write_status = _write_decision_json_output(
                decision_json_output=args.decision_json_output,
                decision_stdout=decision_result.stdout,
            )
            if json_write_status != 0:
                return json_write_status

    print("Runtime support metrics pipeline completed.")
    print("Report written to: %s" % report_output)
    if not args.skip_decision:
        print("Decision report written to: %s" % decision_output)
    if args.decision_json_output is not None and not args.skip_decision:
        print("Decision JSON written to: %s" % args.decision_json_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
