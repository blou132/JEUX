import unittest

from ui import format_population_dynamics


class DebugReadabilityTests(unittest.TestCase):
    def test_growth_dynamics_is_explicit(self) -> None:
        stats = {
            "births_last_tick": 3,
            "deaths_last_tick": 1,
            "alive": 12,
            "food_remaining": 500.0,
            "avg_energy": 55.0,
            "death_causes_last_tick": {"starvation": 1, "exhaustion": 0, "unknown": 0},
        }
        previous = {"alive": 10}

        text = format_population_dynamics(stats, previous)

        self.assertIn("dynamique:croissance", text)
        self.assertIn("delta_log_vivants:+2", text)
        self.assertIn("pression_nourriture:faible", text)

    def test_decline_dynamics_highlights_mortality_cause(self) -> None:
        stats = {
            "births_last_tick": 0,
            "deaths_last_tick": 4,
            "alive": 8,
            "food_remaining": 40.0,
            "avg_energy": 12.0,
            "death_causes_last_tick": {"starvation": 4, "exhaustion": 0, "unknown": 0},
        }
        previous = {"alive": 12}

        text = format_population_dynamics(stats, previous)

        self.assertIn("dynamique:declin", text)
        self.assertIn("dominante:faim", text)
        self.assertIn("energie:basse", text)


if __name__ == "__main__":
    unittest.main()