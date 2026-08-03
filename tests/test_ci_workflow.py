"""Regression contract for the hosted Python quality gate."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
SECRET_WORKFLOW = ROOT / ".github" / "workflows" / "secret-scan.yml"


class CiWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")
        cls.secret_workflow = SECRET_WORKFLOW.read_text(encoding="utf-8")

    def test_python_lint_uses_a_pinned_tool_and_the_local_surface(self) -> None:
        self.assertIn("  python-lint:\n", self.workflow)
        self.assertIn("python-version: '3.12'", self.workflow)
        self.assertIn(
            'python -m pip install --disable-pip-version-check --no-input "ruff==0.15.20"',
            self.workflow,
        )
        self.assertIn("python -m ruff check scripts tests browser", self.workflow)

    def test_workflows_use_current_node24_action_pins(self) -> None:
        expected_ci = {
            "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
            "actions/setup-node@820762786026740c76f36085b0efc47a31fe5020",
            "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97",
        }
        expected_secret = {
            "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
            "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97",
        }
        for action in expected_ci:
            self.assertIn(action, self.workflow)
        for action in expected_secret:
            self.assertIn(action, self.secret_workflow)
        self.assertIn(
            "actions/cache@55cc8345863c7cc4c66a329aec7e433d2d1c52a9",
            self.secret_workflow,
        )
        for retired in (
            "11bd71901bbe5b1630ceea73d27597364c9af683",
            "49933ea5288caeca8642d1e84afbd3f7d6820020",
            "a26af69be951a213d495a4c3e4e4022e16d87065",
            "0057852bfaa89a56745cba8c7296529d2fc39830",
        ):
            self.assertNotIn(retired, self.workflow + self.secret_workflow)


if __name__ == "__main__":
    unittest.main()
