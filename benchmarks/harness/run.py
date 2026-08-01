#!/usr/bin/env python3
"""Run Vidux's small, offline benchmark harness.

The harness deliberately drives the public local surfaces instead of importing
their implementation details: a temporary synthetic root is served by the
real browser, the real ``vidux checkpoint`` command writes a ledger row, and
the real claims CLI leaves a resumable handoff.  No provider, network, home
directory, or development-root state is consulted.

The metric projection and sealed fixture digest are hashed. Paths, timestamps,
claim IDs, and informational elapsed time stay out of the canonical digest so
a fresh run is expected to produce the same receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from typing import Any, Iterator
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURES = Path(__file__).resolve().parent / "fixtures"
MANIFEST_NAME = "manifest.json"
MANIFEST_SCHEMA = "vidux-benchmark-fixtures.v1"
SECRET_MARKER = "__BENCHMARK_SECRET__"
MAX_FIXTURE_FILES = 64
MAX_FIXTURE_BYTES = 256 * 1024
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_CASES = frozenset(
    {
        "durable-state",
        "interruption-resume",
        "proof-present",
        "proof-missing",
        "cross-project-priority-high",
        "cross-project-priority-low",
    }
)


class BenchmarkError(RuntimeError):
    """A fail-closed benchmark assertion or fixture error."""


def _runtime_secret() -> str:
    """Build a scanner-safe provider-shaped value only inside the temp root."""

    return "s" + "k-" + ("A1b2C3d4" * 4)


def _sha256_file(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise BenchmarkError(f"fixture cannot be hashed: {path.name}") from exc


def _fixture_digest(
    schema: str,
    files: list[str],
    hashes: dict[str, str],
    cases: list[dict[str, str]],
) -> str:
    projection = {
        "schema": schema,
        "cases": cases,
        "files": [{"path": path, "sha256": hashes[path]} for path in files],
    }
    canonical = json.dumps(projection, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _relative_path(raw: Any, *, field: str) -> str:
    if not isinstance(raw, str) or not raw or "\x00" in raw:
        raise BenchmarkError(f"{field} must be a non-empty relative path")
    if "\\" in raw:
        raise BenchmarkError(f"{field} must use forward-slash paths")
    parsed = PurePosixPath(raw)
    if parsed.is_absolute() or any(part in ("", ".", "..") for part in parsed.parts):
        raise BenchmarkError(f"{field} escapes the fixture root: {raw!r}")
    return str(parsed)


def _safe_join(root: Path, relative: str, *, field: str = "path") -> Path:
    rel = _relative_path(relative, field=field)
    candidate = (root / Path(*PurePosixPath(rel).parts)).resolve(strict=False)
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise BenchmarkError(f"{field} escapes its root: {relative!r}") from exc
    return candidate


def _read_fixture_text(path: Path) -> str:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise BenchmarkError(f"fixture cannot be stat'ed: {path.name}") from exc
    if size > MAX_FIXTURE_BYTES:
        raise BenchmarkError(f"fixture is too large: {path.name}")
    if path.is_symlink() or not path.is_file():
        raise BenchmarkError(f"fixture must be a regular file: {path.name}")
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise BenchmarkError(f"fixture is not valid UTF-8: {path.name}") from exc


def _secret_in_text(text: str) -> bool:
    """Reject real credential-shaped fixture content, with one safe marker."""

    # The marker is intentionally allowed only as the complete synthetic
    # assignment.  A line containing extra content must not smuggle a second
    # credential-shaped value past the scanner.
    marker_assignment = re.compile(
        rf"^\s*API_TOKEN\s*=\s*{re.escape(SECRET_MARKER)}\s*$"
    )
    lines = text.splitlines()
    if any(SECRET_MARKER in line and not marker_assignment.fullmatch(line) for line in lines):
        return True
    check_lines = [line for line in lines if not marker_assignment.fullmatch(line)]
    checked = "\n".join(check_lines)

    provider_prefixes = (
        "s" + "k-",
        "github_" + "pat_",
        "gh" + "p_",
        "xox" + "b-",
        "AKIA",
        "AIza",
        "sk_" + "live_",
    )
    for prefix in provider_prefixes:
        start = 0
        while True:
            index = checked.find(prefix, start)
            if index < 0:
                break
            tail = checked[index + len(prefix):]
            match = re.match(r"[A-Za-z0-9_-]+", tail)
            if match is not None and len(match.group(0)) >= 16:
                return True
            start = index + len(prefix)

    assignment = re.compile(
        r"(?i)\b(?:api[_-]?key|access[_-]?(?:key|token)|auth[_-]?token|"
        r"client[_-]?secret|private[_-]?key|credential|password|passwd|token)"
        r"\s*[:=]\s*(['\"`]?)([^\s,;'\"`]{4,})\1"
    )
    return assignment.search(checked) is not None


def _validate_referenced_paths(text: str, *, source: str) -> None:
    """Validate evidence/proof references without requiring missing proof."""

    for match in re.finditer(
        r"(?i)\b(?:evidence|proof)\s*:\s*([^\s\]|,)]+)", text
    ):
        reference = match.group(1).rstrip(".,;:)")
        if reference.startswith("http://") or reference.startswith("https://"):
            continue
        _relative_path(reference, field=f"{source} reference")


def _actual_fixture_files(fixtures: Path) -> set[str]:
    actual: set[str] = set()
    for path in fixtures.rglob("*"):
        if path.name == MANIFEST_NAME:
            continue
        if path.is_symlink():
            raise BenchmarkError(f"fixture symlinks are not allowed: {path}")
        if path.is_file():
            try:
                relative = path.relative_to(fixtures)
            except ValueError as exc:
                raise BenchmarkError(f"fixture escaped its directory: {path}") from exc
            actual.add(str(PurePosixPath(*relative.parts)))
        elif not path.is_dir():
            raise BenchmarkError(f"fixture entry is not a file or directory: {path}")
    return actual


def validate_manifest(manifest: Any, fixtures: Path) -> dict[str, Any]:
    """Validate the sealed fixture manifest and every listed source file."""

    if not isinstance(manifest, dict):
        raise BenchmarkError("fixture manifest must be an object")
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise BenchmarkError("fixture manifest schema is unsupported")

    files_raw = manifest.get("files")
    cases_raw = manifest.get("cases")
    hashes_raw = manifest.get("sha256")
    if not isinstance(files_raw, list) or not files_raw:
        raise BenchmarkError("fixture manifest files must be a non-empty list")
    if not isinstance(cases_raw, list) or not cases_raw:
        raise BenchmarkError("fixture manifest cases must be a non-empty list")
    if not isinstance(hashes_raw, dict):
        raise BenchmarkError("fixture manifest sha256 map is required")
    if len(files_raw) > MAX_FIXTURE_FILES:
        raise BenchmarkError("fixture manifest has too many files")

    files: list[str] = []
    for raw in files_raw:
        relative = _relative_path(raw, field="fixture file")
        if relative in files:
            raise BenchmarkError(f"fixture file is listed twice: {relative}")
        if not relative.endswith((".md", ".json")):
            raise BenchmarkError(f"fixture file type is not allowed: {relative}")
        files.append(relative)

    cases: list[dict[str, str]] = []
    case_ids: set[str] = set()
    case_paths: set[str] = set()
    for raw in cases_raw:
        if not isinstance(raw, dict):
            raise BenchmarkError("each fixture case must be an object")
        case_id = raw.get("id")
        if not isinstance(case_id, str) or not re.fullmatch(r"[a-z0-9-]{3,64}", case_id):
            raise BenchmarkError("fixture case id is invalid")
        if case_id in case_ids:
            raise BenchmarkError(f"fixture case is listed twice: {case_id}")
        relative = _relative_path(raw.get("path"), field=f"case {case_id} path")
        if not relative.endswith("/PLAN.md") or relative not in files:
            raise BenchmarkError(f"case {case_id} must point to a listed PLAN.md")
        case_ids.add(case_id)
        case_paths.add(relative)
        cases.append({"id": case_id, "path": relative})

    if case_ids != REQUIRED_CASES:
        missing = sorted(REQUIRED_CASES - case_ids)
        extra = sorted(case_ids - REQUIRED_CASES)
        raise BenchmarkError(f"fixture cases do not match the sealed set (missing={missing}, extra={extra})")
    if len(case_paths) != len(cases):
        raise BenchmarkError("fixture cases must point to distinct plans")

    listed = set(files)
    if set(hashes_raw) != listed:
        raise BenchmarkError("fixture manifest sha256 keys must match its files")
    hashes: dict[str, str] = {}
    for relative, raw_hash in hashes_raw.items():
        if not isinstance(raw_hash, str) or not SHA256_RE.fullmatch(raw_hash):
            raise BenchmarkError(f"fixture hash is not a lowercase SHA-256: {relative}")
        hashes[relative] = raw_hash

    actual = _actual_fixture_files(fixtures)
    if actual != listed:
        raise BenchmarkError(
            f"fixture file set mismatch (missing={sorted(listed - actual)}, extra={sorted(actual - listed)})"
        )

    for relative in files:
        source = _safe_join(fixtures, relative, field="fixture file")
        try:
            source.relative_to(fixtures.resolve())
        except ValueError as exc:
            raise BenchmarkError(f"fixture escaped its directory: {relative}") from exc
        text = _read_fixture_text(source)
        actual_hash = _sha256_file(source)
        if actual_hash != hashes[relative]:
            raise BenchmarkError(f"fixture hash mismatch: {relative}")
        if _secret_in_text(text):
            raise BenchmarkError(f"fixture contains a credential-shaped value: {relative}")
        _validate_referenced_paths(text, source=relative)

    for relative in case_paths:
        text = _read_fixture_text(_safe_join(fixtures, relative))
        if not text.lstrip().startswith("#") or "## Tasks" not in text:
            raise BenchmarkError(f"plan fixture is not a usable PLAN.md: {relative}")

    return {
        "schema": MANIFEST_SCHEMA,
        "files": files,
        "cases": cases,
        "sha256": hashes,
        "fixture_digest": _fixture_digest(MANIFEST_SCHEMA, files, hashes, cases),
    }


def load_manifest(fixtures: Path = DEFAULT_FIXTURES) -> dict[str, Any]:
    fixtures = fixtures.expanduser().resolve()
    manifest_path = fixtures / MANIFEST_NAME
    try:
        manifest = json.loads(_read_fixture_text(manifest_path))
    except json.JSONDecodeError as exc:
        raise BenchmarkError(f"fixture manifest is malformed: {exc}") from exc
    return validate_manifest(manifest, fixtures)


def copy_fixtures(destination: Path, fixtures: Path = DEFAULT_FIXTURES) -> dict[str, Any]:
    """Copy validated fixtures into ``destination`` and insert one runtime token."""

    manifest = load_manifest(fixtures)
    destination = destination.expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)
    secret = _runtime_secret()
    for relative in manifest["files"]:
        source = _safe_join(fixtures, relative, field="fixture file")
        target = _safe_join(destination, relative, field="copied fixture file")
        target.parent.mkdir(parents=True, exist_ok=True)
        text = _read_fixture_text(source)
        text = text.replace(SECRET_MARKER, secret)
        target.write_text(text, encoding="utf-8")
    return manifest


def _run_checked(args: list[str], *, cwd: Path, env: dict[str, str], timeout: float = 30.0) -> str:
    result = subprocess.run(
        args,
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip().replace("\n", " | ")
        raise BenchmarkError(f"command failed ({result.returncode}): {' '.join(args[:3])}: {detail}")
    return result.stdout


def _seed_git(root: Path, env: dict[str, str]) -> None:
    _run_checked(["git", "init", "-q", "-b", "main", str(root)], cwd=root, env=env)
    _run_checked(["git", "-C", str(root), "config", "user.email", "benchmark@example.invalid"], cwd=root, env=env)
    _run_checked(["git", "-C", str(root), "config", "user.name", "Vidux Benchmark"], cwd=root, env=env)
    _run_checked(["git", "-C", str(root), "add", "."], cwd=root, env=env)
    _run_checked(["git", "-C", str(root), "commit", "-qm", "seed synthetic benchmark fixtures"], cwd=root, env=env)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _request(port: int, target: str) -> tuple[int, bytes]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    try:
        connection.request("GET", target, headers={"Host": f"127.0.0.1:{port}"})
        response = connection.getresponse()
        return response.status, response.read()
    finally:
        connection.close()


def _json_request(port: int, target: str) -> dict[str, Any]:
    status, body = _request(port, target)
    if status != 200:
        raise BenchmarkError(f"GET {target} returned HTTP {status}: {body[:160]!r}")
    try:
        value = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BenchmarkError(f"GET {target} did not return JSON") from exc
    if not isinstance(value, dict):
        raise BenchmarkError(f"GET {target} returned a non-object JSON value")
    return value


def _stop_browser(process: subprocess.Popen) -> None:
    if process.poll() is None:
        process.send_signal(signal.SIGTERM)
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=3)


@contextmanager
def _browser(root: Path, state: Path, env: dict[str, str]) -> Iterator[int]:
    port = _free_port()
    command = [
        sys.executable,
        str(ROOT / "browser" / "server.py"),
        "--root",
        str(root),
        "--port",
        str(port),
        "--host",
        "127.0.0.1",
        "--comments-path",
        str(state / "comments.jsonl"),
        "--steering-path",
        str(state / "steering.jsonl"),
        "--claims-path",
        str(state / "claims.jsonl"),
        "--artifacts-dir",
        str(state / "artifacts"),
    ]
    process = subprocess.Popen(
        command,
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        deadline = time.monotonic() + 8.0
        while time.monotonic() < deadline:
            if process.poll() is not None:
                break
            try:
                status, _ = _request(port, "/api/health")
                if status == 200:
                    yield port
                    return
            except (OSError, http.client.HTTPException):
                time.sleep(0.03)
        # Stop the child before reading its pipe.  Reading an open stderr pipe
        # here can block forever when a broken server stays alive but never
        # serves /api/health.
        _stop_browser(process)
        stderr = ""
        if process.stderr is not None:
            try:
                stderr = process.stderr.read().strip()
            except OSError:
                stderr = ""
        raise BenchmarkError(f"browser did not become ready: {stderr[-800:]}")
    finally:
        _stop_browser(process)
        if process.stderr is not None:
            process.stderr.close()


def _fixture_case_map(manifest: dict[str, Any]) -> dict[str, str]:
    return {item["id"]: item["path"] for item in manifest["cases"]}


def _canonical_projection(
    *,
    root: Path,
    health: dict[str, Any],
    plans_payload: dict[str, Any],
    ledger_payload: dict[str, Any],
    coordination_payload: dict[str, Any],
    file_body: bytes,
    path_escape_status: dict[str, Any],
    secret: str,
    fixture_digest: str,
) -> dict[str, Any]:
    plans = plans_payload.get("plans")
    if not isinstance(plans, list):
        raise BenchmarkError("/api/plans did not return a plan list")
    summary = plans_payload.get("summary") or {}
    dashboard = plans_payload.get("dashboard") or {}
    mission = (dashboard.get("mission_control") or {}) if isinstance(dashboard, dict) else {}
    selected = mission.get("selected") or {}
    plan_projection: list[dict[str, Any]] = []
    redaction_count = 0
    for plan in plans:
        if not isinstance(plan, dict):
            raise BenchmarkError("/api/plans contained a non-object plan")
        relative = str(plan.get("rel") or "")
        stats = plan.get("task_stats") or {}
        counts = stats.get("counts") or {}
        brief = plan.get("operator_brief") or {}
        redaction_count += int(plan.get("sensitive_redactions") or 0)
        plan_projection.append(
            {
                "rel": relative,
                "repo": str(plan.get("repo") or ""),
                "priority": int(brief.get("priority") or 0),
                "task_counts": {
                    "pending": int(counts.get("pending") or 0),
                    "in_progress": int(counts.get("in_progress") or 0),
                    "completed": int(counts.get("completed") or 0),
                    "blocked": int(counts.get("blocked") or 0),
                },
                "content_redacted": bool(plan.get("content_redacted")),
            }
        )
    plan_projection.sort(key=lambda item: item["rel"])

    ledger_items = ledger_payload.get("items") or []
    if not isinstance(ledger_items, list):
        raise BenchmarkError("/api/ledger did not return plan_items")
    ledger_projection = [
        {
            "event": str(item.get("event") or ""),
            "proof_present": bool(item.get("proof")),
            "resume_present": bool(item.get("next_agent_resume")),
            "handoff_status": str(item.get("handoff_status") or ""),
        }
        for item in ledger_items
        if isinstance(item, dict)
    ]
    ledger_projection.sort(key=lambda item: (item["event"], item["handoff_status"]))

    handoffs = coordination_payload.get("handoffs") or []
    active = coordination_payload.get("active") or []
    checkpoint = {}
    if handoffs and isinstance(handoffs[0], dict):
        checkpoint = handoffs[0].get("checkpoint") or {}
    if not isinstance(checkpoint, dict):
        checkpoint = {}

    rendered_file = file_body.decode("utf-8", errors="replace")
    if secret in rendered_file:
        raise BenchmarkError("browser file response leaked the synthetic provider token")
    if "[REDACTED:secret]" not in rendered_file:
        raise BenchmarkError("browser file response did not expose its redaction marker")
    api_blob = json.dumps(
        [health, plans_payload, ledger_payload, coordination_payload],
        sort_keys=True,
    )
    if secret in api_blob:
        raise BenchmarkError("browser JSON response leaked the synthetic provider token")

    authority = mission.get("authority") or {}
    if not isinstance(selected, dict) or selected.get("rel") != "priority-high/PLAN.md":
        raise BenchmarkError("mission control did not select the sealed high-priority plan")
    evidence_target = selected.get("evidence_target")
    if not isinstance(evidence_target, dict):
        raise BenchmarkError("mission control omitted the selected evidence target")
    scorecard_targets: dict[str, str] = {}
    for metric in selected.get("scorecard") or []:
        if not isinstance(metric, dict):
            raise BenchmarkError("mission control scorecard contains a non-object")
        name = str(metric.get("metric") or "")
        target = metric.get("proof_target")
        if not name or not isinstance(target, dict):
            raise BenchmarkError("mission control omitted a scorecard proof target")
        scorecard_targets[name] = str(target.get("state") or "")
    if evidence_target.get("state") != "available":
        raise BenchmarkError("mission control selected evidence is not available")
    if scorecard_targets.get("Proof present") != "available":
        raise BenchmarkError("mission control did not resolve the available scorecard proof")
    if scorecard_targets.get("Proof missing") != "missing":
        raise BenchmarkError("mission control did not preserve the missing scorecard proof")
    return {
        "fixture_digest": fixture_digest,
        "health_ok": bool(health.get("ok")) and health.get("dev_root") == str(root),
        "plan_count": len(plan_projection),
        "repo_count": int(summary.get("repos") or 0),
        "task_totals": {
            "completed": int(summary.get("tasks_completed") or 0),
            "total": int(summary.get("tasks_total") or 0),
        },
        "plans": plan_projection,
        "proof_targets": {
            "selected_evidence": str(evidence_target.get("state") or ""),
            "selected_scorecard": dict(sorted(scorecard_targets.items())),
        },
        "priority": {
            "authority_state": str(authority.get("state") or ""),
            "selected_rel": str(selected.get("rel") or ""),
            "selected_priority": int(selected.get("priority") or 0),
        },
        "redaction": {
            "plans_with_redactions": sum(1 for plan in plan_projection if plan["content_redacted"]),
            "redaction_count": redaction_count,
            "file_marker_present": "[REDACTED:secret]" in rendered_file,
        },
        "path_escape": path_escape_status,
        "ledger": {
            "plan_items": ledger_projection,
            "checkpoint_rows": sum(1 for item in ledger_projection if item["event"] == "vidux_checkpoint"),
        },
        "resume": {
            "active_claims": len(active),
            "handoffs": len(handoffs),
            "checkpoint_present": bool(checkpoint),
            "resume_present": bool(checkpoint.get("resume")),
        },
    }


def run_benchmark(fixtures: Path = DEFAULT_FIXTURES) -> dict[str, Any]:
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="vidux-benchmark-") as temp:
        temp_root = Path(temp).resolve()
        fixture_root = temp_root / "synthetic-root"
        state = temp_root / "state"
        home = temp_root / "home"
        state.mkdir()
        home.mkdir()
        (state / "ledger.jsonl").write_text("", encoding="utf-8")
        (state / "claims.jsonl").write_text("", encoding="utf-8")
        manifest = copy_fixtures(fixture_root, fixtures)
        _seed_git(fixture_root, {
            **os.environ,
            "HOME": str(home),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": str(temp_root / "empty-git-config"),
        })

        env = {
            **os.environ,
            "HOME": str(home),
            "XDG_CONFIG_HOME": str(temp_root / "xdg-config"),
            "XDG_DATA_HOME": str(temp_root / "xdg-data"),
            "XDG_CACHE_HOME": str(temp_root / "xdg-cache"),
            "VIDUX_DEV_ROOT": str(fixture_root),
            "VIDUX_PLANS_CACHE_TTL_SECONDS": "0",
            "VIDUX_CLAUDE_PROJECTS_DIR": str(temp_root / "claude-projects"),
            "VIDUX_LEDGER_FILE": str(state / "ledger.jsonl"),
            "VIDUX_CLAIMS_FILE": str(state / "claims.jsonl"),
            "VIDUX_ROOT": str(ROOT),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": str(temp_root / "empty-git-config"),
        }
        (temp_root / "empty-git-config").write_text("", encoding="utf-8")
        (state / "comments.jsonl").write_text("", encoding="utf-8")
        (state / "steering.jsonl").write_text("", encoding="utf-8")

        cases = _fixture_case_map(manifest)
        durable_plan = fixture_root / cases["durable-state"]
        interrupted_plan = fixture_root / cases["interruption-resume"]
        # Make the producer's repo identity agree with the browser's
        # dev-root projection.  The real emitter prefers CODEX_PROJECT_DIR;
        # without this, the temporary git root would be reported as
        # ``synthetic-root`` and the browser correctly filters that row out
        # of the durable plan's ledger view.
        env["CODEX_PROJECT_DIR"] = str(durable_plan.parent)

        _run_checked(
            [
                str(ROOT / "bin" / "vidux"),
                "checkpoint",
                str(durable_plan),
                "capture the durable checkpoint",
                "durable checkpoint recorded",
                "--proof",
                "offline benchmark proof present",
            ],
            cwd=fixture_root,
            env=env,
        )

        claim_output = _run_checked(
            [
                sys.executable,
                str(ROOT / "scripts" / "vidux-claims.py"),
                "--claims-file",
                str(state / "claims.jsonl"),
                "claim",
                "--repo",
                "interrupted",
                "--claim",
                "resume the interrupted surface",
                "--owner",
                "benchmark-runner",
                "--lane",
                "offline-harness",
                "--plan-path",
                str(interrupted_plan),
                "--task-id",
                "resume-1",
                "--ttl-hours",
                "1",
            ],
            cwd=fixture_root,
            env=env,
        )
        try:
            claim = json.loads(claim_output)
            claim_id = str(claim["claim"]["claim_id"])
        except (KeyError, TypeError, json.JSONDecodeError) as exc:
            raise BenchmarkError("claims CLI did not return a claim id") from exc
        _run_checked(
            [
                sys.executable,
                str(ROOT / "scripts" / "vidux-claims.py"),
                "--claims-file",
                str(state / "claims.jsonl"),
                "checkpoint",
                "--claim-id",
                claim_id,
                "--owner",
                "benchmark-runner",
                "--summary",
                "interruption checkpoint captured",
                "--resume",
                "resume from the interrupted synthetic plan",
                "--proof",
                "claims round-trip proof",
            ],
            cwd=fixture_root,
            env=env,
        )

        outside_file = temp_root / "outside.md"
        outside_file.write_text("outside the synthetic root\n", encoding="utf-8")
        outside_plan = temp_root / "outside-plan.md"
        outside_plan.write_text("# Outside\n\n## Tasks\n- [pending] never serve\n", encoding="utf-8")
        symlink_plan = fixture_root / "symlink-plan" / "PLAN.md"
        symlink_plan.parent.mkdir(parents=True)
        symlink_plan.symlink_to(outside_plan)
        _run_checked(
            [
                sys.executable,
                str(ROOT / "scripts" / "vidux-claims.py"),
                "--claims-file",
                str(state / "claims.jsonl"),
                "release",
                "--claim-id",
                claim_id,
                "--owner",
                "benchmark-runner",
                "--status",
                "handoff",
                "--summary",
                "interruption left a resumable handoff",
                "--resume",
                "resume from the interrupted synthetic plan",
                "--proof",
                "handoff proof present",
            ],
            cwd=fixture_root,
            env=env,
        )

        with _browser(fixture_root, state, env) as port:
            health = _json_request(port, "/api/health")
            plans = _json_request(port, "/api/plans")
            ledger = _json_request(port, "/api/ledger?path=" + quote(str(durable_plan), safe=""))
            coordination = _json_request(
                port,
                "/api/coordination?plan_path=" + quote(str(interrupted_plan), safe=""),
            )
            file_status, file_body = _request(
                port,
                "/api/file?path=" + quote(str(durable_plan), safe=""),
            )
            if file_status != 200:
                raise BenchmarkError(f"redaction file request returned HTTP {file_status}")
            escape_status, _ = _request(
                port,
                "/api/file?path=" + quote(str(fixture_root.parent / "outside.md"), safe=""),
            )
            relative_escape_status, _ = _request(port, "/api/file?path=../outside.md")
            symlink_file_status, _ = _request(
                port,
                "/api/file?path=" + quote(str(symlink_plan), safe=""),
            )
            symlink_ledger_status, _ = _request(
                port,
                "/api/ledger?path=" + quote(str(symlink_plan), safe=""),
            )
            symlink_coordination_status, _ = _request(
                port,
                "/api/coordination?plan_path=" + quote(str(symlink_plan), safe=""),
            )

        projection = _canonical_projection(
            root=fixture_root,
            health=health,
            plans_payload=plans,
            ledger_payload=ledger,
            coordination_payload=coordination,
            file_body=file_body,
            path_escape_status={
                "absolute_status": escape_status,
                "relative_status": relative_escape_status,
                "symlink_file_status": symlink_file_status,
                "symlink_ledger_status": symlink_ledger_status,
                "symlink_coordination_status": symlink_coordination_status,
                "rejected": all(
                    status != 200
                    for status in (
                        escape_status,
                        relative_escape_status,
                        symlink_file_status,
                        symlink_ledger_status,
                        symlink_coordination_status,
                    )
                ),
            },
            secret=_runtime_secret(),
            fixture_digest=str(manifest["fixture_digest"]),
        )

    canonical = json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return {
        "schema": "vidux-benchmark-receipt.v1",
        "fixture_digest": str(manifest["fixture_digest"]),
        "canonical_digest": digest,
        "metrics": projection,
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the offline Vidux benchmark harness.")
    parser.add_argument(
        "--fixtures",
        type=Path,
        default=DEFAULT_FIXTURES,
        help="sealed fixture directory (defaults to benchmarks/harness/fixtures)",
    )
    args = parser.parse_args(argv)
    try:
        receipt = run_benchmark(args.fixtures)
    except (BenchmarkError, OSError, subprocess.SubprocessError) as exc:
        print(f"vidux benchmark: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
