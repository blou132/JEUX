import argparse
import unittest

from main import validate_args


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
