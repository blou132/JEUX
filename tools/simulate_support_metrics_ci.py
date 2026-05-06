from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import tempfile


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Simulate the GitHub Actions support metrics CI step locally."
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        required=True,
        help="Path to baseline support metrics history JSONL.",
    )
    parser.add_argument(
        "--current",
        type=Path,
        required=True,
        help="Path to current support metrics history JSONL.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Root directory used to generate local artifacts (default: temporary directory).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero on technical analysis errors.",
    )
    parser.add_argument(
        "--analyze-script",
        type=Path,
        default=None,
        help="Optional analyze script override (useful for tests).",
    )
    parser.add_argument(
        "--report-mode",
        type=str,
        default="local",
        help="Provenance mode forwarded to support metrics summary script (default: local).",
    )
    return parser


def _resolve_output_dir(output_dir: Path | None) -> Path:
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    return Path(tempfile.mkdtemp(prefix="support_metrics_ci_sim_"))


def _build_command(
    summary_script_path: Path,
    baseline_path: Path,
    current_path: Path,
    report_output_path: Path,
    step_summary_path: Path,
    strict_mode: bool,
    analyze_script_path: Path | None,
    report_mode: str,
    input_label: str,
    compare_input_label: str,
) -> list[str]:
    command: list[str] = [
        sys.executable,
        str(summary_script_path),
        "--baseline",
        str(baseline_path),
        "--current",
        str(current_path),
        "--report-output",
        str(report_output_path),
        "--step-summary",
        str(step_summary_path),
        "--artifact-name",
        "support-metrics-report",
        "--report-mode",
        report_mode,
        "--input-label",
        input_label,
        "--compare-input-label",
        compare_input_label,
        "--ci-check",
    ]
    if strict_mode:
        command.append("--strict")
    if analyze_script_path is not None:
        command.extend(["--analyze-script", str(analyze_script_path)])
    return command


def main() -> int:
    args = _build_parser().parse_args()

    output_root = _resolve_output_dir(args.output_dir)
    artifacts_dir = output_root / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    report_output_path = artifacts_dir / "support_metrics_report.md"
    step_summary_path = artifacts_dir / "github_step_summary.md"
    summary_script_path = Path(__file__).with_name("write_support_metrics_ci_summary.py")

    command = _build_command(
        summary_script_path=summary_script_path,
        baseline_path=args.baseline,
        current_path=args.current,
        report_output_path=report_output_path,
        step_summary_path=step_summary_path,
        strict_mode=bool(args.strict),
        analyze_script_path=args.analyze_script,
        report_mode=str(args.report_mode).strip() or "local",
        input_label="local:%s" % str(args.baseline),
        compare_input_label="local:%s" % str(args.current),
    )
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)

    print("support_metrics_report=%s" % report_output_path)
    print("github_step_summary=%s" % step_summary_path)

    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
