"""shadow accept --row: the clean-checkout proof rerun is the only flip path."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "shadow-accept.py"


PLAN = """# Demo

## Operator Brief

- Entity: demo
- Mode: Close

## Checkpoints

### M — file speaks
- [in_progress] x.txt says hello ~ab12 | proof: cmd python3 -c "import pathlib,sys; sys.exit(0 if pathlib.Path('x.txt').read_text()=='hello' else 1)"
- [pending] shipped ~cd34 (DoD) | proof: gate leo resume: release cut

## Progress

- 2026-08-06T10:00:00Z POSTURE Broad->Close | harness: the proof command
"""


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=False)
    if result.returncode:
        raise AssertionError(result.stderr)
    return result.stdout.strip()


def make_repo(root: Path, content: str = "hello") -> Path:
    repo = root / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "t@example.invalid")
    git(repo, "config", "user.name", "T")
    (repo / "x.txt").write_text(content, encoding="utf-8")
    (repo / "PLAN.md").write_text(PLAN, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "base")
    return repo


def run_accept(repo: Path, row: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--repo", str(repo), "--row", row],
        capture_output=True,
        text=True,
        check=False,
    )


class ShadowAcceptTests(unittest.TestCase):
    def test_green_proof_flips_the_row_with_a_paired_proof_line_in_one_commit(self) -> None:
        with tempfile.TemporaryDirectory() as dirname:
            repo = make_repo(Path(dirname).resolve())
            before = git(repo, "rev-parse", "HEAD")
            result = run_accept(repo, "~ab12")
            text = (repo / "PLAN.md").read_text(encoding="utf-8")
            commits = git(repo, "rev-list", "--count", "HEAD")
            subject = git(repo, "log", "-1", "--pretty=%s")
            status = git(repo, "status", "--porcelain")
            pools = list(Path(dirname).resolve().glob("**/*shadow-accept*"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("- [completed] x.txt says hello ~ab12", text)
        self.assertIn("~ab12 PROOF", text)
        self.assertIn("-> pass (accept)", text)
        self.assertEqual(commits, "2")
        self.assertIn("~ab12", subject)
        self.assertEqual(status, "")
        self.assertEqual(pools, [])

    def test_red_proof_touches_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as dirname:
            repo = make_repo(Path(dirname).resolve(), content="goodbye")
            before_plan = (repo / "PLAN.md").read_text(encoding="utf-8")
            result = run_accept(repo, "~ab12")
            after_plan = (repo / "PLAN.md").read_text(encoding="utf-8")
            commits = git(repo, "rev-list", "--count", "HEAD")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(before_plan, after_plan)
        self.assertEqual(commits, "1")

    def test_gate_class_proof_is_refused_plainly(self) -> None:
        with tempfile.TemporaryDirectory() as dirname:
            repo = make_repo(Path(dirname).resolve())
            result = run_accept(repo, "~cd34")
        self.assertEqual(result.returncode, 1)
        self.assertIn("gate", result.stderr.lower() + result.stdout.lower())

    def test_unknown_row_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as dirname:
            repo = make_repo(Path(dirname).resolve())
            result = run_accept(repo, "~zz99")
        self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
