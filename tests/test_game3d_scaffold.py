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
            GAME3D / "scripts" / "entities" / "BruteMonster.gd",
            GAME3D / "scripts" / "entities" / "RangedMonster.gd",
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
        self.assertIn("poi", content)
        self.assertIn("nova", content)
        self.assertIn("brute", content)
        self.assertIn("ranged", content)
        self.assertIn("control", content)
        self.assertIn("slow", content)
        self.assertIn("fighter", content)
        self.assertIn("mage", content)
        self.assertIn("scout", content)
        self.assertIn("champion", content)
        self.assertIn("rally", content)

    def test_magic_system_has_second_spell(self):
        content = (GAME3D / "scripts" / "magic" / "MagicSystem.gd").read_text(encoding="utf-8")
        self.assertIn("func try_cast_nova", content)
        self.assertIn('register_cast(caster, null, "nova")', content)
        self.assertIn("func try_cast_control", content)
        self.assertIn('register_cast(caster, target, "control")', content)

    def test_world_manager_has_poi(self):
        content = (GAME3D / "scripts" / "world" / "WorldManager.gd").read_text(encoding="utf-8")
        self.assertIn('"name": "camp"', content)
        self.assertIn('"name": "ruins"', content)
        self.assertIn("get_poi_guidance", content)
        self.assertIn("update_poi_runtime", content)
        self.assertIn("trigger_poi_entry_effect", content)
        self.assertIn("domination_changed", content)
        self.assertIn("poi_influence_activation_time", content)
        self.assertIn("get_active_poi_influences", content)
        self.assertIn("influence_activated", content)

    def test_debug_overlay_has_poi_status_labels(self):
        content = (GAME3D / "scripts" / "ui" / "DebugOverlay.gd").read_text(encoding="utf-8")
        self.assertIn("domine_humains", content)
        self.assertIn("domine_monstres", content)
        self.assertIn("conteste", content)
        self.assertIn("POI influence", content)
        self.assertIn("influence:off", content)
        self.assertIn("Champions:", content)
        self.assertIn("Rally:", content)

    def test_sandbox_has_ranged_spawn_ratio(self):
        content = (GAME3D / "scripts" / "sandbox" / "SandboxSystems.gd").read_text(encoding="utf-8")
        self.assertIn("ranged_spawn_ratio", content)
        self.assertIn("RangedMonster.new()", content)

    def test_ai_has_ranged_reposition_logic(self):
        content = (GAME3D / "scripts" / "ai" / "AgentAI.gd").read_text(encoding="utf-8")
        self.assertIn("ranged_monster", content)
        self.assertIn('"state": "reposition"', content)
        self.assertIn('"state": "cast_control"', content)
        self.assertIn("magic_usage_bias", content)
        self.assertIn("control_usage_bias", content)
        self.assertIn('"state": "rally"', content)
        self.assertIn("rally_regroup", content)
        self.assertIn("rally_pressure", content)

    def test_human_agent_has_roles(self):
        content = (GAME3D / "scripts" / "entities" / "HumanAgent.gd").read_text(encoding="utf-8")
        self.assertIn('assign_role(role: String)', content)
        self.assertIn('"fighter"', content)
        self.assertIn('"mage"', content)
        self.assertIn('"scout"', content)

    def test_sandbox_assigns_human_roles(self):
        content = (GAME3D / "scripts" / "sandbox" / "SandboxSystems.gd").read_text(encoding="utf-8")
        self.assertIn("fighter_role_ratio", content)
        self.assertIn("mage_role_ratio", content)
        self.assertIn("scout_role_ratio", content)
        self.assertIn("assign_role(_pick_human_role())", content)

    def test_actor_has_progression_fields(self):
        content = (GAME3D / "scripts" / "entities" / "Actor.gd").read_text(encoding="utf-8")
        self.assertIn("var progress_xp: float", content)
        self.assertIn("var level: int", content)
        self.assertIn("var max_level: int", content)
        self.assertIn("award_progress_xp", content)
        self.assertIn("_check_level_up", content)
        self.assertIn("var kill_count: int", content)
        self.assertIn("var is_champion: bool", content)
        self.assertIn("champion_tag()", content)
        self.assertIn("is_ready_for_champion", content)
        self.assertIn("promote_to_champion", content)
        self.assertIn("rally_leader_id", content)
        self.assertIn("rally_bonus_active", content)
        self.assertIn('"rally":', content)

    def test_game_loop_exposes_progression_runtime_metrics(self):
        content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.assertIn("const XP_ON_HIT", content)
        self.assertIn("const XP_ON_CAST", content)
        self.assertIn("const XP_ON_KILL", content)
        self.assertIn("register_level_up", content)
        self.assertIn('"level_counts"', content)
        self.assertIn('"level_ups_total"', content)
        self.assertIn("avg_level", content)

    def test_game_loop_exposes_poi_influence_runtime_metrics(self):
        content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.assertIn("POI_INFLUENCE_ENERGY_REGEN_PER_SEC", content)
        self.assertIn("POI_INFLUENCE_XP_GAIN", content)
        self.assertIn("_apply_poi_influences", content)
        self.assertIn("poi_influence_activation_events_total", content)
        self.assertIn("poi_influence_xp_grants_total", content)

    def test_game_loop_has_champion_metrics_and_promotion_hooks(self):
        content = (GAME3D / "scripts" / "core" / "GameLoop.gd").read_text(encoding="utf-8")
        self.assertIn("CHAMPION_MIN_LEVEL", content)
        self.assertIn("CHAMPION_MIN_KILLS", content)
        self.assertIn("CHAMPION_MAX_RATIO", content)
        self.assertIn("champion_promotions_total", content)
        self.assertIn("_try_promote_champion", content)
        self.assertIn("_scan_for_champion_promotion", content)
        self.assertIn('"champion_alive_total"', content)
        self.assertIn("rally_groups_formed_total", content)
        self.assertIn("rally_followers_active", content)
        self.assertIn("_update_rally_runtime", content)


if __name__ == "__main__":
    unittest.main()
