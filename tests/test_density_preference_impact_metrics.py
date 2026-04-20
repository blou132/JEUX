import unittest

from debug_tools import (
    build_final_run_summary,
    build_multi_run_summary,
    create_proto_temporal_tracker,
)
from ui import format_final_run_summary, format_multi_run_summary


class DensityPreferenceImpactMetricsTests(unittest.TestCase):
    def test_final_summary_includes_density_preference_impact_metrics(self) -> None:
        tracker = create_proto_temporal_tracker()
        final_stats = {
            "avg_density_preference": 1.02,
            "std_density_preference": 0.11,
            "density_preference_guided_usage_bias_total": 0.05,
            "total_density_preference_guided_moves": 20,
            "total_density_preference_seek_moves": 12,
            "total_density_preference_avoid_moves": 8,
            "density_preference_seek_usage_per_tick_total": 0.3,
            "density_preference_avoid_usage_per_tick_total": 0.2,
            "density_preference_seek_share_total": 0.6,
            "density_preference_avoid_share_total": 0.4,
            "density_preference_seek_users_avg_total": 1.08,
            "density_preference_seek_usage_bias_total": 0.06,
            "density_preference_avoid_users_avg_total": 0.94,
            "density_preference_avoid_usage_bias_total": -0.08,
            "avg_density_preference_neighbor_count_total": 2.7,
            "avg_density_preference_center_distance_delta_total": 0.13,
        }

        summary = build_final_run_summary(final_stats, tracker)
        trait_impact = summary["trait_impact"]

        self.assertAlmostEqual(float(trait_impact["density_preference_mean"]), 1.02)
        self.assertAlmostEqual(float(trait_impact["density_preference_std"]), 0.11)
        self.assertAlmostEqual(float(trait_impact["density_preference_guided_bias"]), 0.05)
        self.assertEqual(int(trait_impact["density_preference_guided_total"]), 20)
        self.assertEqual(int(trait_impact["density_preference_seek_total"]), 12)
        self.assertEqual(int(trait_impact["density_preference_avoid_total"]), 8)
        self.assertAlmostEqual(float(trait_impact["density_preference_seek_usage_per_tick"]), 0.3)
        self.assertAlmostEqual(float(trait_impact["density_preference_avoid_usage_per_tick"]), 0.2)
        self.assertAlmostEqual(float(trait_impact["density_preference_seek_share"]), 0.6)
        self.assertAlmostEqual(float(trait_impact["density_preference_avoid_share"]), 0.4)
        self.assertAlmostEqual(float(trait_impact["density_preference_seek_users_avg"]), 1.08)
        self.assertAlmostEqual(float(trait_impact["density_preference_seek_usage_bias"]), 0.06)
        self.assertAlmostEqual(float(trait_impact["density_preference_avoid_users_avg"]), 0.94)
        self.assertAlmostEqual(float(trait_impact["density_preference_avoid_usage_bias"]), -0.08)
        self.assertAlmostEqual(float(trait_impact["density_preference_neighbor_count_avg"]), 2.7)
        self.assertAlmostEqual(float(trait_impact["density_preference_center_distance_delta"]), 0.13)

    def test_multi_run_summary_aggregates_density_preference_impact_metrics(self) -> None:
        run_results = [
            {
                "seed": 1,
                "extinct": False,
                "max_generation": 3,
                "final_alive": 12,
                "run_summary": {
                    "trait_impact": {
                        "density_preference_mean": 1.05,
                        "density_preference_std": 0.10,
                        "density_preference_guided_bias": 0.04,
                        "density_preference_guided_total": 10,
                        "density_preference_seek_total": 7,
                        "density_preference_avoid_total": 3,
                        "density_preference_seek_usage_per_tick": 0.25,
                        "density_preference_avoid_usage_per_tick": 0.11,
                        "density_preference_seek_share": 0.7,
                        "density_preference_avoid_share": 0.3,
                        "density_preference_seek_users_avg": 1.09,
                        "density_preference_seek_usage_bias": 0.05,
                        "density_preference_avoid_users_avg": 0.93,
                        "density_preference_avoid_usage_bias": -0.07,
                        "density_preference_neighbor_count_avg": 2.5,
                        "density_preference_center_distance_delta": 0.12,
                    }
                },
            },
            {
                "seed": 2,
                "extinct": False,
                "max_generation": 4,
                "final_alive": 14,
                "run_summary": {
                    "trait_impact": {
                        "density_preference_mean": 0.95,
                        "density_preference_std": 0.14,
                        "density_preference_guided_bias": -0.02,
                        "density_preference_guided_total": 14,
                        "density_preference_seek_total": 5,
                        "density_preference_avoid_total": 9,
                        "density_preference_seek_usage_per_tick": 0.18,
                        "density_preference_avoid_usage_per_tick": 0.22,
                        "density_preference_seek_share": 0.36,
                        "density_preference_avoid_share": 0.64,
                        "density_preference_seek_users_avg": 1.02,
                        "density_preference_seek_usage_bias": 0.02,
                        "density_preference_avoid_users_avg": 0.89,
                        "density_preference_avoid_usage_bias": -0.05,
                        "density_preference_neighbor_count_avg": 2.1,
                        "density_preference_center_distance_delta": 0.08,
                    }
                },
            },
        ]

        summary = build_multi_run_summary(run_results)
        avg = summary["avg_trait_impact"]

        self.assertAlmostEqual(float(avg["density_preference_mean"]), 1.0)
        self.assertAlmostEqual(float(avg["density_preference_std"]), 0.12)
        self.assertAlmostEqual(float(avg["density_preference_guided_bias"]), 0.01)
        self.assertAlmostEqual(float(avg["density_preference_guided_total"]), 12.0)
        self.assertAlmostEqual(float(avg["density_preference_seek_total"]), 6.0)
        self.assertAlmostEqual(float(avg["density_preference_avoid_total"]), 6.0)
        self.assertAlmostEqual(float(avg["density_preference_seek_usage_per_tick"]), 0.215)
        self.assertAlmostEqual(float(avg["density_preference_avoid_usage_per_tick"]), 0.165)
        self.assertAlmostEqual(float(avg["density_preference_seek_share"]), 0.53)
        self.assertAlmostEqual(float(avg["density_preference_avoid_share"]), 0.47)
        self.assertAlmostEqual(float(avg["density_preference_seek_users_avg"]), 1.055)
        self.assertAlmostEqual(float(avg["density_preference_seek_usage_bias"]), 0.035)
        self.assertAlmostEqual(float(avg["density_preference_avoid_users_avg"]), 0.91)
        self.assertAlmostEqual(float(avg["density_preference_avoid_usage_bias"]), -0.06)

    def test_formatted_summaries_expose_density_preference_impact_metrics(self) -> None:
        run_text = format_final_run_summary(
            {
                "trait_impact": {
                    "density_preference_seek_total": 7,
                    "density_preference_avoid_total": 3,
                    "density_preference_seek_share": 0.7,
                    "density_preference_avoid_share": 0.3,
                    "density_preference_seek_usage_per_tick": 0.25,
                    "density_preference_avoid_usage_per_tick": 0.11,
                }
            }
        )
        self.assertIn("densite:", run_text)
        self.assertIn("part_avoid=", run_text)
        self.assertIn("freq_seek=", run_text)
        self.assertIn("freq_avoid=", run_text)

        multi_text = format_multi_run_summary(
            {
                "avg_trait_impact": {
                    "density_preference_seek_total": 6.0,
                    "density_preference_avoid_total": 4.0,
                    "density_preference_seek_share": 0.6,
                    "density_preference_avoid_share": 0.4,
                    "density_preference_seek_usage_per_tick": 0.2,
                    "density_preference_avoid_usage_per_tick": 0.1,
                }
            }
        )
        self.assertIn("densite_moy:", multi_text)
        self.assertIn("part_avoid=", multi_text)
        self.assertIn("freq_seek=", multi_text)
        self.assertIn("freq_avoid=", multi_text)


if __name__ == "__main__":
    unittest.main()

