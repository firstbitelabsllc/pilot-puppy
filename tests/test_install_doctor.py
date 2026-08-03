from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "bin" / "pilot-puppy"
DOCTOR = ROOT / "scripts" / "pilot-puppy-doctor.py"


class DoctorTests(unittest.TestCase):
    def run_doctor(self, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(CLI), "doctor", *args],
            cwd=ROOT,
            env={**os.environ, **(env or {})},
            capture_output=True,
            text=True,
            check=False,
        )

    def test_json_report_has_one_product_and_native_host_floor(self) -> None:
        result = self.run_doctor("--json")
        report = json.loads(result.stdout)
        self.assertEqual(report["schema"], "pilot-puppy.doctor.v1")
        self.assertEqual(report["product"], "Pilot Puppy")
        self.assertEqual(result.returncode, 0 if report["ok"] else 1)
        names = {item["name"] for item in report["checks"]}
        self.assertIn("product identity", names)
        self.assertIn("native host floor", names)
        self.assertIn("skill mount: .agents", names)
        self.assertNotIn("skill mount: .codex", names)
        self.assertNotIn("token permissions", names)
        self.assertNotIn("background process", names)

    def test_bad_root_fails_identity_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as dirname:
            result = subprocess.run(
                ["python3", str(DOCTOR), "--json"],
                cwd=ROOT,
                env={**os.environ, "PILOT_PUPPY_ROOT": dirname},
                capture_output=True,
                text=True,
                check=False,
            )
        report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(report["ok"])
        self.assertNotIn("Traceback", result.stderr)

    def test_bad_cli_root_does_not_echo_private_path(self) -> None:
        with tempfile.TemporaryDirectory() as dirname:
            result = subprocess.run(
                [str(CLI), "status", "--json"],
                cwd=ROOT,
                env={**os.environ, "PILOT_PUPPY_ROOT": dirname},
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 127)
        self.assertIn("PILOT_PUPPY_ROOT does not look like a pilot-puppy checkout", result.stderr)
        self.assertNotIn(dirname, result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_malformed_metadata_fails_without_private_details(self) -> None:
        with tempfile.TemporaryDirectory() as dirname:
            root = Path(dirname)
            (root / "package.json").write_text("[]\n", encoding="utf-8")
            (root / ".claude-plugin").mkdir()
            (root / ".claude-plugin" / "plugin.json").write_text("{}\n", encoding="utf-8")
            (root / "VERSION").write_text("2.1.0\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(DOCTOR), "--json"],
                cwd=ROOT,
                env={**os.environ, "PILOT_PUPPY_ROOT": str(root)},
                capture_output=True,
                text=True,
                check=False,
            )
        report = json.loads(result.stdout)
        identity = next(item for item in report["checks"] if item["name"] == "product identity")
        self.assertEqual(identity["detail"], "metadata is unreadable")
        self.assertNotIn("object has no attribute", json.dumps(identity))
        self.assertNotIn("Traceback", result.stderr)

    def test_text_output_is_human_readable(self) -> None:
        result = self.run_doctor()
        self.assertIn("[PASS] product identity", result.stdout)
        self.assertIn("checks without hard failure", result.stdout)


if __name__ == "__main__":
    unittest.main()
