from __future__ import annotations

import argparse
import json
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
DEFAULT_PROBE_OUTPUT_PATH = Path("outputs/ci/support_metrics_runtime_probe.json")
DEFAULT_TRACE_OUTPUT_PATH = Path("outputs/ci/support_metrics_runtime_export_trace.json")
KNOWN_RUNTIME_OBJECTIVES: tuple[str, ...] = (
    "observe_dominance",
    "survive_calamity",
    "watch_champion_rise",
    "rally_champion",
    "support_gate",
)


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
    parser.add_argument(
        "--probe",
        action="store_true",
        help=(
            "Run a Godot runtime probe handshake that validates CLI argument propagation "
            "and writes outputs/ci/support_metrics_runtime_probe.json."
        ),
    )
    parser.add_argument(
        "--trace-export",
        action="store_true",
        help=(
            "Enable export trace diagnostics and expect "
            "outputs/ci/support_metrics_runtime_export_trace.json from Godot."
        ),
    )
    parser.add_argument(
        "--objective",
        type=str,
        default="",
        help=(
            "Optional runtime objective override for debug/CI collection "
            "(example: rally_champion)."
        ),
    )
    parser.add_argument(
        "--export-on-quit",
        action="store_true",
        help=(
            "Debug/CI mode: request a forced runtime export on controlled quit "
            "when objective flow did not naturally export before --quit-after."
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
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
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


def _build_probe_missing_error(
    command: list[str],
    project_path: Path,
    history_path: Path,
    output_path: Path,
    probe_output_path: Path,
) -> str:
    messages: list[str] = []
    messages.append("Godot launched, but project did not execute support metrics probe.")
    messages.append("command: %s" % _format_command(command))
    messages.append("project_path: %s" % project_path)
    messages.append("history_path: %s" % history_path)
    messages.append("output_path: %s" % output_path)
    messages.append("probe_output_path: %s" % probe_output_path)
    messages.append("possible causes:")
    messages.append("- mauvais project path")
    messages.append("- mauvaise scene principale")
    messages.append("- arguments CLI non propages")
    messages.append("- code probe non charge")
    return "\n".join(messages)


def _build_trace_missing_error(
    command: list[str],
    project_path: Path,
    history_path: Path,
    output_path: Path,
    trace_output_path: Path,
) -> str:
    messages: list[str] = []
    messages.append("Godot launched, probe works, but export trace was not produced.")
    messages.append("command: %s" % _format_command(command))
    messages.append("project_path: %s" % project_path)
    messages.append("history_path: %s" % history_path)
    messages.append("output_path: %s" % output_path)
    messages.append("trace_output_path: %s" % trace_output_path)
    messages.append("possible causes:")
    messages.append("- mauvais project path")
    messages.append("- mauvaise scene principale")
    messages.append("- arguments CLI non propages")
    messages.append("- code trace export non charge")
    return "\n".join(messages)


def _build_output_path(mode: str, output_path: Path | None) -> Path:
    if output_path is not None:
        return output_path
    return DEFAULT_OUTPUT_BY_MODE[mode]


def _normalize_objective(raw_value: str) -> str:
    return raw_value.strip()


def _warn_unknown_objective(objective: str) -> None:
    if objective == "":
        return
    if objective in KNOWN_RUNTIME_OBJECTIVES:
        return
    known_values = ", ".join(KNOWN_RUNTIME_OBJECTIVES)
    print(
        (
            "Warning: objective '%s' is not in known runtime objectives [%s]. "
            "The value will still be forwarded to Godot for debug/CI diagnostics."
        )
        % (objective, known_values),
        file=sys.stderr,
    )


def _build_run_command(
    godot_executable: str,
    project_path: Path,
    seed: int,
    quit_after_frames: int,
    history_path: Path,
    output_path: Path,
    probe_output_path: Path,
    trace_output_path: Path,
    objective: str,
    probe: bool,
    trace_export: bool,
    export_on_quit: bool,
) -> list[str]:
    command = [
        godot_executable,
        "--headless",
        "--path",
        str(project_path),
        "--quit-after",
        str(quit_after_frames),
        "--",
        "--support-metrics-seed",
        str(seed),
        "--support-metrics-quit-after",
        str(quit_after_frames),
        "--support-metrics-history-path",
        str(history_path.resolve()),
        "--support-metrics-output-path",
        str(output_path.resolve()),
    ]
    if objective.strip() != "":
        command.extend(["--support-metrics-objective", objective.strip()])
    if export_on_quit:
        command.append("--support-metrics-export-on-quit")
    if probe:
        command.extend(
            [
                "--support-metrics-probe",
                "--support-metrics-probe-output",
                str(probe_output_path.resolve()),
            ]
        )
    if trace_export:
        command.extend(
            [
                "--support-metrics-trace-export",
                "--support-metrics-trace-output",
                str(trace_output_path.resolve()),
            ]
        )
    return command


def _format_command(command: list[str]) -> str:
    if os.name == "nt":
        return subprocess.list2cmdline(command)
    return shlex.join(command)


def _extract_command_arg_value(command: list[str], flag: str) -> str:
    try:
        flag_index = command.index(flag)
    except ValueError:
        return ""
    value_index = flag_index + 1
    if value_index >= len(command):
        return ""
    return command[value_index]


def _print_configuration(
    mode: str,
    runs: int,
    seed_start: int,
    objective: str,
    output_path: Path,
    probe_output_path: Path,
    trace_output_path: Path,
    project_path: Path,
    history_path: Path,
    dry_run: bool,
    diagnose: bool,
    allow_existing_history: bool,
    probe: bool,
    trace_export: bool,
    export_on_quit: bool,
) -> None:
    print("Support metrics runtime collection")
    print("- mode: %s" % mode)
    print("- runs: %d" % runs)
    print("- seed_start: %d" % seed_start)
    print("- objective: %s" % (objective if objective != "" else "(default)"))
    print("- output: %s" % output_path)
    print("- probe_output: %s" % probe_output_path)
    print("- trace_output: %s" % trace_output_path)
    print("- project_path: %s" % project_path)
    print("- history_path: %s" % history_path)
    print("- dry_run: %s" % ("yes" if dry_run else "no"))
    print("- diagnose: %s" % ("yes" if diagnose else "no"))
    print("- allow_existing_history: %s" % ("yes" if allow_existing_history else "no"))
    print("- probe: %s" % ("yes" if probe else "no"))
    print("- trace_export: %s" % ("yes" if trace_export else "no"))
    print("- export_on_quit: %s" % ("yes" if export_on_quit else "no"))


def _probe_snapshot(path: Path) -> dict[str, object]:
    snapshot: dict[str, object] = {
        "path": str(path),
        "exists": path.exists(),
        "size_bytes": 0,
        "mtime_ns": 0,
    }
    if not path.exists():
        return snapshot
    try:
        stat_result = path.stat()
    except OSError:
        return snapshot
    snapshot["size_bytes"] = int(stat_result.st_size)
    snapshot["mtime_ns"] = int(stat_result.st_mtime_ns)
    return snapshot


def _trace_snapshot(path: Path) -> dict[str, object]:
    snapshot: dict[str, object] = {
        "path": str(path),
        "exists": path.exists(),
        "size_bytes": 0,
        "mtime_ns": 0,
    }
    if not path.exists():
        return snapshot
    try:
        stat_result = path.stat()
    except OSError:
        return snapshot
    snapshot["size_bytes"] = int(stat_result.st_size)
    snapshot["mtime_ns"] = int(stat_result.st_mtime_ns)
    return snapshot


def _read_probe_payload(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    try:
        raw_content = path.read_text(encoding="utf-8")
    except OSError as exc:
        print("Unable to read probe file: %s" % str(exc), file=sys.stderr)
        return None
    try:
        parsed = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        print("Probe file is not valid JSON: %s" % str(exc), file=sys.stderr)
        return None
    if not isinstance(parsed, dict):
        print("Probe file JSON must be an object.", file=sys.stderr)
        return None
    return parsed


def _read_trace_payload(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    try:
        raw_content = path.read_text(encoding="utf-8")
    except OSError as exc:
        print("Unable to read trace file: %s" % str(exc), file=sys.stderr)
        return None
    try:
        parsed = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        print("Trace file is not valid JSON: %s" % str(exc), file=sys.stderr)
        return None
    if not isinstance(parsed, dict):
        print("Trace file JSON must be an object.", file=sys.stderr)
        return None
    return parsed


def _print_probe_summary(probe_payload: dict[str, object]) -> None:
    print("Probe summary")
    print("- timestamp: %s" % _to_str(probe_payload.get("timestamp")))
    print("- seed: %s" % _to_str(probe_payload.get("seed")))
    print("- active_scene: %s" % _to_str(probe_payload.get("active_scene")))
    print("- game_loop_found: %s" % _to_str(probe_payload.get("game_loop_found")))
    print("- export_runtime_possible: %s" % _to_str(probe_payload.get("export_runtime_possible")))
    print(
        "- support_metrics_forced_objective: %s"
        % _to_str(probe_payload.get("support_metrics_forced_objective"))
    )
    print(
        "- support_metrics_forced_objective_enabled: %s"
        % _to_str(probe_payload.get("support_metrics_forced_objective_enabled"))
    )
    print(
        "- support_metrics_forced_objective_rejected: %s"
        % _to_str(probe_payload.get("support_metrics_forced_objective_rejected"))
    )
    print(
        "- support_metrics_forced_objective_reject_reason: %s"
        % _to_str(probe_payload.get("support_metrics_forced_objective_reject_reason"))
    )
    print("- history_path: %s" % _to_str(probe_payload.get("history_path")))
    print("- output_path: %s" % _to_str(probe_payload.get("output_path")))
    print("- note: %s" % _to_str(probe_payload.get("note")))


def _print_trace_summary(trace_payload: dict[str, object], expected_objective: str) -> None:
    objective_requested = _to_str(trace_payload.get("objective_requested"))
    objective_observed = _to_str(trace_payload.get("objective_observed"))
    if objective_observed == "":
        objective_observed = _to_str(trace_payload.get("objective_id"))
    missing_payload_fields = _to_lines(trace_payload.get("missing_payload_fields"))
    print("Export trace summary")
    print("- note: %s" % _to_str(trace_payload.get("note")))
    print("- active_scene: %s" % _to_str(trace_payload.get("active_scene")))
    print("- game_loop_found: %s" % _to_str(trace_payload.get("game_loop_found")))
    print("- export_on_quit_requested: %s" % _to_str(trace_payload.get("export_on_quit_requested")))
    print("- objective_requested: %s" % objective_requested)
    print("- objective_observed: %s" % objective_observed)
    print("- objective_id: %s" % _to_str(trace_payload.get("objective_id")))
    print(
        "- support_metrics_forced_objective: %s"
        % _to_str(trace_payload.get("support_metrics_forced_objective"))
    )
    print(
        "- support_metrics_forced_objective_enabled: %s"
        % _to_str(trace_payload.get("support_metrics_forced_objective_enabled"))
    )
    print(
        "- support_metrics_forced_objective_rejected: %s"
        % _to_str(trace_payload.get("support_metrics_forced_objective_rejected"))
    )
    print(
        "- support_metrics_forced_objective_reject_reason: %s"
        % _to_str(trace_payload.get("support_metrics_forced_objective_reject_reason"))
    )
    print("- history_path_resolved: %s" % _to_str(trace_payload.get("history_path_resolved")))
    print("- latest_export_path_resolved: %s" % _to_str(trace_payload.get("latest_export_path_resolved")))
    print("- export_function_reached: %s" % _to_str(trace_payload.get("export_function_reached")))
    print("- export_payload_built: %s" % _to_str(trace_payload.get("export_payload_built")))
    print("- export_trigger: %s" % _to_str(trace_payload.get("export_trigger")))
    print("- payload_has_support_gate: %s" % _to_str(trace_payload.get("payload_has_support_gate")))
    print("- payload_has_champion_support: %s" % _to_str(trace_payload.get("payload_has_champion_support")))
    print("- payload_has_champion_resolution: %s" % _to_str(trace_payload.get("payload_has_champion_resolution")))
    print(
        "- missing_payload_fields: %s"
        % (", ".join(missing_payload_fields) if missing_payload_fields else "none")
    )
    print("- latest_export_write_attempted: %s" % _to_str(trace_payload.get("latest_export_write_attempted")))
    print("- latest_export_write_success: %s" % _to_str(trace_payload.get("latest_export_write_success")))
    print("- history_append_attempted: %s" % _to_str(trace_payload.get("history_append_attempted")))
    print("- history_append_success: %s" % _to_str(trace_payload.get("history_append_success")))
    print("- reason_export_not_attempted: %s" % _to_str(trace_payload.get("reason_export_not_attempted")))
    print("- quit_after_received: %s" % _to_str(trace_payload.get("quit_after_received")))
    print("- tick_observed: %s" % _to_str(trace_payload.get("tick_observed")))
    print("- run_duration_observed: %s" % _to_str(trace_payload.get("run_duration_observed")))
    if (
        expected_objective != ""
        and objective_observed != ""
        and objective_observed != expected_objective
    ):
        print(
            (
                "Warning: objective mismatch in trace "
                "(requested=%s, observed=%s)."
            )
            % (expected_objective, objective_observed),
            file=sys.stderr,
        )
    elif objective_requested != "" and objective_observed != "" and objective_requested != objective_observed:
        print(
            (
                "Warning: objective mismatch in trace "
                "(requested=%s, observed=%s)."
            )
            % (objective_requested, objective_observed),
            file=sys.stderr,
        )


def _trace_file_changed(before_snapshot: dict[str, object], after_snapshot: dict[str, object]) -> bool:
    before_exists = _to_bool(before_snapshot.get("exists"))
    after_exists = _to_bool(after_snapshot.get("exists"))
    before_size = _to_int(before_snapshot.get("size_bytes"))
    after_size = _to_int(after_snapshot.get("size_bytes"))
    before_mtime = _to_int(before_snapshot.get("mtime_ns"))
    after_mtime = _to_int(after_snapshot.get("mtime_ns"))
    return (not before_exists and after_exists) or (before_size != after_size) or (before_mtime != after_mtime)


def _validate_and_print_trace_export(
    command: list[str],
    project_path: Path,
    history_path: Path,
    output_path: Path,
    trace_output_path: Path,
    before_snapshot: dict[str, object],
    diagnose: bool,
    objective: str,
) -> int:
    after_snapshot = _trace_snapshot(trace_output_path)
    if diagnose:
        print("- trace exists after: %s" % ("yes" if _to_bool(after_snapshot.get("exists")) else "no"))
        print("- trace size after: %d" % _to_int(after_snapshot.get("size_bytes")))
        print("- trace mtime after: %d" % _to_int(after_snapshot.get("mtime_ns")))

    if (not _to_bool(after_snapshot.get("exists"))) or (not _trace_file_changed(before_snapshot, after_snapshot)):
        print(
            _build_trace_missing_error(
                command=command,
                project_path=project_path,
                history_path=history_path,
                output_path=output_path,
                trace_output_path=trace_output_path,
            ),
            file=sys.stderr,
        )
        return 7

    trace_payload = _read_trace_payload(trace_output_path)
    if trace_payload is None:
        return 7
    _print_trace_summary(trace_payload, expected_objective=objective)
    return 0

def _collect_runtime_probe(
    command: list[str],
    project_path: Path,
    history_path: Path,
    output_path: Path,
    probe_output_path: Path,
    trace_output_path: Path,
    diagnose: bool,
    trace_export: bool,
    objective: str,
) -> int:
    seed_value = _extract_command_arg_value(command, "--support-metrics-seed")
    if seed_value == "":
        seed_value = "unknown"
    before_snapshot = _probe_snapshot(probe_output_path)
    trace_before_snapshot: dict[str, object] | None = None
    if trace_export:
        trace_before_snapshot = _trace_snapshot(trace_output_path)
    if diagnose:
        print("")
        print("DIAGNOSE probe")
        print("- seed: %s" % seed_value)
        print("- command: %s" % _format_command(command))
        print("- probe exists before: %s" % ("yes" if _to_bool(before_snapshot.get("exists")) else "no"))
        print("- probe size before: %d" % _to_int(before_snapshot.get("size_bytes")))
        print("- probe mtime before: %d" % _to_int(before_snapshot.get("mtime_ns")))
        if trace_export and trace_before_snapshot is not None:
            print("- trace exists before: %s" % ("yes" if _to_bool(trace_before_snapshot.get("exists")) else "no"))
            print("- trace size before: %d" % _to_int(trace_before_snapshot.get("size_bytes")))
            print("- trace mtime before: %d" % _to_int(trace_before_snapshot.get("mtime_ns")))

    print("Probe run (seed=%s): %s" % (seed_value, _format_command(command)))
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
            "Godot probe run failed for seed %s with return code %d."
            % (seed_value, result.returncode),
            file=sys.stderr,
        )
        return 3

    after_snapshot = _probe_snapshot(probe_output_path)
    if diagnose:
        print("- probe exists after: %s" % ("yes" if _to_bool(after_snapshot.get("exists")) else "no"))
        print("- probe size after: %d" % _to_int(after_snapshot.get("size_bytes")))
        print("- probe mtime after: %d" % _to_int(after_snapshot.get("mtime_ns")))

    before_exists = _to_bool(before_snapshot.get("exists"))
    after_exists = _to_bool(after_snapshot.get("exists"))
    before_size = _to_int(before_snapshot.get("size_bytes"))
    after_size = _to_int(after_snapshot.get("size_bytes"))
    before_mtime = _to_int(before_snapshot.get("mtime_ns"))
    after_mtime = _to_int(after_snapshot.get("mtime_ns"))
    changed = (not before_exists and after_exists) or (before_size != after_size) or (before_mtime != after_mtime)
    if (not after_exists) or (not changed):
        print(
            _build_probe_missing_error(
                command=command,
                project_path=project_path,
                history_path=history_path,
                output_path=output_path,
                probe_output_path=probe_output_path,
            ),
            file=sys.stderr,
        )
        return 6

    probe_payload = _read_probe_payload(probe_output_path)
    if probe_payload is None:
        return 6
    _print_probe_summary(probe_payload)
    if trace_export and trace_before_snapshot is not None:
        trace_status = _validate_and_print_trace_export(
            command=command,
            project_path=project_path,
            history_path=history_path,
            output_path=output_path,
            trace_output_path=trace_output_path,
            before_snapshot=trace_before_snapshot,
            diagnose=diagnose,
            objective=objective,
        )
        if trace_status != 0:
            return trace_status
    return 0


def _collect_runtime_entries(
    commands: list[list[str]],
    project_path: Path,
    history_path: Path,
    output_path: Path,
    trace_output_path: Path,
    diagnose: bool,
    allow_existing_history: bool,
    trace_export: bool,
    objective: str,
) -> tuple[int, list[str]]:
    collected: list[str] = []

    for run_index, command in enumerate(commands, start=1):
        seed_value = _extract_command_arg_value(command, "--support-metrics-seed")
        if seed_value == "":
            seed_value = "unknown"
        before_snapshot = _history_snapshot(history_path)
        before_lines = _to_lines(before_snapshot.get("lines"))
        trace_before_snapshot: dict[str, object] | None = None
        if trace_export:
            trace_before_snapshot = _trace_snapshot(trace_output_path)

        if diagnose:
            print("")
            print("DIAGNOSE run %d/%d" % (run_index, len(commands)))
            print("- seed: %s" % seed_value)
            print("- command: %s" % _format_command(command))
            _print_snapshot("- before", before_snapshot)
            if trace_export and trace_before_snapshot is not None:
                print("- trace exists before: %s" % ("yes" if _to_bool(trace_before_snapshot.get("exists")) else "no"))
                print("- trace size before: %d" % _to_int(trace_before_snapshot.get("size_bytes")))
                print("- trace mtime before: %d" % _to_int(trace_before_snapshot.get("mtime_ns")))

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

        if trace_export and trace_before_snapshot is not None:
            trace_status = _validate_and_print_trace_export(
                command=command,
                project_path=project_path,
                history_path=history_path,
                output_path=output_path,
                trace_output_path=trace_output_path,
                before_snapshot=trace_before_snapshot,
                diagnose=diagnose,
                objective=objective,
            )
            if trace_status != 0:
                return trace_status, collected

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
    objective = _normalize_objective(args.objective)
    _warn_unknown_objective(objective)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    probe_output_path = DEFAULT_PROBE_OUTPUT_PATH
    probe_output_path.parent.mkdir(parents=True, exist_ok=True)
    trace_output_path = DEFAULT_TRACE_OUTPUT_PATH
    trace_output_path.parent.mkdir(parents=True, exist_ok=True)
    history_path = _resolve_history_path(project_path, args.history_path)

    _print_configuration(
        mode=args.mode,
        runs=args.runs,
        seed_start=args.seed_start,
        objective=objective,
        output_path=output_path,
        probe_output_path=probe_output_path,
        trace_output_path=trace_output_path,
        project_path=project_path,
        history_path=history_path,
        dry_run=bool(args.dry_run),
        diagnose=bool(args.diagnose),
        allow_existing_history=bool(args.allow_existing_history),
        probe=bool(args.probe),
        trace_export=bool(args.trace_export),
        export_on_quit=bool(args.export_on_quit),
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
                history_path=history_path,
                output_path=output_path,
                probe_output_path=probe_output_path,
                trace_output_path=trace_output_path,
                objective=objective,
                probe=bool(args.probe),
                trace_export=bool(args.trace_export),
                export_on_quit=bool(args.export_on_quit),
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
            print("- probe_output_path: %s" % probe_output_path)
            print("- trace_output_path: %s" % trace_output_path)
            print("- objective: %s" % (objective if objective != "" else "(default)"))
            print("- export_on_quit: %s" % ("yes" if args.export_on_quit else "no"))
            for run_index, command in enumerate(commands, start=1):
                print(
                    "- seed[%d]: %s"
                    % (run_index, _extract_command_arg_value(command, "--support-metrics-seed"))
                )
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

    if args.probe:
        return _collect_runtime_probe(
            command=commands_with_resolved_bin[0],
            project_path=project_path,
            history_path=history_path,
            output_path=output_path,
            probe_output_path=probe_output_path,
            trace_output_path=trace_output_path,
            diagnose=bool(args.diagnose),
            trace_export=bool(args.trace_export),
            objective=objective,
        )

    collect_status, collected_lines = _collect_runtime_entries(
        commands=commands_with_resolved_bin,
        project_path=project_path,
        history_path=history_path,
        output_path=output_path,
        trace_output_path=trace_output_path,
        diagnose=bool(args.diagnose),
        allow_existing_history=bool(args.allow_existing_history),
        trace_export=bool(args.trace_export),
        objective=objective,
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

