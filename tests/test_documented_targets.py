"""Keep shipped Pilot Puppy instructions aligned with shipped executable targets."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DOCUMENTS = (
    ROOT / "README.md",
    ROOT / "SKILL.md",
    *sorted((ROOT / "docs").rglob("*.md")),
    *sorted((ROOT / "guides").rglob("*.md")),
)
PUBLIC_TEMPLATES = tuple(sorted((ROOT / ".github" / "ISSUE_TEMPLATE").glob("*.yml")))
RETIRED_PUBLIC_REFERENCES = (
    "pilot-puppy-loop.sh",
    "pilot-puppy-checkpoint.sh",
    "docs/reference/loop.md",
    "DOCTRINE.md",
)
TARGET = re.compile(
    r"(?<![A-Za-z0-9_./-])"
    r"((?:assets|bin|browser|docs|examples|guides|hooks|references|schemas|scripts|tests)"
    r"/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*/?)"
)


class DocumentedTargetTests(unittest.TestCase):
    def test_documented_repository_targets_exist(self):
        missing: list[str] = []
        documented: set[str] = set()

        for document in DOCUMENTS:
            text = document.read_text(encoding="utf-8")
            for match in TARGET.finditer(text):
                target = match.group(1)
                documented.add(target)
                if not (ROOT / target).exists():
                    line = text.count("\n", 0, match.start()) + 1
                    missing.append(f"{document.relative_to(ROOT)}:{line}: {target}")

        self.assertTrue(documented, "expected at least one documented target")
        self.assertEqual([], missing, "documented targets must exist in this checkout")

    def test_public_issue_templates_use_current_product_surfaces(self):
        stale: list[str] = []
        for document in PUBLIC_TEMPLATES:
            text = document.read_text(encoding="utf-8")
            for reference in RETIRED_PUBLIC_REFERENCES:
                if reference in text:
                    stale.append(f"{document.relative_to(ROOT)}: {reference}")
        self.assertEqual([], stale, "public issue templates must not teach retired surfaces")


if __name__ == "__main__":
    unittest.main()
