"""Focused tests for one bounded Pilot Puppy A/B/C decision."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from browser import decision_mode as decision


ROOT = Path(__file__).resolve().parent.parent


def document() -> dict:
    return json.loads((ROOT / "examples" / "outcome-choice" / "example.json").read_text(encoding="utf-8"))


class DecisionModeTests(unittest.TestCase):
    def test_projection_is_bounded_and_pure(self) -> None:
        source = document()
        original = copy.deepcopy(source)
        result = decision.project_decision(source)
        self.assertEqual(result["schema"], "pilot-puppy.decision.v1")
        self.assertEqual(len(result["ask"]["options"]), 3)
        self.assertEqual(source, original)
        self.assertEqual(
            set(result),
            {"schema", "revision", "updated_at", "outcome", "ask", "proof"},
        )

    def test_closed_document_rejects_implementation_fields(self) -> None:
        source = document()
        source["provider"] = "example"
        with self.assertRaises(decision.DecisionInputError):
            decision.project_decision(source)

    def test_proof_projection_is_closed_bounded_and_public_safe(self) -> None:
        for mutation in (
            lambda source: source["proof"][0].update({"extra": "field"}),
            lambda source: source["proof"][0].update({"delivery": "unknown"}),
            lambda source: source["proof"][0].update({"locator": "/Users/person/private"}),
            lambda source: source["proof"][0].update({"verification_summary": "x" * 501}),
        ):
            with self.subTest(mutation=mutation):
                source = document()
                mutation(source)
                with self.assertRaises(decision.DecisionInputError):
                    decision.project_decision(source)

    def test_nested_outcome_and_choice_contracts_are_closed(self) -> None:
        mutations = (
            lambda source: source["outcome"].update({"implementation": "hidden"}),
            lambda source: source["outcome"].update({"state": "unknown"}),
            lambda source: source["ask"].update({"answer_option_id": "full-review"}),
            lambda source: source["ask"].update({"extra": "field"}),
            lambda source: source["ask"]["options"][0].update({"extra": "field"}),
            lambda source: source["ask"].update({"category": "provider"}),
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                source = document()
                mutation(source)
                with self.assertRaises(decision.DecisionInputError):
                    decision.project_decision(source)

    def test_state_and_identifier_invariants_match_validator(self) -> None:
        mutations = (
            lambda source: (
                source["outcome"].update({"state": "finished_with_proof"}),
                source.__setitem__("ask", None),
                source["proof"][0].update({"delivery": "not_delivered"}),
            ),
            lambda source: source["ask"].update({"id": source["outcome"]["id"]}),
            lambda source: source["ask"]["options"][0].update({"id": source["proof"][0]["id"]}),
            lambda source: source["proof"].append(copy.deepcopy(source["proof"][0])),
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                source = document()
                mutation(source)
                with self.assertRaises(decision.DecisionInputError):
                    decision.project_decision(source)

    def test_finished_state_accepts_delivered_proof(self) -> None:
        source = document()
        source["outcome"]["state"] = "finished_with_proof"
        source["ask"] = None
        result = decision.project_decision(source)
        self.assertEqual(result["outcome"]["state"], "finished_with_proof")
        self.assertEqual(result["proof"][0]["delivery"], "delivered")

    def test_scalar_bounds_match_canonical_validator(self) -> None:
        mutations = (
            lambda source: source.update(updated_at="2026-99-99T99:99:99Z"),
            lambda source: source["outcome"].update({"summary": "cafe\u0301"}),
            lambda source: source["outcome"].update({"summary": "safe\u200btext"}),
            lambda source: source["ask"]["options"][0].update({"label": "x" * 81}),
            lambda source: source["proof"][0].update({"locator": "relative path with spaces"}),
            lambda source: source["proof"][0].update({"locator": "ftp://example.com/proof"}),
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                source = document()
                mutation(source)
                with self.assertRaises(decision.DecisionInputError):
                    decision.project_decision(source)

    def test_https_locator_is_allowed(self) -> None:
        source = document()
        source["proof"][0]["locator"] = "https://example.com/proof"
        result = decision.project_decision(source)
        self.assertEqual(result["proof"][0]["locator"], "https://example.com/proof")

    def test_privacy_and_json_array_bounds_match_canonical_validator(self) -> None:
        fragmented = json.loads(
            (ROOT / "examples" / "outcome-choice" / "privacy-fragmented.invalid.json").read_text(encoding="utf-8")
        )
        with self.assertRaises(decision.DecisionInputError):
            decision.project_decision(fragmented)
        for value in (
            "/tmp/private/file",
            "path:/tmp/private/file",
            "see(/tmp/private/file)",
            "$HOME/private",
            "xoxb-1234567890",
            "AKIA1234567890123456",
        ):
            with self.subTest(value=value):
                source = document()
                source["outcome"]["current_move"] = value
                with self.assertRaises(decision.DecisionInputError):
                    decision.project_decision(source)
        source = document()
        source["ask"]["options"] = tuple(source["ask"]["options"])
        with self.assertRaises(decision.DecisionInputError):
            decision.project_decision(source)

    def test_choice_is_closed_and_typed(self) -> None:
        result = decision.build_choice(document(), "full-review")
        self.assertEqual(
            result,
            {
                "schema": "pilot-puppy.decision-choice.v1",
                "kind": "answer",
                "revision": 3,
                "outcome_id": "ship-release-notes",
                "ask_id": "choose-review-depth",
                "option_id": "full-review",
            },
        )

    def test_unknown_choice_is_rejected(self) -> None:
        with self.assertRaises(decision.DecisionInputError):
            decision.build_choice(document(), "invented-choice")

    def test_current_choice_is_received_without_mutating_authority(self) -> None:
        source = document()
        original = copy.deepcopy(source)
        result = decision.receive_choice(source, decision.build_choice(source, "focused-review"))
        self.assertEqual(result["receipt"]["state"], "received")
        self.assertEqual(result["receipt"]["reason"], "accepted")
        self.assertEqual(result["receipt"]["authority_revision"], 3)
        self.assertEqual(source, original)
        self.assertEqual(
            set(result["receipt"]),
            {"schema", "state", "reason", "observed_revision", "authority_revision", "outcome_id", "ask_id", "option_id"},
        )

    def test_stale_choice_is_superseded(self) -> None:
        choice = decision.build_choice(document(), "focused-review")
        source = document()
        source["revision"] = 4
        result = decision.receive_choice(source, choice)
        self.assertEqual(result["receipt"]["state"], "superseded")
        self.assertEqual(result["receipt"]["reason"], "stale_revision")

    def test_identity_or_hidden_option_is_not_delivered(self) -> None:
        choice = decision.build_choice(document(), "focused-review")
        choice["outcome_id"] = "other-outcome"
        result = decision.receive_choice(document(), choice)
        self.assertEqual(result["receipt"]["reason"], "identity_mismatch")
        choice = decision.build_choice(document(), "focused-review")
        choice["option_id"] = "hidden-option"
        result = decision.receive_choice(document(), choice)
        self.assertEqual(result["receipt"]["reason"], "option_not_visible")

    def test_choice_rejects_extra_fields(self) -> None:
        choice = decision.build_choice(document(), "focused-review")
        choice["message"] = "extra"
        with self.assertRaises(decision.DecisionInputError):
            decision.receive_choice(document(), choice)


if __name__ == "__main__":
    unittest.main()
