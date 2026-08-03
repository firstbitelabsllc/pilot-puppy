from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "pilot-puppy-public-ready-grep-gate.py"
SPEC = importlib.util.spec_from_file_location("public_ready", SCRIPT)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


class PublicReadyTests(unittest.TestCase):
    def test_clean_public_text_passes(self) -> None:
        with tempfile.TemporaryDirectory() as dirname:
            root = Path(dirname)
            path = root / "README.md"
            path.write_text("Pilot Puppy stores bounded local proof.\n", encoding="utf-8")
            report = mod.scan(root, [path], metadata=False)
        self.assertTrue(report["ok"], report)

    def test_private_home_path_fails(self) -> None:
        with tempfile.TemporaryDirectory() as dirname:
            root = Path(dirname)
            path = root / "README.md"
            path.write_text("checkout: /" + "Users/realname/secret\n", encoding="utf-8")
            report = mod.scan(root, [path], metadata=False)
        self.assertFalse(report["ok"])
        self.assertEqual(report["findings"][0]["reason"], "private filesystem path")

    def test_secret_shape_fails(self) -> None:
        with tempfile.TemporaryDirectory() as dirname:
            root = Path(dirname)
            path = root / "notes.md"
            path.write_text("token: gh" + "p_12345678901234567890\n", encoding="utf-8")
            report = mod.scan(root, [path], metadata=False)
        self.assertFalse(report["ok"])
        self.assertEqual(report["findings"][0]["reason"], "secret-shaped value")

    def test_evidence_stream_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as dirname:
            root = Path(dirname)
            path = root / "activity.jsonl"
            path.write_text("{}\n", encoding="utf-8")
            report = mod.scan(root, [path], metadata=False)
        self.assertFalse(report["ok"])
        self.assertEqual(report["findings"][0]["reason"], "forbidden release file")

    def test_symlinked_release_path_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as dirname:
            root = Path(dirname) / "repo"
            root.mkdir()
            outside = Path(dirname) / "outside.txt"
            outside.write_text("safe public text\n", encoding="utf-8")
            path = root / "README.md"
            path.symlink_to(outside)
            report = mod.scan(root, [path], metadata=False)
        self.assertFalse(report["ok"])
        self.assertEqual(report["findings"][0]["reason"], "symlinked release path")

    def test_unreadable_release_path_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as dirname:
            root = Path(dirname)
            path = root / "README.md"
            path.write_text("safe public text\n", encoding="utf-8")
            with mock.patch.object(Path, "read_bytes", side_effect=OSError("private path")):
                report = mod.scan(root, [path], metadata=False)
        self.assertFalse(report["ok"])
        self.assertEqual(report["findings"][0]["reason"], "unreadable release path")

    def test_current_metadata_is_consistent(self) -> None:
        self.assertEqual(mod.metadata_errors(ROOT), [])

    def test_metadata_with_non_objects_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as dirname:
            root = Path(dirname)
            (root / "package.json").write_text("[]\n", encoding="utf-8")
            (root / ".claude-plugin").mkdir()
            (root / ".claude-plugin" / "plugin.json").write_text("{}\n", encoding="utf-8")
            (root / "VERSION").write_text("2.1.0\n", encoding="utf-8")
            self.assertEqual(mod.metadata_errors(root), ["metadata unreadable"])

    def test_metadata_with_invalid_utf8_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as dirname:
            root = Path(dirname)
            (root / "package.json").write_bytes(b"\xff\n")
            (root / ".claude-plugin").mkdir()
            (root / ".claude-plugin" / "plugin.json").write_text("{}\n", encoding="utf-8")
            (root / "VERSION").write_text("2.1.0\n", encoding="utf-8")
            self.assertEqual(mod.metadata_errors(root), ["metadata unreadable"])

    def test_git_paths_reject_invalid_utf8_without_traceback(self) -> None:
        result = subprocess.CompletedProcess(["git"], 0, stdout=b"?? invalid-\xff\0", stderr=b"")
        with mock.patch.object(mod.subprocess, "run", return_value=result):
            with self.assertRaisesRegex(RuntimeError, "unsafe path text"):
                mod.git_paths(Path("."))

    def test_failure_details_do_not_echo_private_paths(self) -> None:
        failed = subprocess.CompletedProcess(
            ["git"], 1, stdout=b"", stderr=b"/Users/private/secret"
        )
        with mock.patch.object(mod.subprocess, "run", return_value=failed):
            with self.assertRaisesRegex(RuntimeError, "^git ls-files failed$"):
                mod.git_paths(Path("."))

        with mock.patch.object(mod.subprocess, "run", side_effect=OSError("/Users/private/secret")):
            with self.assertRaisesRegex(RuntimeError, "^git ls-files unavailable$"):
                mod.git_paths(Path("."))

        with mock.patch.object(Path, "read_text", side_effect=OSError("/Users/private/secret")):
            self.assertEqual(mod.metadata_errors(Path("/tmp/repo")), ["metadata unreadable"])


if __name__ == "__main__":
    unittest.main()
