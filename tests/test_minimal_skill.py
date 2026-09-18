from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "minimal"


class MinimalSkillTest(unittest.TestCase):
    def test_minimal_contract_preserves_scope_safety_and_verification(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("explicit-only, cross-agent skill", skill)
        self.assertIn("Minimize implementation complexity, not the user's requirements", skill)
        self.assertIn("do not add a persona or intensity modes", skill)
        self.assertIn("Do not register always-on lifecycle callbacks", skill)
        self.assertIn("inject persistent behavior, or create global state", skill)
        self.assertIn("actual execution and data flow", skill)
        self.assertIn("smallest root-cause fix", skill)
        self.assertIn("Reuse existing project code", skill)
        self.assertIn("language standard library", skill)
        self.assertIn("native platform capability", skill)
        self.assertIn("already-installed dependency", skill)
        self.assertIn("Graft retrieval, graph, or blast-radius capabilities", skill)
        self.assertIn("ordinary repository search and source reading", skill)
        self.assertIn("Never simplify away explicit user requirements", skill)
        self.assertIn("security controls", skill)
        self.assertIn("data-loss prevention", skill)
        self.assertIn("smallest decisive verification", skill)
        self.assertIn("another explicitly active workflow defines authority", skill)
        self.assertIn("do not search for, install, require, or invoke another skill", skill)
        self.assertIn("does not authorize dependency or system installation, commits, pushes", skill)

    def test_minimal_package_is_explicit_only_and_unbranded(self):
        adapter = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        metadata = json.loads((SKILL_ROOT / "metadata.json").read_text(encoding="utf-8"))
        package_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(SKILL_ROOT.rglob("*"))
            if path.is_file()
        )

        self.assertIn('display_name: "Minimal"', adapter)
        self.assertIn("allow_implicit_invocation: false", adapter)
        self.assertIn("$minimal", adapter)
        self.assertEqual(metadata["name"], "minimal")
        self.assertEqual(metadata["version"], "0.1.0")
        self.assertEqual(metadata["references"], [])
        for forbidden in ("Ponytail", "completion-loop"):
            self.assertNotIn(forbidden, package_text)


if __name__ == "__main__":
    unittest.main()
