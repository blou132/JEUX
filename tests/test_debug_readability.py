import unittest

from ui import format_population_dynamics


class DebugReadabilityTests(unittest.TestCase):
    def test_growth_dynamics_is_explicit(self) -> None:
        stats = {
            "births_last_tick": 3,
            "deaths_last_tick": 1,
            "total_births": 10,
            "total_deaths": 2,
            "alive": 12,
            "food_remaining": 500.0,
            "avg_energy": 55.0,
            "death_causes_last_tick": {"starvation": 1, "exhaustion": 0, "unknown": 0},
            "death_causes_total": {"starvation": 2, "exhaustion": 0, "unknown": 0},
        }
        previous = {
            "alive": 10,
            "total_births": 7,
            "total_deaths": 1,
            "death_causes_total": {"starvation": 1, "exhaustion": 0, "unknown": 0},
        }

        text = format_population_dynamics(stats, previous)

        self.assertIn("dynamique_log:croissance", text)
        self.assertIn("dynamique_tick:croissance", text)
        self.assertIn("delta_log_vivants:+2", text)
        self.assertIn("net_log_naissances_deces:+2", text)
        self.assertIn("pression_nourriture:faible", text)
        self.assertIn("dist_menace_moy_tick:n/a", text)
        self.assertIn("memoire_freq_tick:utile=", text)
        self.assertIn("memoire_effet_tick:utile=", text)
    def test_decline_dynamics_highlights_mortality_cause(self) -> None:
        stats = {
            "births_last_tick": 0,
            "deaths_last_tick": 4,
            "total_births": 3,
            "total_deaths": 6,
            "alive": 8,
            "food_remaining": 40.0,
            "avg_energy": 12.0,
            "death_causes_last_tick": {"starvation": 4, "exhaustion": 0, "unknown": 0},
            "death_causes_total": {"starvation": 6, "exhaustion": 0, "unknown": 0},
        }
        previous = {
            "alive": 12,
            "total_births": 3,
            "total_deaths": 2,
            "death_causes_total": {"starvation": 2, "exhaustion": 0, "unknown": 0},
        }

        text = format_population_dynamics(stats, previous)

        self.assertIn("dynamique_log:declin", text)
        self.assertIn("dynamique_tick:declin", text)
        self.assertIn("dominante_log:faim", text)
        self.assertIn("energie:basse", text)


if __name__ == "__main__":
    unittest.main()


