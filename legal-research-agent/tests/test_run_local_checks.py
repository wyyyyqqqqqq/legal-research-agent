#!/usr/bin/env python3
"""Unit tests for the local preflight runner."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "scripts" / "run-local-checks.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("run_local_checks", RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load run-local-checks.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RUNNER = load_runner()


class Completed:
    def __init__(self, returncode: int = 0, stdout: str = "ok", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class RunLocalChecksTest(unittest.TestCase):
    def test_check_ids_are_unique(self) -> None:
        ids = [check["id"] for check in RUNNER.CHECKS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_run_preflight_passes_when_all_commands_pass(self) -> None:
        with mock.patch.object(RUNNER.subprocess, "run", return_value=Completed()):
            result = RUNNER.run_preflight(ROOT)
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["total"], len(RUNNER.CHECKS))

    def test_stop_on_failure_stops_after_first_failure(self) -> None:
        calls = [Completed(returncode=1, stderr="boom"), Completed()]
        with mock.patch.object(RUNNER.subprocess, "run", side_effect=calls):
            result = RUNNER.run_preflight(ROOT, stop_on_failure=True)
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["failed"], 1)

    def test_write_report_creates_json_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = Path(temp_dir) / "nested" / "report.json"
            RUNNER.write_report(report_path, {"status": "pass"})
            self.assertTrue(report_path.exists())
            self.assertIn('"status": "pass"', report_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
