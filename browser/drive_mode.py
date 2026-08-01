"""Pure helpers for the provider-neutral Vidux Drive / 90 boundary.

This module deliberately does not read a plan, write a mailbox, invoke a
provider, or retain input.  It projects one already-validated
``vidux.outcome.v1`` document into the small semantic surface a native voice
client needs, and builds one typed choice envelope for the owning host.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
import re
from typing import Any


OUTCOME_SCHEMA = "vidux.outcome.v1"
DRIVE_SCHEMA = "vidux.drive.v1"
STEER_SCHEMA = "vidux.drive-steer.v1"
MAX_PRESENTED_OPTIONS = 3
NONTERMINAL_STEER_STATES = frozenset({"received", "applied", "working", "blocked"})
IDENTIFIER_RE = re.compile(r"^[a-z][a-z0-9_-]{2,63}$")


class DriveInputError(ValueError):
    """Raised when a client receives a document outside the typed boundary."""


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise DriveInputError(f"{label} must be an object")
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DriveInputError(f"{label} must be a nonblank string")
    return value


def _identifier(value: Any, label: str) -> str:
    value = _text(value, label)
    if not IDENTIFIER_RE.fullmatch(value):
        raise DriveInputError(f"{label} must be a public identifier")
    return value


def _document(document: Any) -> Mapping[str, Any]:
    document = _mapping(document, "document")
    if document.get("schema") != OUTCOME_SCHEMA:
        raise DriveInputError(f"document schema must equal {OUTCOME_SCHEMA}")
    return document


def _outcome(document: Mapping[str, Any]) -> Mapping[str, Any]:
    outcome = _mapping(document.get("outcome"), "outcome")
    return {
        "id": _identifier(outcome.get("id"), "outcome.id"),
        "summary": _text(outcome.get("summary"), "outcome.summary"),
        "state": _text(outcome.get("state"), "outcome.state"),
        "current_move": outcome.get("current_move"),
    }


def _ask(document: Mapping[str, Any], outcome: Mapping[str, Any]) -> dict[str, Any] | None:
    raw = document.get("ask")
    if raw is None:
        return None
    ask = _mapping(raw, "ask")
    ask_id = _identifier(ask.get("id"), "ask.id")
    state = _text(ask.get("state"), "ask.state")
    options = ask.get("options")
    if not isinstance(options, Sequence) or isinstance(options, (str, bytes)):
        raise DriveInputError("ask.options must be an array")
    normalized: list[dict[str, str]] = []
    seen: set[str] = set()
    for index, raw_option in enumerate(options):
        option = _mapping(raw_option, f"ask.options[{index}]")
        option_id = _identifier(option.get("id"), f"ask.options[{index}].id")
        if option_id in seen:
            raise DriveInputError("ask option IDs must be unique")
        seen.add(option_id)
        normalized.append(
            {
                "id": option_id,
                "label": _text(option.get("label"), f"ask.options[{index}].label"),
                "consequence": _text(
                    option.get("consequence"),
                    f"ask.options[{index}].consequence",
                ),
            }
        )
    if state == "open" and outcome.get("state") != "needs_input":
        raise DriveInputError("an open Ask requires an outcome in needs_input state")
    if state != "open" and outcome.get("state") == "needs_input":
        raise DriveInputError("a needs_input outcome requires an open Ask")
    visible = normalized[:MAX_PRESENTED_OPTIONS] if state == "open" else []
    return {
        "id": ask_id,
        "category": _text(ask.get("category"), "ask.category"),
        "question": _text(ask.get("question"), "ask.question"),
        "state": state,
        "answer_option_id": ask.get("answer_option_id"),
        "options": visible,
        "options_total": len(normalized),
        "options_truncated": len(visible) < len(normalized) if state == "open" else False,
    }


def _steers(document: Mapping[str, Any], outcome_id: str) -> list[dict[str, Any]]:
    raw_steers = document.get("steers", [])
    if not isinstance(raw_steers, Sequence) or isinstance(raw_steers, (str, bytes)):
        raise DriveInputError("steers must be an array")
    result: list[dict[str, Any]] = []
    for index, raw_steer in enumerate(raw_steers):
        steer = _mapping(raw_steer, f"steers[{index}]")
        if steer.get("outcome_id") != outcome_id:
            raise DriveInputError("every Steer must target the current Outcome")
        result.append(
            {
                "id": _identifier(steer.get("id"), f"steers[{index}].id"),
                "outcome_id": outcome_id,
                "summary": _text(steer.get("summary"), f"steers[{index}].summary"),
                "state": _text(steer.get("state"), f"steers[{index}].state"),
                "proof_ref": steer.get("proof_ref"),
            }
        )
    return result


def _proof(document: Mapping[str, Any]) -> list[dict[str, Any]]:
    raw_proof = document.get("proof", [])
    if not isinstance(raw_proof, Sequence) or isinstance(raw_proof, (str, bytes)):
        raise DriveInputError("proof must be an array")
    result: list[dict[str, Any]] = []
    for index, raw_reference in enumerate(raw_proof):
        reference = _mapping(raw_reference, f"proof[{index}]")
        result.append(
            {
                "id": _identifier(reference.get("id"), f"proof[{index}].id"),
                "type": _text(reference.get("type"), f"proof[{index}].type"),
                "locator": _text(reference.get("locator"), f"proof[{index}].locator"),
                "verification_summary": _text(
                    reference.get("verification_summary"),
                    f"proof[{index}].verification_summary",
                ),
                "delivery": _text(reference.get("delivery"), f"proof[{index}].delivery"),
            }
        )
    return result


def project_drive(document: Any) -> dict[str, Any]:
    """Return the bounded semantic view consumed by a native 90 client.

    The returned object is newly allocated and contains only allowlisted
    semantic fields.  In particular, provider/model/prompt/transcript and
    arbitrary host fields can never pass through this projection.
    """

    source = _document(document)
    outcome = _outcome(source)
    ask = _ask(source, outcome)
    steers = _steers(source, outcome["id"])
    proof = _proof(source)
    active = next((item for item in steers if item["state"] in NONTERMINAL_STEER_STATES), None)
    return {
        "schema": DRIVE_SCHEMA,
        "revision": source.get("revision"),
        "updated_at": source.get("updated_at"),
        "outcome": deepcopy(outcome),
        "ask": ask,
        "active_steer_id": active["id"] if active else None,
        "steers": steers,
        "proof": proof,
    }


def build_choice(document: Any, option_id: Any) -> dict[str, str]:
    """Build one ephemeral typed answer for the owning host.

    This is an intent envelope, not a durable Steer record.  The host that
    owns the Outcome decides whether to accept it and records the resulting
    Steer/proof in the existing authority.  There is intentionally no free
    text, provider, model, command, or queue field.
    """

    source = _document(document)
    outcome = _outcome(source)
    ask = _ask(source, outcome)
    if ask is None or ask["state"] != "open":
        raise DriveInputError("a choice requires an open Ask")
    option_id = _identifier(option_id, "option_id")
    options = source["ask"].get("options", [])
    if not any(isinstance(option, Mapping) and option.get("id") == option_id for option in options):
        raise DriveInputError("option_id is not present in the open Ask")
    return {
        "schema": STEER_SCHEMA,
        "kind": "answer",
        "outcome_id": outcome["id"],
        "ask_id": ask["id"],
        "option_id": option_id,
    }


__all__ = [
    "DRIVE_SCHEMA",
    "MAX_PRESENTED_OPTIONS",
    "OUTCOME_SCHEMA",
    "STEER_SCHEMA",
    "DriveInputError",
    "build_choice",
    "project_drive",
]
