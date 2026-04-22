from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GAME3D = ROOT / "game3d"


class TestGame3DScaffold(unittest.TestCase):
    def test_required_files_exist(self):
        required = [
            GAME3D / "project.godot",
            GAME3D / "scenes" / "MainSandbox.tscn",
            GAME3D / "scripts" / "core" / "GameLoop.gd",
            GAME3D / "scripts" / "world" / "WorldManager.gd",
            GAME3D / "scripts" / "entities" / "Actor.gd",
            GAME3D / "scripts" / "entities" / "HumanAgent.gd",
            GAME3D / "scripts" / "entities" / "MonsterAgent.gd",
            GAME3D / "scripts" / "ai" / "AgentAI.gd",
            GAME3D / "scripts" / "combat" / "CombatSystem.gd",
            GAME3D / "scripts" / "magic" / "MagicSystem.gd",
            GAME3D / "scripts" / "sandbox" / "SandboxSystems.gd",
            GAME3D / "scripts" / "ui" / "DebugOverlay.gd",
        ]

        for path in required:
            self.assertTrue(path.exists(), f"Missing file: {path}")

    def test_project_targets_main_scene(self):
        content = (GAME3D / "project.godot").read_text(encoding="utf-8")
        self.assertIn('run/main_scene="res://scenes/MainSandbox.tscn"', content)

    def test_main_scene_wires_core_systems(self):
        content = (GAME3D / "scenes" / "MainSandbox.tscn").read_text(encoding="utf-8")
        required_fragments = [
            "scripts/core/GameLoop.gd",
            "scripts/world/WorldManager.gd",
            "scripts/combat/CombatSystem.gd",
            "scripts/magic/MagicSystem.gd",
            "scripts/sandbox/SandboxSystems.gd",
            "scripts/ui/DebugOverlay.gd",
        ]
        for fragment in required_fragments:
            self.assertIn(fragment, content)

    def test_readme_mentions_new_3d_direction(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8").lower()
        self.assertIn("game3d", content)
        self.assertIn("legacy python", content)


if __name__ == "__main__":
    unittest.main()
