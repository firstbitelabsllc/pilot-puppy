from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent.parent


class IssueTemplateTests(unittest.TestCase):
    def test_public_templates_use_current_commands_and_docs(self) -> None:
        bug = (ROOT / ".github/ISSUE_TEMPLATE/bug-report.yml").read_text(encoding="utf-8")
        feature = (ROOT / ".github/ISSUE_TEMPLATE/feature-request.yml").read_text(encoding="utf-8")
        self.assertIn("pilot-puppy status", bug)
        self.assertIn("pilot-puppy host probe", bug)
        self.assertIn("docs/reference/plan-fields.md", feature)
        self.assertIn("init, status, browse, checkpoint, roster, route, host, doctor", feature)
        retired_loop = "pilot-puppy-" + "loop.sh"
        retired_checkpoint = "pilot-puppy-" + "checkpoint.sh"
        self.assertNotIn(retired_loop, bug + feature)
        self.assertNotIn(retired_checkpoint, bug + feature)
        self.assertNotIn("docs/reference/loop.md", feature)
        self.assertTrue((ROOT / "SKILL.md").is_file())
        self.assertTrue((ROOT / "docs/reference/plan-fields.md").is_file())


if __name__ == "__main__":
    unittest.main()
