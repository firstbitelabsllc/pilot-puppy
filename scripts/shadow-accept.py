#!/usr/bin/env python3
"""Rerun one checkpoint row's proof in a clean checkout, then flip the row.

This is the Method's only code path that flips a row to completed. It parses
the repo's PLAN.md, finds the row by its ~hash id, reruns a ``cmd``-classed
proof inside a detached clean worktree of HEAD, and — only on success —
rewrites the row's state and appends the paired PROOF Progress line in one
commit. ``read`` and ``gate`` proofs are person/agent judgments and are
refused here on purpose.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import re
import shlex
import subprocess
import sys
from pathlib import Path


ROW_ID_RE = re.compile(r"^~[0-9a-z]{4}$")
PROOF_FIELD_RE = re.compile(r"\| proof: (?P<proof>[^|]+?)(?= \||$)")


class AcceptError(ValueError):
    """Fail closed; nothing was changed."""


def git_completed(repo: Path, *args: str, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AcceptError(f"project Git state cannot be read: {exc}") from exc


def proof_passes(worktree: Path, proof: list[str], timeout_seconds: int) -> bool:
    try:
        result = subprocess.run(
            proof,
            cwd=worktree,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


# Moved verbatim from the retired Drive engine (scripts/shadow-drive.py):
# the clean-checkout review is the mechanical trust boundary and survives
# every simplification of the vocabulary around it.
def create_lead_review_worktree(repo: Path, attempt: Path, lane_id: str, commit: str) -> Path:
    destination = attempt / lane_id
    if destination.is_symlink() or destination.exists():
        raise AcceptError("lead review location is unsafe")
    result = git_completed(repo, "worktree", "add", "--detach", str(destination), commit, timeout=30)
    if result.returncode:
        raise AcceptError("a clean lead review checkout could not be created")
    return destination


def lead_review_passes(worktree: Path, proof: list[str], timeout_seconds: int) -> bool:
    if not proof_passes(worktree, proof, timeout_seconds):
        return False
    status = git_completed(worktree, "status", "--porcelain=v1", "--untracked-files=all")
    if status.returncode:
        return False
    dirt = [
        line
        for line in status.stdout.splitlines()
        if line.strip() and not line[3:].startswith((".shadow/", ".pilot-puppy/"))
        and not line[3:].startswith("__pycache__/") and "/__pycache__/" not in line[3:]
    ]
    return not dirt


def remove_review_worktree(repo: Path, destination: Path) -> None:
    git_completed(repo, "worktree", "remove", "--force", str(destination), timeout=30)
    git_completed(repo, "worktree", "prune", timeout=15)


def find_row(plan_text: str, row_id: str) -> tuple[str, str]:
    for line in plan_text.splitlines():
        if f" {row_id}" in line and line.startswith("- ["):
            match = PROOF_FIELD_RE.search(line)
            if not match:
                raise AcceptError("the row has no proof field")
            return line, match.group("proof").strip()
    raise AcceptError(f"no checkpoint row carries {row_id}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--row", required=True)
    parser.add_argument("--timeout-seconds", type=int, default=900)
    args = parser.parse_args(argv)
    repo = args.repo.resolve()
    row_id = args.row.strip()
    try:
        if ROW_ID_RE.fullmatch(row_id) is None:
            raise AcceptError("row must be a ~hash id, four base36 chars")
        plan_path = repo / "PLAN.md"
        try:
            plan_text = plan_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise AcceptError(f"plan cannot be read: {exc}") from exc
        row_line, proof = find_row(plan_text, row_id)
        if "[completed]" in row_line:
            raise AcceptError("the row is already completed")
        if not proof.startswith("cmd "):
            kind = proof.split(" ", 1)[0]
            raise AcceptError(
                f"only cmd proofs are machine-rerunnable; this row is {kind}-classed — "
                "re-observe it yourself and append the PROOF line with the flip"
            )
        argv_proof = shlex.split(proof[4:])
        if not argv_proof:
            raise AcceptError("the proof command is empty")
        head = git_completed(repo, "rev-parse", "--verify", "HEAD").stdout.strip()
        if not head:
            raise AcceptError("the project has no HEAD commit")
        pool = repo.parent / f"{repo.name}-shadow-accept"
        pool.mkdir(exist_ok=True)
        review = create_lead_review_worktree(repo, pool, row_id.lstrip("~"), head)
        try:
            passed = lead_review_passes(review, argv_proof, args.timeout_seconds)
        finally:
            remove_review_worktree(repo, review)
            try:
                pool.rmdir()
            except OSError:
                pass
        if not passed:
            raise AcceptError("the proof did not pass in a clean checkout; nothing was changed")
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        flipped = re.sub(r"^- \[[a-z_]+\]", "- [completed]", row_line)
        updated = plan_text.replace(row_line, flipped, 1)
        proof_line = f"- {stamp} {row_id} PROOF {' '.join(argv_proof)} -> pass (accept)\n"
        if "## Progress" not in updated:
            raise AcceptError("the plan has no Progress section")
        updated = updated.rstrip() + "\n" + proof_line
        staged_before = git_completed(repo, "diff", "--cached", "--quiet", "--", "PLAN.md").returncode != 0
        plan_path.write_text(updated, encoding="utf-8")
        added = git_completed(repo, "add", "--", "PLAN.md")
        # --only with a pathspec keeps unrelated already-staged files out of the
        # acceptance commit: the flip and its PROOF line travel alone.
        committed = (
            git_completed(
                repo,
                "commit",
                "--only",
                "-m",
                f"shadow accept: {row_id} proven in a clean checkout",
                "--",
                "PLAN.md",
            )
            if added.returncode == 0
            else added
        )
        if added.returncode or committed.returncode:
            # A flipped row with no acceptance commit would read as completed
            # and refuse the rerun, so the plan goes back exactly as it was.
            plan_path.write_text(plan_text, encoding="utf-8")
            if staged_before:
                git_completed(repo, "add", "--", "PLAN.md")
            else:
                git_completed(repo, "reset", "--quiet", "HEAD", "--", "PLAN.md")
            raise AcceptError("the acceptance commit could not be created; the plan was restored")
    except AcceptError as exc:
        print(f"shadow accept: {exc}", file=sys.stderr)
        return 1
    print(f"accepted {row_id}: proof passed in a clean checkout; row flipped with its PROOF line")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
