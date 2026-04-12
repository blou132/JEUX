import argparse
import unittest

from main import build_parser, validate_args


class CliValidationTests(unittest.TestCase):
    def _valid_args(self, **overrides: object) -> argparse.Namespace:
        data = {
            "steps": 100,
            "dt": 1.0,
            "log_interval": 10,
            "seed": 42,
            "runs": 1,
            "seed_step": 1,
            "batch_param": None,
            "batch_values": None,
            "batch_runs": 3,
            "batch_history_path": None,
            "batch_id": None,
            "export_path": None,
            "export_format": "json",
            "map_width": 60.0,
            "map_height": 40.0,
            "creatures": 20,
            "initial_food": 50,
            "min_food": 30,
            "energy_drain_rate": 1.2,
            "movement_speed": 1.0,
            "eat_rate": 24.0,
            "hunger_threshold": 0.6,
            "reproduction_threshold": 58.0,
            "reproduction_cost": 12.0,
            "reproduction_distance": 15.0,
            "reproduction_min_age": 0.0,
            "mutation_variation": 0.1,
            "food_memory_duration": 8.0,
            "danger_memory_duration": 6.0,
            "food_memory_recall_distance": 8.0,
            "danger_memory_avoid_distance": 5.0,
            "social_influence_distance": 6.0,
            "social_follow_strength": 0.35,
            "social_flee_boost_per_neighbor": 0.15,
            "social_flee_boost_max": 0.45,
        }
        data.update(overrides)
        return argparse.Namespace(**data)

    def test_valid_args_pass_validation(self) -> None:
        validate_args(self._valid_args())

    def test_invalid_core_loop_args_raise(self) -> None:
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(steps=0))
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(dt=0.0))
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(log_interval=0))

    def test_invalid_multi_run_args_raise(self) -> None:
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(runs=0))
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(seed_step=0))

    def test_invalid_batch_args_raise(self) -> None:
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(batch_runs=0))
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(batch_values="1.0,1.2"))
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(batch_param="energy_drain_rate", batch_values=None))
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(batch_param="energy_drain_rate", batch_values="abc"))

    def test_batch_memory_param_is_supported(self) -> None:
        validate_args(
            self._valid_args(
                batch_param="food_memory_duration",
                batch_values="0,8",
            )
        )

    def test_invalid_batch_history_args_raise(self) -> None:
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(batch_history_path="history.json"))
        with self.assertRaises(ValueError):
            validate_args(
                self._valid_args(
                    batch_param="energy_drain_rate",
                    batch_values="1.0,1.2",
                    batch_history_path="   ",
                )
            )
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(batch_id="exp_001"))
        with self.assertRaises(ValueError):
            validate_args(
                self._valid_args(
                    batch_param="energy_drain_rate",
                    batch_values="1.0,1.2",
                    batch_history_path="history.json",
                    batch_id="   ",
                )
            )

    def test_invalid_export_args_raise(self) -> None:
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(export_path="   "))
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(export_format="xml"))

    def test_invalid_world_and_population_args_raise(self) -> None:
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(map_width=0.0))
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(map_height=0.0))
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(creatures=0))
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(initial_food=-1))

    def test_invalid_ai_and_energy_args_raise(self) -> None:
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(energy_drain_rate=-0.1))
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(movement_speed=-0.1))
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(eat_rate=-0.1))
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(hunger_threshold=-0.1))
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(hunger_threshold=1.1))

    def test_invalid_memory_args_raise(self) -> None:
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(food_memory_duration=-0.1))
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(danger_memory_duration=-0.1))
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(food_memory_recall_distance=-0.1))
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(danger_memory_avoid_distance=-0.1))

    def test_social_cli_args_parse_and_validate(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "--steps",
                "10",
                "--social-influence-distance",
                "0",
                "--social-follow-strength",
                "0",
                "--social-flee-boost-per-neighbor",
                "0",
                "--social-flee-boost-max",
                "0",
            ]
        )
        validate_args(args)

    def test_invalid_social_args_raise(self) -> None:
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(social_influence_distance=-0.1))
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(social_follow_strength=-0.1))
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(social_flee_boost_per_neighbor=-0.1))
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(social_flee_boost_max=-0.1))

    def test_invalid_reproduction_and_mutation_args_raise(self) -> None:
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(reproduction_threshold=-1.0))
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(reproduction_cost=-1.0))
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(reproduction_distance=-1.0))
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(reproduction_min_age=-1.0))
        with self.assertRaises(ValueError):
            validate_args(self._valid_args(mutation_variation=-0.1))


if __name__ == "__main__":
    unittest.main()

