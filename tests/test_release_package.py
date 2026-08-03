from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "pilot-puppy-release-package.py"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").splitlines()[0].strip()
SPEC = importlib.util.spec_from_file_location("release_package", SCRIPT)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


def baseline() -> tuple[dict, dict, dict, set[str]]:
    package = {
        "name": "pilot-puppy",
        "version": VERSION,
        "private": False,
        "bin": {"pilot-puppy": "bin/pilot-puppy"},
        "homepage": "https://github.com/firstbitelabsllc/pilot-puppy",
        "repository": {"url": "git+https://github.com/firstbitelabsllc/pilot-puppy.git"},
        "publishConfig": {"access": "public", "provenance": True},
    }
    plugin = {"name": "pilot-puppy", "version": VERSION}
    paths = set(mod.REQUIRED_FILES)
    pack = {
        "version": VERSION,
        "unpackedSize": 100_000,
        "files": [{"path": path} for path in sorted(paths)],
    }
    return package, plugin, pack, paths


class ReleasePackageTests(unittest.TestCase):
    def errors(self, package: dict, plugin: dict, pack: dict, tracked: set[str], **kwargs) -> list[str]:
        return mod.validate_release_candidate(
            package,
            plugin,
            pack,
            version=VERSION,
            tracked_paths=tracked,
            **kwargs,
        )

    def test_minimum_public_artifact_passes(self) -> None:
        package, plugin, pack, tracked = baseline()
        self.assertEqual(self.errors(package, plugin, pack, tracked), [])

    def test_missing_required_file_fails(self) -> None:
        package, plugin, pack, tracked = baseline()
        pack["files"] = [item for item in pack["files"] if item["path"] != "bin/pilot-puppy"]
        self.assertTrue(any("missing" in error for error in self.errors(package, plugin, pack, tracked)))

    def test_second_skill_or_private_stream_fails(self) -> None:
        package, plugin, pack, tracked = baseline()
        extras = ["nested/SKILL.md", "activity.jsonl"]
        pack["files"].extend({"path": path} for path in extras)
        tracked.update(extras)
        errors = self.errors(package, plugin, pack, tracked)
        self.assertTrue(any("exactly the root" in error for error in errors))
        self.assertTrue(any("forbidden" in error for error in errors))

    def test_dirty_bytes_require_explicit_development_mode(self) -> None:
        package, plugin, pack, tracked = baseline()
        errors = self.errors(package, plugin, pack, tracked, dirty_paths={"README.md"})
        self.assertTrue(any("uncommitted" in error for error in errors))
        self.assertEqual(self.errors(package, plugin, pack, tracked, dirty_paths={"README.md"}, allow_dirty=True), [])

    def test_current_checkout_packs_and_installs(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(ROOT), "--allow-dirty", "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, report)
        self.assertTrue(report["stranger_install"])
        self.assertTrue(report["reproducible"])
        self.assertFalse(report["publishable"])

    def test_tracked_files_reject_invalid_utf8_without_traceback(self) -> None:
        result = subprocess.CompletedProcess(["git"], 0, stdout=b"invalid-\xff\0", stderr=b"")
        with mock.patch.object(mod.subprocess, "run", return_value=result):
            with self.assertRaisesRegex(RuntimeError, "unsafe path text"):
                mod.tracked_files(ROOT)

    def test_command_failures_do_not_echo_private_details(self) -> None:
        failed = subprocess.CompletedProcess(
            ["npm"], 1, stdout="", stderr="/Users/private/secret"
        )
        with mock.patch.object(mod.subprocess, "run", return_value=failed):
            with self.assertRaisesRegex(RuntimeError, "^npm command failed$"):
                mod.command(["npm", "pack"], ROOT)

        with mock.patch.object(mod.subprocess, "run", side_effect=OSError("/Users/private/secret")):
            with self.assertRaisesRegex(RuntimeError, "^npm command unavailable$"):
                mod.command(["npm", "pack"], ROOT)


if __name__ == "__main__":
    unittest.main()
