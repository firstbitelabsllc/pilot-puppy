"""Pure projection and compare-and-set receipt for one A/B/C choice."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
import re
from typing import Any
from urllib.parse import urlparse
import unicodedata


OUTCOME_SCHEMA = "pilot-puppy.outcome.v1"
DECISION_SCHEMA = "pilot-puppy.decision.v1"
CHOICE_SCHEMA = "pilot-puppy.decision-choice.v1"
RECEIPT_SCHEMA = "pilot-puppy.decision-receipt.v1"
MAX_REVISION = 2_147_483_647
IDENTIFIER_RE = re.compile(r"^[a-z][a-z0-9_-]{2,63}$")
UTC_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?Z$")
RELATIVE_LOCATOR_RE = re.compile(
    r"^(?!\.\.(?:/|$))(?!.*(?:^|/)\.\.(?:/|$))[A-Za-z0-9][A-Za-z0-9._/-]{0,511}$"
)
CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")
PRIVATE_PATH_RE = re.compile(
    r"(?:^|[\s\"'=])(?:~/|/Users/|/home/|/private/var/|file:///|[A-Za-z]:[\\/]|\\\\)",
    re.IGNORECASE,
)
SECRET_SHAPE_RE = re.compile(
    r"(?:sk-(?:ant-)?[A-Za-z0-9_-]{8,}|gh[pousr]_[A-Za-z0-9]{20,}|"
    r"github_pat_[A-Za-z0-9_]{20,}|Bearer\s+[A-Za-z0-9._\-/+=]{20,}|"
    r"-----BEGIN[ A-Z]*PRIVATE KEY-----)",
    re.IGNORECASE,
)
PROOF_TYPES = frozenset({"test", "runtime", "ui", "release", "document", "other"})
PROOF_DELIVERY = frozenset({"delivered", "not_delivered"})
OUTCOME_STATES = frozenset({"working", "needs_input", "blocked", "finished_with_proof", "not_delivered"})
CATEGORIES = frozenset({"product_choice", "security", "money", "external_communication", "irreversible_action"})


class DecisionInputError(ValueError):
    pass


def mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise DecisionInputError(f"{label} must be an object")
    return value


def text(value: Any, label: str, *, maximum: int = 280) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DecisionInputError(f"{label} must be a nonblank string")
    value = " ".join(value.split())
    if len(value) > maximum:
        raise DecisionInputError(f"{label} exceeds {maximum} characters")
    if (
        CONTROL_RE.search(value)
        or any(unicodedata.category(character) in {"Cc", "Cf"} for character in value)
        or unicodedata.normalize("NFC", value) != value
        or PRIVATE_PATH_RE.search(value)
        or SECRET_SHAPE_RE.search(value)
    ):
        raise DecisionInputError(f"{label} contains private or unsafe text")
    return value


def identifier(value: Any, label: str) -> str:
    value = text(value, label)
    if IDENTIFIER_RE.fullmatch(value) is None:
        raise DecisionInputError(f"{label} must be a public identifier")
    return value


def revision(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= MAX_REVISION:
        raise DecisionInputError(f"{label} must be a public integer")
    return value


def timestamp(value: Any, label: str) -> str:
    if not isinstance(value, str) or UTC_RE.fullmatch(value) is None:
        raise DecisionInputError(f"{label} must be an RFC3339 UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise DecisionInputError(f"{label} must be a real timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise DecisionInputError(f"{label} must be an RFC3339 UTC timestamp")
    return value


def locator(value: Any, label: str) -> str:
    value = text(value, label, maximum=512)
    if value.startswith("https://"):
        parsed = urlparse(value)
        if not parsed.netloc or parsed.username or parsed.password:
            raise DecisionInputError(f"{label} must be a public HTTPS or relative locator")
    elif RELATIVE_LOCATOR_RE.fullmatch(value) is None:
        raise DecisionInputError(f"{label} must be a public HTTPS or relative locator")
    return value


def outcome_document(value: Any) -> Mapping[str, Any]:
    document = mapping(value, "document")
    if document.get("schema") != OUTCOME_SCHEMA:
        raise DecisionInputError(f"document schema must equal {OUTCOME_SCHEMA}")
    if set(document) != {"schema", "revision", "updated_at", "outcome", "ask", "proof"}:
        raise DecisionInputError("document contains fields outside the Outcome contract")
    revision(document.get("revision"), "document.revision")
    timestamp(document.get("updated_at"), "document.updated_at")
    return document


def project_outcome(document: Mapping[str, Any]) -> dict[str, Any]:
    source = mapping(document.get("outcome"), "outcome")
    expected = {"id", "summary", "state", "current_move"}
    if set(source) != expected:
        raise DecisionInputError("outcome contains fields outside the Outcome contract")
    state = text(source.get("state"), "outcome.state", maximum=32)
    if state not in OUTCOME_STATES:
        raise DecisionInputError("outcome.state is not supported")
    return {
        "id": identifier(source.get("id"), "outcome.id"),
        "summary": text(source.get("summary"), "outcome.summary"),
        "state": state,
        "current_move": text(source.get("current_move"), "outcome.current_move"),
    }


def project_ask(document: Mapping[str, Any], outcome: Mapping[str, Any]) -> dict[str, Any] | None:
    raw = document.get("ask")
    if raw is None:
        if outcome["state"] == "needs_input":
            raise DecisionInputError("a needs_input Outcome requires an open A/B/C choice")
        return None
    source = mapping(raw, "ask")
    expected = {"id", "category", "question", "options", "state", "answer_option_id"}
    if set(source) != expected:
        raise DecisionInputError("ask contains fields outside the choice contract")
    if source.get("state") != "open" or outcome["state"] != "needs_input":
        raise DecisionInputError("only a needs_input Outcome may expose an open A/B/C choice")
    if source.get("answer_option_id") is not None:
        raise DecisionInputError("an open choice must not carry an answer")
    category = text(source.get("category"), "ask.category", maximum=32)
    if category not in CATEGORIES:
        raise DecisionInputError("ask.category is not supported")
    options = source.get("options")
    if not isinstance(options, Sequence) or isinstance(options, (str, bytes)) or len(options) != 3:
        raise DecisionInputError("an open choice must contain exactly A/B/C")
    projected = []
    seen = set()
    for index, raw_option in enumerate(options):
        option = mapping(raw_option, f"ask.options[{index}]")
        if set(option) != {"id", "label", "consequence"}:
            raise DecisionInputError(f"ask.options[{index}] contains fields outside the option contract")
        option_id = identifier(option.get("id"), f"ask.options[{index}].id")
        if option_id in seen:
            raise DecisionInputError("choice option IDs must be unique")
        seen.add(option_id)
        projected.append(
            {
                "id": option_id,
                "label": text(option.get("label"), f"ask.options[{index}].label", maximum=80),
                "consequence": text(option.get("consequence"), f"ask.options[{index}].consequence"),
            }
        )
    return {
        "id": identifier(source.get("id"), "ask.id"),
        "category": category,
        "question": text(source.get("question"), "ask.question"),
        "state": "open",
        "answer_option_id": None,
        "options": projected,
    }


def project_proof(document: Mapping[str, Any]) -> list[dict[str, Any]]:
    raw = document.get("proof")
    if not isinstance(raw, list) or len(raw) > 64:
        raise DecisionInputError("proof must be an array")
    projected = []
    for index, item in enumerate(raw):
        source = mapping(item, f"proof[{index}]")
        expected = {"id", "type", "locator", "verification_summary", "delivery"}
        if set(source) != expected:
            raise DecisionInputError(f"proof[{index}] contains fields outside the proof contract")
        proof_type = text(source.get("type"), f"proof[{index}].type", maximum=32)
        delivery = text(source.get("delivery"), f"proof[{index}].delivery", maximum=32)
        if proof_type not in PROOF_TYPES:
            raise DecisionInputError(f"proof[{index}].type is not supported")
        if delivery not in PROOF_DELIVERY:
            raise DecisionInputError(f"proof[{index}].delivery is not supported")
        projected.append(
            {
                "id": identifier(source.get("id"), f"proof[{index}].id"),
                "type": proof_type,
                "locator": locator(source.get("locator"), f"proof[{index}].locator"),
                "verification_summary": text(
                    source.get("verification_summary"),
                    f"proof[{index}].verification_summary",
                    maximum=500,
                ),
                "delivery": delivery,
            }
        )
    return projected


def _ensure_unique_ids(
    outcome: Mapping[str, Any],
    ask: Mapping[str, Any] | None,
    proof: list[Mapping[str, Any]],
) -> None:
    seen: dict[str, str] = {}

    def add(value: str, label: str) -> None:
        previous = seen.get(value)
        if previous is not None:
            raise DecisionInputError(f"{label} duplicates {previous}")
        seen[value] = label

    add(outcome["id"], "outcome.id")
    if ask is not None:
        add(ask["id"], "ask.id")
        for index, option in enumerate(ask["options"]):
            add(option["id"], f"ask.options[{index}].id")
    for index, item in enumerate(proof):
        add(item["id"], f"proof[{index}].id")


def project_decision(value: Any) -> dict[str, Any]:
    document = outcome_document(value)
    outcome = project_outcome(document)
    ask = project_ask(document, outcome)
    proof = project_proof(document)
    if outcome["state"] == "finished_with_proof" and not any(
        item["delivery"] == "delivered" for item in proof
    ):
        raise DecisionInputError("finished_with_proof requires delivered proof")
    _ensure_unique_ids(outcome, ask, proof)
    return {
        "schema": DECISION_SCHEMA,
        "revision": document["revision"],
        "updated_at": document["updated_at"],
        "outcome": outcome,
        "ask": ask,
        "proof": proof,
    }


def build_choice(value: Any, option_id: Any) -> dict[str, Any]:
    decision = project_decision(value)
    ask = decision["ask"]
    if ask is None:
        raise DecisionInputError("a choice requires an open A/B/C question")
    option_id = identifier(option_id, "option_id")
    if option_id not in {option["id"] for option in ask["options"]}:
        raise DecisionInputError("option_id is not present in the open choice")
    return {
        "schema": CHOICE_SCHEMA,
        "kind": "answer",
        "revision": decision["revision"],
        "outcome_id": decision["outcome"]["id"],
        "ask_id": ask["id"],
        "option_id": option_id,
    }


def receive_choice(value: Any, envelope: Any, *, updated_at: str | None = None) -> dict[str, Any]:
    decision = project_decision(value)
    choice = mapping(envelope, "choice")
    expected = {"schema", "kind", "revision", "outcome_id", "ask_id", "option_id"}
    if set(choice) != expected or choice.get("schema") != CHOICE_SCHEMA or choice.get("kind") != "answer":
        raise DecisionInputError("choice contains fields outside the closed choice contract")
    observed = revision(choice.get("revision"), "choice.revision")
    outcome_id = identifier(choice.get("outcome_id"), "choice.outcome_id")
    ask_id = identifier(choice.get("ask_id"), "choice.ask_id")
    option_id = identifier(choice.get("option_id"), "choice.option_id")
    ask = decision["ask"]
    if outcome_id != decision["outcome"]["id"] or ask is None or ask_id != ask["id"]:
        state, reason = "not_delivered", "identity_mismatch"
    elif option_id not in {option["id"] for option in ask["options"]}:
        state, reason = "not_delivered", "option_not_visible"
    elif observed != decision["revision"]:
        state, reason = "superseded", "stale_revision"
    else:
        state, reason = "received", "accepted"
    if updated_at is not None and UTC_RE.fullmatch(updated_at) is None:
        raise DecisionInputError("updated_at must be an RFC3339 UTC timestamp")
    return {
        "receipt": {
            "schema": RECEIPT_SCHEMA,
            "state": state,
            "reason": reason,
            "observed_revision": observed,
            "authority_revision": decision["revision"],
            "outcome_id": outcome_id,
            "ask_id": ask_id,
            "option_id": option_id,
        }
    }


__all__ = [
    "CHOICE_SCHEMA",
    "DECISION_SCHEMA",
    "DecisionInputError",
    "OUTCOME_SCHEMA",
    "RECEIPT_SCHEMA",
    "build_choice",
    "project_decision",
    "receive_choice",
]
