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
    parser.add_argument(
        "--diagnose",
        action="store_true",
        help=(
            "Print detailed runtime collection diagnostics (history file state, "
            "command details, and no-export root causes)."
        ),
    )
    parser.add_argument(
        "--allow-existing-history",
        action="store_true",
        help=(
            "Allow reusing existing history lines when no new export line is produced. "
            "Disabled by default to avoid false runtime success."
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


def _history_snapshot(path: Path) -> dict[str, object]:
    exists = path.exists()
    snapshot: dict[str, object] = {
        "path": str(path),
        "exists": exists,
        "readable": False,
        "size_bytes": 0,
        "line_count": 0,
        "lines": [],
        "read_error": "",
    }
    if not exists:
        return snapshot

    try:
        size_bytes = int(path.stat().st_size)
    except OSError as exc:
        snapshot["read_error"] = str(exc)
        return snapshot

    try:
        lines = _read_jsonl_lines(path)
    except OSError as exc:
        snapshot["size_bytes"] = size_bytes
        snapshot["read_error"] = str(exc)
        return snapshot

    snapshot["readable"] = True
    snapshot["size_bytes"] = size_bytes
    snapshot["line_count"] = len(lines)
    snapshot["lines"] = lines
    return snapshot


def _to_bool(value: object) -> bool:
    return bool(value)


def _to_int(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    return 0


def _to_str(value: object) -> str:
    if isinstance(value, str):
        return value
    return ""


def _to_lines(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, str)]


def _truncate_line(line: str, max_length: int = 180) -> str:
    if len(line) <= max_length:
        return line
    return line[: max(0, max_length - 3)] + "..."


def _tail_lines(lines: list[str], count: int = 3) -> list[str]:
    if count <= 0:
        return []
    if len(lines) <= count:
        return lines
    return lines[-count:]


def _print_snapshot(prefix: str, snapshot: dict[str, object]) -> None:
    print("%s history file found: %s" % (prefix, "yes" if _to_bool(snapshot.get("exists")) else "no"))
    print("%s history readable: %s" % (prefix, "yes" if _to_bool(snapshot.get("readable")) else "no"))
    print("%s history size bytes: %d" % (prefix, _to_int(snapshot.get("size_bytes"))))
    print("%s history line count: %d" % (prefix, _to_int(snapshot.get("line_count"))))
    read_error = _to_str(snapshot.get("read_error")).strip()
    if read_error != "":
        print("%s history read error: %s" % (prefix, read_error))
    tail = _tail_lines(_to_lines(snapshot.get("lines")), count=3)
    if tail:
        print("%s history tail lines:" % prefix)
        for raw_line in tail:
            print("  - %s" % _truncate_line(raw_line))


def _select_existing_history_line(
    lines: list[str],
    total_runs: int,
    run_index: int,
) -> str | None:
    if total_runs <= 0 or run_index <= 0:
        return None
    if not lines:
        return None
    offset_from_end = total_runs - run_index + 1
    candidate_index = len(lines) - offset_from_end
    if candidate_index < 0 or candidate_index >= len(lines):
        return None
    return lines[candidate_index]


def _build_no_new_export_error(
    seed_value: str,
    command: list[str],
    before_snapshot: dict[str, object],
    after_snapshot: dict[str, object],
) -> str:
    before_found = "yes" if _to_bool(before_snapshot.get("exists")) else "no"
    after_found = "yes" if _to_bool(after_snapshot.get("exists")) else "no"
    before_lines = _to_int(before_snapshot.get("line_count"))
    after_lines = _to_int(after_snapshot.get("line_count"))
    before_size = _to_int(before_snapshot.get("size_bytes"))
    after_size = _to_int(after_snapshot.get("size_bytes"))

    messages: list[str] = []
    messages.append("No new run metrics were exported after seed %s." % seed_value)
    messages.append("Godot launched: yes")
    messages.append("command: %s" % _format_command(command))
    messages.append("history file found (before): %s" % before_found)
    messages.append("history file found (after): %s" % after_found)
    messages.append("history line count before: %d" % before_lines)
    messages.append("history line count after: %d" % after_lines)
    messages.append("history size bytes before: %d" % before_size)
    messages.append("history size bytes after: %d" % after_size)
    messages.append("expected new lines: > 0")
    messages.append("possible causes:")
    messages.append("- game did not run the export path")
    messages.append("- wrong project path")
    messages.append("- wrong history path")
    messages.append("- run ended before metrics export")
    messages.append("- Godot CLI arguments not handled by project")
    return "\n".join(messages)


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
    diagnose: bool,
    allow_existing_history: bool,
) -> None:
    print("Support metrics runtime collection")
    print("- mode: %s" % mode)
    print("- runs: %d" % runs)
    print("- seed_start: %d" % seed_start)
    print("- output: %s" % output_path)
    print("- project_path: %s" % project_path)
    print("- history_path: %s" % history_path)
    print("- dry_run: %s" % ("yes" if dry_run else "no"))
    print("- diagnose: %s" % ("yes" if diagnose else "no"))
    print("- allow_existing_history: %s" % ("yes" if allow_existing_history else "no"))


def _collect_runtime_entries(
    commands: list[list[str]],
    history_path: Path,
    diagnose: bool,
    allow_existing_history: bool,
) -> tuple[int, list[str]]:
    collected: list[str] = []

    for run_index, command in enumerate(commands, start=1):
        seed_value = command[-1]
        before_snapshot = _history_snapshot(history_path)
        before_lines = _to_lines(before_snapshot.get("lines"))

        if diagnose:
            print("")
            print("DIAGNOSE run %d/%d" % (run_index, len(commands)))
            print("- seed: %s" % seed_value)
            print("- command: %s" % _format_command(command))
            _print_snapshot("- before", before_snapshot)

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

        after_snapshot = _history_snapshot(history_path)
        after_lines = _to_lines(after_snapshot.get("lines"))
        before_count = _to_int(before_snapshot.get("line_count"))
        after_count = _to_int(after_snapshot.get("line_count"))
        new_lines: list[str] = []
        if before_count >= 0 and after_count >= before_count and len(after_lines) >= before_count:
            new_lines = after_lines[before_count:]

        if diagnose:
            _print_snapshot("- after", after_snapshot)
            print("- new lines detected: %d" % len(new_lines))
            if new_lines:
                print("- new line tail:")
                for raw_line in _tail_lines(new_lines, count=3):
                    print("  - %s" % _truncate_line(raw_line))

        if not new_lines:
            if allow_existing_history:
                fallback_line = _select_existing_history_line(
                    lines=after_lines if after_lines else before_lines,
                    total_runs=len(commands),
                    run_index=run_index,
                )
                if fallback_line is not None:
                    collected.append(fallback_line)
                    print(
                        (
                            "No new metrics line detected for seed %s; "
                            "reused existing history line due to --allow-existing-history."
                        )
                        % seed_value
                    )
                    if diagnose:
                        print("- reused line: %s" % _truncate_line(fallback_line))
                    continue

            error_message = _build_no_new_export_error(
                seed_value=seed_value,
                command=command,
                before_snapshot=before_snapshot,
                after_snapshot=after_snapshot,
            )
            print(
                error_message,
                file=sys.stderr,
            )
            return 4, collected
        collected.append(new_lines[-1])

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
        diagnose=bool(args.diagnose),
        allow_existing_history=bool(args.allow_existing_history),
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
        if args.diagnose:
            print("")
            print("DIAGNOSE dry-run context")
            print("- godot_bin: %s" % args.godot_bin)
            print("- project_path: %s" % project_path)
            print("- history_path: %s" % history_path)
            print("- output_path: %s" % output_path)
            for run_index, command in enumerate(commands, start=1):
                print("- seed[%d]: %s" % (run_index, command[-1]))
                print("  command[%d]: %s" % (run_index, _format_command(command)))
            _print_snapshot("- current", _history_snapshot(history_path))
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
        diagnose=bool(args.diagnose),
        allow_existing_history=bool(args.allow_existing_history),
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
