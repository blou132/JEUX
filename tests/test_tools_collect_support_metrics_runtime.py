from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "collect_support_metrics_runtime.py"


def _run_tool(
    extra_args: list[str],
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(SCRIPT)]
    command.extend(extra_args)
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        env=merged_env,
    )


class CollectSupportMetricsRuntimeToolTests(unittest.TestCase):
    def _write_stub_godot_launcher(self, tmpdir: str) -> Path:
        launcher_path = Path(tmpdir) / ("stub_godot.cmd" if os.name == "nt" else "stub_godot.sh")
        if os.name == "nt":
            launcher_path.write_text(
                "\n".join(
                    [
                        "@echo off",
                        "setlocal",
                        "if \"%STUB_APPEND_HISTORY%\"==\"1\" (",
                        "  >> \"%STUB_HISTORY_PATH%\" echo {\"export_id\":\"stub_%SUPPORT_METRICS_SEED%\",\"objective_id\":\"support_gate\",\"run_status\":\"completed\",\"objective_status\":\"completed\",\"support_gate_run_attempts\":1,\"support_gate_run_success\":1,\"support_gate_run_success_rate\":1.0,\"support_gate_run_available_ratio\":1.0}",
                        ")",
                        "if \"%STUB_WRITE_PROBE%\"==\"1\" (",
                        "  for %%I in (\"%STUB_PROBE_PATH%\") do if not exist \"%%~dpI\" mkdir \"%%~dpI\"",
                        "  > \"%STUB_PROBE_PATH%\" echo {\"timestamp\":\"stub\",\"user_args\":[\"--support-metrics-probe\"],\"project_path\":\"stub_project\",\"history_path\":\"stub_history\",\"output_path\":\"stub_output\",\"seed\":\"%SUPPORT_METRICS_SEED%\",\"active_scene\":\"MainSandbox\",\"game_loop_found\":\"yes\",\"export_runtime_possible\":\"yes\",\"note\":\"probe only, not gameplay metrics\"}",
                        ")",
                        "if \"%STUB_WRITE_TRACE%\"==\"1\" (",
                        "  for %%I in (\"%STUB_TRACE_PATH%\") do if not exist \"%%~dpI\" mkdir \"%%~dpI\"",
                        "  > \"%STUB_TRACE_PATH%\" echo {\"note\":\"debug only, not gameplay metrics\",\"args_received\":[\"--support-metrics-trace-export\"],\"active_scene\":\"MainSandbox\",\"game_loop_found\":\"yes\",\"objective_id\":\"observe_dominance\",\"history_path_resolved\":\"stub_history\",\"latest_export_path_resolved\":\"stub_latest\",\"export_function_reached\":\"yes\",\"export_payload_built\":\"yes\",\"history_append_attempted\":\"yes\",\"history_append_success\":\"yes\",\"latest_export_write_attempted\":\"yes\",\"latest_export_write_success\":\"yes\",\"reason_export_not_attempted\":\"\",\"quit_after_received\":\"4200\",\"tick_observed\":42,\"run_duration_observed\":12.5}",
                        ")",
                        "exit /b 0",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
        else:
            launcher_path.write_text(
                "\n".join(
                    [
                        "#!/usr/bin/env bash",
                        "set -euo pipefail",
                        "if [ \"${STUB_APPEND_HISTORY:-0}\" = \"1\" ]; then",
                        "  echo '{\"export_id\":\"stub_'\"${SUPPORT_METRICS_SEED:-0}\"'\",\"objective_id\":\"support_gate\",\"run_status\":\"completed\",\"objective_status\":\"completed\",\"support_gate_run_attempts\":1,\"support_gate_run_success\":1,\"support_gate_run_success_rate\":1.0,\"support_gate_run_available_ratio\":1.0}' >> \"${STUB_HISTORY_PATH}\"",
                        "fi",
                        "if [ \"${STUB_WRITE_PROBE:-0}\" = \"1\" ]; then",
                        "  mkdir -p \"$(dirname \"${STUB_PROBE_PATH}\")\"",
                        "  echo '{\"timestamp\":\"stub\",\"user_args\":[\"--support-metrics-probe\"],\"project_path\":\"stub_project\",\"history_path\":\"stub_history\",\"output_path\":\"stub_output\",\"seed\":\"'\"${SUPPORT_METRICS_SEED:-0}\"'\",\"active_scene\":\"MainSandbox\",\"game_loop_found\":\"yes\",\"export_runtime_possible\":\"yes\",\"note\":\"probe only, not gameplay metrics\"}' > \"${STUB_PROBE_PATH}\"",
                        "fi",
                        "if [ \"${STUB_WRITE_TRACE:-0}\" = \"1\" ]; then",
                        "  mkdir -p \"$(dirname \"${STUB_TRACE_PATH}\")\"",
                        "  echo '{\"note\":\"debug only, not gameplay metrics\",\"args_received\":[\"--support-metrics-trace-export\"],\"active_scene\":\"MainSandbox\",\"game_loop_found\":\"yes\",\"objective_id\":\"observe_dominance\",\"history_path_resolved\":\"stub_history\",\"latest_export_path_resolved\":\"stub_latest\",\"export_function_reached\":\"yes\",\"export_payload_built\":\"yes\",\"history_append_attempted\":\"yes\",\"history_append_success\":\"yes\",\"latest_export_write_attempted\":\"yes\",\"latest_export_write_success\":\"yes\",\"reason_export_not_attempted\":\"\",\"quit_after_received\":\"4200\",\"tick_observed\":42,\"run_duration_observed\":12.5}' > \"${STUB_TRACE_PATH}\"",
                        "fi",
                        "exit 0",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            launcher_path.chmod(0o755)
        return launcher_path

    def test_help_exposes_expected_options(self) -> None:
        result = _run_tool(["--help"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("--mode", result.stdout)
        self.assertIn("--runs", result.stdout)
        self.assertIn("--seed-start", result.stdout)
        self.assertIn("--output", result.stdout)
        self.assertIn("--godot-bin", result.stdout)
        self.assertIn("--dry-run", result.stdout)
        self.assertIn("--project-path", result.stdout)
        self.assertIn("--history-path", result.stdout)
        self.assertIn("--diagnose", result.stdout)
        self.assertIn("--allow-existing-history", result.stdout)
        self.assertIn("--probe", result.stdout)
        self.assertIn("--trace-export", result.stdout)

    def test_godot_absent_returns_non_zero_and_clear_message(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "outputs" / "ci" / "support_metrics_current.jsonl"
            result = _run_tool(
                [
                    "--mode",
                    "current",
                    "--runs",
                    "1",
                    "--seed-start",
                    "1000",
                    "--output",
                    str(output_path),
                    "--godot-bin",
                    "__missing_godot_binary_for_collect_runtime_tests__",
                ]
            )
            self.assertNotEqual(result.returncode, 0)
            merged_output = result.stdout + "\n" + result.stderr
            self.assertIn("Godot binary not found", merged_output)
            self.assertTrue(output_path.parent.exists())

    def test_dry_run_succeeds_without_godot(self) -> None:
        result = _run_tool(
            [
                "--mode",
                "baseline",
                "--runs",
                "2",
                "--seed-start",
                "2000",
                "--godot-bin",
                "__missing_godot_binary_for_collect_runtime_tests__",
                "--dry-run",
            ]
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("DRY-RUN: planned commands", result.stdout)
        self.assertIn("--support-metrics-seed 2000", result.stdout)
        self.assertIn("--support-metrics-seed 2001", result.stdout)

    def test_diagnose_dry_run_succeeds_without_godot(self) -> None:
        result = _run_tool(
            [
                "--mode",
                "current",
                "--runs",
                "1",
                "--seed-start",
                "1000",
                "--godot-bin",
                "__missing_godot_binary_for_collect_runtime_tests__",
                "--dry-run",
                "--diagnose",
            ]
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("DIAGNOSE dry-run context", result.stdout)
        self.assertIn("history_path", result.stdout)
        self.assertIn("command[1]", result.stdout)

    def test_probe_dry_run_shows_probe_command(self) -> None:
        result = _run_tool(
            [
                "--mode",
                "current",
                "--runs",
                "1",
                "--seed-start",
                "1000",
                "--godot-bin",
                "__missing_godot_binary_for_collect_runtime_tests__",
                "--dry-run",
                "--probe",
            ]
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("--support-metrics-probe", result.stdout)
        self.assertIn("--support-metrics-probe-output", result.stdout)

    def test_trace_export_dry_run_shows_trace_command(self) -> None:
        result = _run_tool(
            [
                "--mode",
                "current",
                "--runs",
                "1",
                "--seed-start",
                "1000",
                "--godot-bin",
                "__missing_godot_binary_for_collect_runtime_tests__",
                "--dry-run",
                "--trace-export",
            ]
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("--support-metrics-trace-export", result.stdout)
        self.assertIn("--support-metrics-trace-output", result.stdout)

    def test_probe_without_probe_file_returns_clear_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            launcher_path = self._write_stub_godot_launcher(tmpdir)
            history_path = Path(tmpdir) / "run_metrics_history.jsonl"
            history_path.write_text(
                '{"export_id":"old_1","objective_id":"support_gate"}\n',
                encoding="utf-8",
            )
            output_path = Path(tmpdir) / "outputs" / "ci" / "support_metrics_current.jsonl"
            probe_path = ROOT / "outputs" / "ci" / "support_metrics_runtime_probe.json"
            if probe_path.exists():
                probe_path.unlink()
            result = _run_tool(
                [
                    "--mode",
                    "current",
                    "--runs",
                    "1",
                    "--seed-start",
                    "1000",
                    "--output",
                    str(output_path),
                    "--godot-bin",
                    str(launcher_path),
                    "--history-path",
                    str(history_path),
                    "--probe",
                ],
                env={
                    "STUB_APPEND_HISTORY": "0",
                    "STUB_WRITE_PROBE": "0",
                    "STUB_HISTORY_PATH": str(history_path),
                    "STUB_OUTPUT_PATH": str(output_path),
                    "STUB_PROBE_PATH": str(probe_path),
                },
            )
            self.assertNotEqual(result.returncode, 0)
            combined = result.stdout + "\n" + result.stderr
            self.assertIn(
                "Godot launched, but project did not execute support metrics probe.",
                combined,
            )

    def test_probe_with_simulated_probe_file_returns_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            launcher_path = self._write_stub_godot_launcher(tmpdir)
            history_path = Path(tmpdir) / "run_metrics_history.jsonl"
            history_path.write_text(
                '{"export_id":"old_1","objective_id":"support_gate"}\n',
                encoding="utf-8",
            )
            output_path = Path(tmpdir) / "outputs" / "ci" / "support_metrics_current.jsonl"
            probe_path = ROOT / "outputs" / "ci" / "support_metrics_runtime_probe.json"
            if probe_path.exists():
                probe_path.unlink()
            result = _run_tool(
                [
                    "--mode",
                    "current",
                    "--runs",
                    "1",
                    "--seed-start",
                    "1000",
                    "--output",
                    str(output_path),
                    "--godot-bin",
                    str(launcher_path),
                    "--history-path",
                    str(history_path),
                    "--probe",
                ],
                env={
                    "STUB_APPEND_HISTORY": "0",
                    "STUB_WRITE_PROBE": "1",
                    "STUB_HISTORY_PATH": str(history_path),
                    "STUB_OUTPUT_PATH": str(output_path),
                    "STUB_PROBE_PATH": str(probe_path),
                },
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertIn("Probe summary", result.stdout)
            self.assertIn("game_loop_found: yes", result.stdout)
            self.assertIn("probe only, not gameplay metrics", result.stdout)

    def test_probe_does_not_modify_history_when_stub_does_not_append(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            launcher_path = self._write_stub_godot_launcher(tmpdir)
            history_path = Path(tmpdir) / "run_metrics_history.jsonl"
            original_history = '{"export_id":"old_1","objective_id":"support_gate"}\n'
            history_path.write_text(original_history, encoding="utf-8")
            output_path = Path(tmpdir) / "outputs" / "ci" / "support_metrics_current.jsonl"
            probe_path = ROOT / "outputs" / "ci" / "support_metrics_runtime_probe.json"
            if probe_path.exists():
                probe_path.unlink()
            result = _run_tool(
                [
                    "--mode",
                    "current",
                    "--runs",
                    "1",
                    "--seed-start",
                    "1000",
                    "--output",
                    str(output_path),
                    "--godot-bin",
                    str(launcher_path),
                    "--history-path",
                    str(history_path),
                    "--probe",
                ],
                env={
                    "STUB_APPEND_HISTORY": "0",
                    "STUB_WRITE_PROBE": "1",
                    "STUB_HISTORY_PATH": str(history_path),
                    "STUB_OUTPUT_PATH": str(output_path),
                    "STUB_PROBE_PATH": str(probe_path),
                },
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertEqual(history_path.read_text(encoding="utf-8"), original_history)

    def test_trace_export_without_trace_file_returns_clear_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            launcher_path = self._write_stub_godot_launcher(tmpdir)
            history_path = Path(tmpdir) / "run_metrics_history.jsonl"
            history_path.write_text(
                '{"export_id":"old_1","objective_id":"support_gate"}\n',
                encoding="utf-8",
            )
            output_path = Path(tmpdir) / "outputs" / "ci" / "support_metrics_current.jsonl"
            trace_path = ROOT / "outputs" / "ci" / "support_metrics_runtime_export_trace.json"
            if trace_path.exists():
                trace_path.unlink()

            result = _run_tool(
                [
                    "--mode",
                    "current",
                    "--runs",
                    "1",
                    "--seed-start",
                    "1000",
                    "--output",
                    str(output_path),
                    "--godot-bin",
                    str(launcher_path),
                    "--history-path",
                    str(history_path),
                    "--trace-export",
                ],
                env={
                    "STUB_APPEND_HISTORY": "1",
                    "STUB_WRITE_TRACE": "0",
                    "STUB_HISTORY_PATH": str(history_path),
                    "STUB_TRACE_PATH": str(trace_path),
                },
            )
            self.assertNotEqual(result.returncode, 0)
            combined = result.stdout + "\n" + result.stderr
            self.assertIn(
                "Godot launched, probe works, but export trace was not produced.",
                combined,
            )

    def test_trace_export_with_simulated_trace_file_returns_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            launcher_path = self._write_stub_godot_launcher(tmpdir)
            history_path = Path(tmpdir) / "run_metrics_history.jsonl"
            output_path = Path(tmpdir) / "outputs" / "ci" / "support_metrics_current.jsonl"
            trace_path = ROOT / "outputs" / "ci" / "support_metrics_runtime_export_trace.json"
            if trace_path.exists():
                trace_path.unlink()

            result = _run_tool(
                [
                    "--mode",
                    "current",
                    "--runs",
                    "1",
                    "--seed-start",
                    "1000",
                    "--output",
                    str(output_path),
                    "--godot-bin",
                    str(launcher_path),
                    "--history-path",
                    str(history_path),
                    "--trace-export",
                ],
                env={
                    "STUB_APPEND_HISTORY": "1",
                    "STUB_WRITE_TRACE": "1",
                    "STUB_HISTORY_PATH": str(history_path),
                    "STUB_TRACE_PATH": str(trace_path),
                },
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertIn("Export trace summary", result.stdout)
            self.assertIn("export_function_reached: yes", result.stdout)
            self.assertIn("history_append_success: yes", result.stdout)

    def test_trace_export_does_not_replace_history_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            launcher_path = self._write_stub_godot_launcher(tmpdir)
            history_path = Path(tmpdir) / "run_metrics_history.jsonl"
            history_path.write_text(
                '{"export_id":"old_1","objective_id":"support_gate"}\n',
                encoding="utf-8",
            )
            output_path = Path(tmpdir) / "outputs" / "ci" / "support_metrics_current.jsonl"
            trace_path = ROOT / "outputs" / "ci" / "support_metrics_runtime_export_trace.json"
            if trace_path.exists():
                trace_path.unlink()

            result = _run_tool(
                [
                    "--mode",
                    "current",
                    "--runs",
                    "1",
                    "--seed-start",
                    "1000",
                    "--output",
                    str(output_path),
                    "--godot-bin",
                    str(launcher_path),
                    "--history-path",
                    str(history_path),
                    "--trace-export",
                ],
                env={
                    "STUB_APPEND_HISTORY": "0",
                    "STUB_WRITE_TRACE": "1",
                    "STUB_HISTORY_PATH": str(history_path),
                    "STUB_TRACE_PATH": str(trace_path),
                },
            )
            self.assertNotEqual(result.returncode, 0)
            combined = result.stdout + "\n" + result.stderr
            self.assertIn("Export trace summary", combined)
            self.assertIn("No new run metrics were exported after seed 1000.", combined)

    def test_mode_baseline_uses_expected_default_output_path(self) -> None:
        result = _run_tool(
            [
                "--mode",
                "baseline",
                "--runs",
                "1",
                "--godot-bin",
                "__missing_godot_binary_for_collect_runtime_tests__",
                "--dry-run",
            ]
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        normalized_output = result.stdout.replace("\\", "/")
        self.assertIn("outputs/ci/support_metrics_baseline.jsonl", normalized_output)

    def test_mode_current_uses_expected_default_output_path(self) -> None:
        result = _run_tool(
            [
                "--mode",
                "current",
                "--runs",
                "1",
                "--godot-bin",
                "__missing_godot_binary_for_collect_runtime_tests__",
                "--dry-run",
            ]
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        normalized_output = result.stdout.replace("\\", "/")
        self.assertIn("outputs/ci/support_metrics_current.jsonl", normalized_output)

    def test_output_directory_is_created_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "nested" / "ci" / "runtime_metrics.jsonl"
            self.assertFalse(output_path.parent.exists())
            result = _run_tool(
                [
                    "--mode",
                    "current",
                    "--runs",
                    "1",
                    "--output",
                    str(output_path),
                    "--godot-bin",
                    "__missing_godot_binary_for_collect_runtime_tests__",
                    "--dry-run",
                ]
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(output_path.parent.exists())

    def test_history_absent_returns_enriched_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            launcher_path = self._write_stub_godot_launcher(tmpdir)
            history_path = Path(tmpdir) / "missing_history.jsonl"
            output_path = Path(tmpdir) / "outputs" / "ci" / "support_metrics_current.jsonl"
            result = _run_tool(
                [
                    "--mode",
                    "current",
                    "--runs",
                    "1",
                    "--seed-start",
                    "1000",
                    "--output",
                    str(output_path),
                    "--godot-bin",
                    str(launcher_path),
                    "--history-path",
                    str(history_path),
                    "--diagnose",
                ],
                env={
                    "STUB_APPEND_HISTORY": "0",
                    "STUB_HISTORY_PATH": str(history_path),
                },
            )
            self.assertNotEqual(result.returncode, 0)
            combined = result.stdout + "\n" + result.stderr
            self.assertIn("history file found (before): no", combined)
            self.assertIn("history line count before: 0", combined)
            self.assertIn("history line count after: 0", combined)
            self.assertIn("possible causes:", combined)

    def test_history_unchanged_returns_enriched_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            launcher_path = self._write_stub_godot_launcher(tmpdir)
            history_path = Path(tmpdir) / "run_metrics_history.jsonl"
            history_path.write_text(
                '{"export_id":"old_1","objective_id":"support_gate"}\n',
                encoding="utf-8",
            )
            output_path = Path(tmpdir) / "outputs" / "ci" / "support_metrics_current.jsonl"
            result = _run_tool(
                [
                    "--mode",
                    "current",
                    "--runs",
                    "1",
                    "--seed-start",
                    "1000",
                    "--output",
                    str(output_path),
                    "--godot-bin",
                    str(launcher_path),
                    "--history-path",
                    str(history_path),
                ],
                env={
                    "STUB_APPEND_HISTORY": "0",
                    "STUB_HISTORY_PATH": str(history_path),
                },
            )
            self.assertNotEqual(result.returncode, 0)
            combined = result.stdout + "\n" + result.stderr
            self.assertIn("No new run metrics were exported after seed 1000.", combined)
            self.assertIn("Godot launched: yes", combined)
            self.assertIn("history line count before: 1", combined)
            self.assertIn("history line count after: 1", combined)
            self.assertIn("expected new lines: > 0", combined)

    def test_history_with_new_lines_collects_successfully(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            launcher_path = self._write_stub_godot_launcher(tmpdir)
            history_path = Path(tmpdir) / "run_metrics_history.jsonl"
            output_path = Path(tmpdir) / "outputs" / "ci" / "support_metrics_current.jsonl"

            result = _run_tool(
                [
                    "--mode",
                    "current",
                    "--runs",
                    "2",
                    "--seed-start",
                    "3000",
                    "--output",
                    str(output_path),
                    "--godot-bin",
                    str(launcher_path),
                    "--history-path",
                    str(history_path),
                ],
                env={
                    "STUB_APPEND_HISTORY": "1",
                    "STUB_HISTORY_PATH": str(history_path),
                },
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(output_path.exists())
            lines = output_path.read_text(encoding="utf-8").splitlines()
            non_empty_lines = [line for line in lines if line.strip()]
            self.assertEqual(len(non_empty_lines), 2)
            self.assertIn("stub_3000", non_empty_lines[0])
            self.assertIn("stub_3001", non_empty_lines[1])

    def test_allow_existing_history_reuses_lines_when_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            launcher_path = self._write_stub_godot_launcher(tmpdir)
            history_path = Path(tmpdir) / "run_metrics_history.jsonl"
            history_path.write_text(
                '{"export_id":"old_1","objective_id":"support_gate"}\n',
                encoding="utf-8",
            )
            output_path = Path(tmpdir) / "outputs" / "ci" / "support_metrics_current.jsonl"

            result = _run_tool(
                [
                    "--mode",
                    "current",
                    "--runs",
                    "1",
                    "--seed-start",
                    "1000",
                    "--output",
                    str(output_path),
                    "--godot-bin",
                    str(launcher_path),
                    "--history-path",
                    str(history_path),
                    "--allow-existing-history",
                ],
                env={
                    "STUB_APPEND_HISTORY": "0",
                    "STUB_HISTORY_PATH": str(history_path),
                },
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("old_1", content)
            self.assertIn("reused existing history line", result.stdout)


if __name__ == "__main__":
    unittest.main()
