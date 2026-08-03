"""Regression contract for the hosted Python quality gate."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"


class CiWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_python_lint_uses_a_pinned_tool_and_the_local_surface(self) -> None:
        self.assertIn("  python-lint:\n", self.workflow)
        self.assertIn("python-version: '3.12'", self.workflow)
        self.assertIn(
            'python -m pip install --disable-pip-version-check --no-input "ruff==0.15.20"',
            self.workflow,
        )
        self.assertIn("python -m ruff check scripts tests browser", self.workflow)


if __name__ == "__main__":
    unittest.main()
