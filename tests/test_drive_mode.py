"""Focused tests for the bounded Vidux Drive / 90 semantic client."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MODULE = ROOT / "browser" / "drive_mode.py"
SPEC = importlib.util.spec_from_file_location("vidux_drive_mode", MODULE)
assert SPEC and SPEC.loader
drive = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = drive
SPEC.loader.exec_module(drive)


def document() -> dict:
    options = [
        {"id": "ship-now", "label": "Ship now", "consequence": "Use the accepted proof."},
        {"id": "hold-review", "label": "Hold for review", "consequence": "Keep the row open."},
        {"id": "run-more", "label": "Run more checks", "consequence": "Spend another bounded cycle."},
        {"id": "write-note", "label": "Write a note", "consequence": "Record the uncertainty."},
        {"id": "stop-work", "label": "Stop work", "consequence": "Leave the outcome unchanged."},
    ]
    return {
        "schema": "vidux.outcome.v1",
        "revision": 4,
        "updated_at": "2026-08-01T18:00:00Z",
        "outcome": {
            "id": "publish-notes",
            "summary": "Ship accurate notes for the next tagged build.",
            "state": "needs_input",
            "current_move": "Choose the next bounded move.",
        },
        "ask": {
            "id": "choose-release",
            "category": "product_choice",
            "question": "What should happen next?",
            "options": options,
            "state": "open",
            "answer_option_id": None,
        },
        "steers": [
            {
                "id": "old-direction",
                "outcome_id": "publish-notes",
                "summary": "The earlier direction was replaced.",
                "state": "superseded",
                "proof_ref": None,
            }
        ],
        "proof": [
            {
                "id": "notes-test",
                "type": "test",
                "locator": "tests/test_drive_mode.py",
                "verification_summary": "Drive contract tests pass.",
                "delivery": "delivered",
            }
        ],
    }


class DriveModeTests(unittest.TestCase):
    def test_projection_is_bounded_and_keeps_superseded_steer_visible(self):
        source = document()
        original = copy.deepcopy(source)
        result = drive.project_drive(source)
        self.assertEqual(result["schema"], "vidux.drive.v1")
        self.assertEqual([option["id"] for option in result["ask"]["options"]], [
            "ship-now",
            "hold-review",
            "run-more",
        ])
        self.assertEqual(result["ask"]["options_total"], 5)
        self.assertTrue(result["ask"]["options_truncated"])
        self.assertEqual(result["steers"][0]["state"], "superseded")
        self.assertIsNone(result["active_steer_id"])
        self.assertEqual(source, original)

    def test_choice_is_closed_typed_and_does_not_include_free_text(self):
        result = drive.build_choice(document(), "hold-review")
        self.assertEqual(
            result,
            {
                "schema": "vidux.drive-steer.v1",
                "kind": "answer",
                "outcome_id": "publish-notes",
                "ask_id": "choose-release",
                "option_id": "hold-review",
            },
        )
        self.assertNotIn("message", result)
        self.assertNotIn("prompt", result)
        self.assertNotIn("provider", result)

    def test_unknown_choice_is_rejected(self):
        with self.assertRaises(drive.DriveInputError):
            drive.build_choice(document(), "invented-choice")

    def test_closed_ask_cannot_receive_a_choice(self):
        source = document()
        source["ask"]["state"] = "superseded"
        source["outcome"]["state"] = "working"
        with self.assertRaises(drive.DriveInputError):
            drive.build_choice(source, "ship-now")

    def test_projection_allowlists_semantic_fields(self):
        source = document()
        source["provider"] = "cursor"
        source["transcript"] = "do not copy this"
        result = drive.project_drive(source)
        encoded = json.dumps(result, sort_keys=True)
        self.assertNotIn("cursor", encoded)
        self.assertNotIn("do not copy this", encoded)


if __name__ == "__main__":
    unittest.main()
