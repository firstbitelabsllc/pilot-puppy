from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from benchmarks.harness import run as harness


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "benchmarks" / "harness" / "fixtures"


class BenchmarkHarnessTests(unittest.TestCase):
    def test_sealed_fixture_manifest_is_strict(self) -> None:
        manifest = harness.load_manifest(FIXTURES)
        self.assertEqual(manifest["schema"], "vidux-benchmark-fixtures.v1")
        self.assertEqual(
            {case["id"] for case in manifest["cases"]},
            harness.REQUIRED_CASES,
        )

    def test_runner_is_repeatable_and_covers_protected_surfaces(self) -> None:
        first = harness.run_benchmark(FIXTURES)
        second = harness.run_benchmark(FIXTURES)

        self.assertEqual(first["canonical_digest"], second["canonical_digest"])
        metrics = first["metrics"]
        self.assertTrue(metrics["health_ok"])
        self.assertEqual(metrics["plan_count"], 6)
        self.assertEqual(metrics["priority"]["selected_priority"], 90)
        self.assertEqual(metrics["priority"]["authority_state"], "ranked")
        self.assertEqual(metrics["proof_targets"]["selected_evidence"], "available")
        self.assertEqual(
            metrics["proof_targets"]["selected_scorecard"],
            {"Proof missing": "missing", "Proof present": "available"},
        )
        self.assertGreaterEqual(metrics["redaction"]["redaction_count"], 1)
        self.assertTrue(metrics["redaction"]["file_marker_present"])
        self.assertTrue(metrics["path_escape"]["rejected"])
        self.assertEqual(metrics["path_escape"]["relative_status"], 403)
        self.assertNotEqual(metrics["path_escape"]["symlink_file_status"], 200)
        self.assertEqual(metrics["path_escape"]["symlink_ledger_status"], 403)
        self.assertEqual(metrics["path_escape"]["symlink_coordination_status"], 403)
        self.assertGreaterEqual(metrics["ledger"]["checkpoint_rows"], 1)
        self.assertTrue(metrics["resume"]["checkpoint_present"])
        self.assertTrue(metrics["resume"]["resume_present"])

    def test_cli_emits_a_versioned_json_receipt(self) -> None:
        result = subprocess.run(
            ["python3", str(ROOT / "benchmarks" / "harness" / "run.py")],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
        receipt = json.loads(result.stdout)
        self.assertEqual(receipt["schema"], "vidux-benchmark-receipt.v1")
        self.assertRegex(receipt["canonical_digest"], r"^[0-9a-f]{64}$")
        self.assertRegex(receipt["fixture_digest"], r"^[0-9a-f]{64}$")

    def test_secret_fixture_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            copy = Path(temp) / "fixtures"
            shutil.copytree(FIXTURES, copy)
            target = copy / "durable" / "PLAN.md"
            target.write_text(
                target.read_text(encoding="utf-8") + "\npassword=not-a-fixture-secret\n",
                encoding="utf-8",
            )
            with self.assertRaises(harness.BenchmarkError):
                harness.load_manifest(copy)

    def test_secret_marker_cannot_hide_extra_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            copy = Path(temp) / "fixtures"
            shutil.copytree(FIXTURES, copy)
            target = copy / "durable" / "PLAN.md"
            target.write_text(
                target.read_text(encoding="utf-8").replace(
                    "API_TOKEN=__BENCHMARK_SECRET__",
                    "API_TOKEN=__BENCHMARK_SECRET__ password=not-a-fixture-secret",
                ),
                encoding="utf-8",
            )
            with self.assertRaises(harness.BenchmarkError):
                harness.load_manifest(copy)

    def test_fixture_hash_seal_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            copy = Path(temp) / "fixtures"
            shutil.copytree(FIXTURES, copy)
            target = copy / "priority-low" / "PLAN.md"
            target.write_text(
                target.read_text(encoding="utf-8").replace(
                    "Remain behind the high-priority synthetic goal.",
                    "Mutated after the fixture was sealed.",
                ),
                encoding="utf-8",
            )
            with self.assertRaises(harness.BenchmarkError):
                harness.load_manifest(copy)

    def test_manifest_path_escape_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            copy = Path(temp) / "fixtures"
            shutil.copytree(FIXTURES, copy)
            manifest_path = copy / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["cases"][0]["path"] = "../PLAN.md"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(harness.BenchmarkError):
                harness.load_manifest(copy)


if __name__ == "__main__":
    unittest.main()
