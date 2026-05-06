from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
from typing import Sequence


DEFAULT_PROJECT_PATH = Path("game3d")
DEFAULT_OUTPUT_BY_MODE: dict[str, Path] = {
    "baseline": Path("outputs/ci/support_metrics_baseline.jsonl"),
    "current": Path("outputs/ci/support_metrics_current.jsonl"),
}
DEFAULT_HISTORY_FILENAME = "run_metrics_history.jsonl"
DEFAULT_PROJECT_NAME = "Sandbox Fantasy 3D MVP"
DEFAULT_QUIT_AFTER_FRAMES = 4200


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run local Godot runtime sessions and collect support metrics JSONL "
            "for baseline/current comparison."
        )
    )
    parser.add_argument(
        "--mode",
        choices=["baseline", "current"],
        required=True,
        help="Collection mode. Selects the default output file when --output is not provided.",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Number of runtime runs to execute (default: 5).",
    )
    parser.add_argument(
        "--seed-start",
        type=int,
        default=1000,
        help="Seed value used for run labels (default: 1000).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Output JSONL path. Default depends on --mode: "
            "outputs/ci/support_metrics_baseline.jsonl or "
            "outputs/ci/support_metrics_current.jsonl."
        ),
    )
    parser.add_argument(
        "--godot-bin",
        type=str,
        default="godot",
        help="Godot executable path or command name (default: godot).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned commands without launching Godot (always exits with code 0).",
    )
    parser.add_argument(
        "--project-path",
        type=Path,
        default=DEFAULT_PROJECT_PATH,
        help="Godot project directory containing project.godot (default: game3d).",
    )
    parser.add_argument(
        "--history-path",
        type=Path,
        default=None,
        help="Optional explicit path to run_metrics_history.jsonl (advanced usage).",
    )
    parser.add_argument(
        "--quit-after",
        type=int,
        default=DEFAULT_QUIT_AFTER_FRAMES,
        help=(
            "Frame budget passed to Godot --quit-after to avoid hanging runs "
            "(default: 4200)."
        ),
    )
    return parser


def _read_project_name(project_path: Path) -> str:
    project_file = project_path / "project.godot"
    if not project_file.exists():
        return DEFAULT_PROJECT_NAME
    content = project_file.read_text(encoding="utf-8")
    match = re.search(r'^config/name="([^"]+)"', content, flags=re.MULTILINE)
    if match is None:
        return DEFAULT_PROJECT_NAME
    value = match.group(1).strip()
    return value if value else DEFAULT_PROJECT_NAME


def _godot_user_data_root() -> Path:
    if os.name == "nt":
        appdata = os.getenv("APPDATA", "").strip()
        if appdata:
            return Path(appdata) / "Godot" / "app_userdata"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Godot" / "app_userdata"
    return Path.home() / ".local" / "share" / "godot" / "app_userdata"


def _resolve_history_path(project_path: Path, explicit_path: Path | None) -> Path:
    if explicit_path is not None:
        return explicit_path
    project_name = _read_project_name(project_path)
    return _godot_user_data_root() / project_name / DEFAULT_HISTORY_FILENAME


def _resolve_godot_executable(godot_bin: str) -> str | None:
    candidate_path = Path(godot_bin)
    if candidate_path.exists():
        return str(candidate_path)
    resolved = shutil.which(godot_bin)
    if resolved is not None:
        return resolved
    return None


def _read_jsonl_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return [line for line in lines if line.strip()]


def _build_output_path(mode: str, output_path: Path | None) -> Path:
    if output_path is not None:
        return output_path
    return DEFAULT_OUTPUT_BY_MODE[mode]


def _build_run_command(
    godot_executable: str,
    project_path: Path,
    seed: int,
    quit_after_frames: int,
) -> list[str]:
    return [
        godot_executable,
        "--headless",
        "--path",
        str(project_path),
        "--quit-after",
        str(quit_after_frames),
        "--",
        "--support-metrics-seed",
        str(seed),
    ]


def _format_command(command: list[str]) -> str:
    if os.name == "nt":
        return subprocess.list2cmdline(command)
    return shlex.join(command)


def _print_configuration(
    mode: str,
    runs: int,
    seed_start: int,
    output_path: Path,
    project_path: Path,
    history_path: Path,
    dry_run: bool,
) -> None:
    print("Support metrics runtime collection")
    print("- mode: %s" % mode)
    print("- runs: %d" % runs)
    print("- seed_start: %d" % seed_start)
    print("- output: %s" % output_path)
    print("- project_path: %s" % project_path)
    print("- history_path: %s" % history_path)
    print("- dry_run: %s" % ("yes" if dry_run else "no"))


def _collect_runtime_entries(
    commands: list[list[str]],
    history_path: Path,
) -> tuple[int, list[str]]:
    collected: list[str] = []
    previous_lines = _read_jsonl_lines(history_path)

    for run_index, command in enumerate(commands, start=1):
        seed_value = command[-1]
        print("Run %d/%d (seed=%s): %s" % (run_index, len(commands), seed_value, _format_command(command)))
        env = os.environ.copy()
        env["SUPPORT_METRICS_SEED"] = seed_value
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            env=env,
        )
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)

        if result.returncode != 0:
            print(
                "Godot run failed for seed %s with return code %d."
                % (seed_value, result.returncode),
                file=sys.stderr,
            )
            return 3, collected

        current_lines = _read_jsonl_lines(history_path)
        new_lines = current_lines[len(previous_lines) :]
        if not new_lines:
            print(
                (
                    "No new run metrics were exported after seed %s. "
                    "Ensure the run reaches completed/failed state and exports metrics."
                )
                % seed_value,
                file=sys.stderr,
            )
            return 4, collected
        collected.append(new_lines[-1])
        previous_lines = current_lines

    return 0, collected


def _write_output_jsonl(output_path: Path, lines: list[str]) -> int:
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        content = ""
        if lines:
            content = "\n".join(lines) + "\n"
        output_path.write_text(content, encoding="utf-8")
        return 0
    except OSError as exc:
        print("Unable to write output JSONL: %s" % str(exc), file=sys.stderr)
        return 5


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.runs <= 0:
        print("--runs must be greater than 0.", file=sys.stderr)
        return 2
    if args.quit_after <= 0:
        print("--quit-after must be greater than 0.", file=sys.stderr)
        return 2

    project_path = args.project_path.resolve()
    output_path = _build_output_path(args.mode, args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    history_path = _resolve_history_path(project_path, args.history_path)

    _print_configuration(
        mode=args.mode,
        runs=args.runs,
        seed_start=args.seed_start,
        output_path=output_path,
        project_path=project_path,
        history_path=history_path,
        dry_run=bool(args.dry_run),
    )

    commands: list[list[str]] = []
    for offset in range(args.runs):
        seed = args.seed_start + offset
        commands.append(
            _build_run_command(
                godot_executable=args.godot_bin,
                project_path=project_path,
                seed=seed,
                quit_after_frames=args.quit_after,
            )
        )

    if args.dry_run:
        print("DRY-RUN: planned commands")
        for run_index, command in enumerate(commands, start=1):
            print("- run %d: %s" % (run_index, _format_command(command)))
        print("Dry-run completed. No Godot process was started.")
        return 0

    resolved_godot = _resolve_godot_executable(args.godot_bin)
    if resolved_godot is None:
        print(
            (
                "Godot binary not found: '%s'. Install Godot or pass --godot-bin "
                "with a valid executable path. Use --dry-run to preview commands."
            )
            % args.godot_bin,
            file=sys.stderr,
        )
        return 2

    commands_with_resolved_bin = []
    for command in commands:
        resolved_command = command.copy()
        resolved_command[0] = resolved_godot
        commands_with_resolved_bin.append(resolved_command)

    collect_status, collected_lines = _collect_runtime_entries(
        commands=commands_with_resolved_bin,
        history_path=history_path,
    )
    if collect_status != 0:
        if collected_lines:
            print(
                "Partial collection: %d run(s) captured before failure."
                % len(collected_lines),
                file=sys.stderr,
            )
        return collect_status

    write_status = _write_output_jsonl(output_path, collected_lines)
    if write_status != 0:
        return write_status

    print("Collected %d run metric entries." % len(collected_lines))
    print("Output written to: %s" % output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
