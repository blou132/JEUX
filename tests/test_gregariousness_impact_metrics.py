import unittest

from legacy_python.debug_tools import (
    build_final_run_summary,
    build_multi_run_summary,
    create_proto_temporal_tracker,
)
from legacy_python.ui import format_final_run_summary, format_multi_run_summary


class GregariousnessImpactMetricsTests(unittest.TestCase):
    def test_final_summary_includes_gregariousness_impact_metrics(self) -> None:
        tracker = create_proto_temporal_tracker()
        final_stats = {
            "avg_gregariousness": 1.01,
            "std_gregariousness": 0.09,
            "gregariousness_guided_usage_bias_total": 0.03,
            "total_gregariousness_guided_moves": 14,
            "total_gregariousness_seek_moves": 8,
            "total_gregariousness_avoid_moves": 6,
            "gregariousness_seek_usage_per_tick_total": 0.22,
            "gregariousness_avoid_usage_per_tick_total": 0.17,
            "gregariousness_seek_share_total": 0.57,
            "gregariousness_avoid_share_total": 0.43,
            "gregariousness_seek_users_avg_total": 1.06,
            "gregariousness_seek_usage_bias_total": 0.05,
            "gregariousness_avoid_users_avg_total": 0.95,
            "gregariousness_avoid_usage_bias_total": -0.06,
            "avg_gregariousness_neighbor_count_total": 2.4,
            "avg_gregariousness_center_distance_delta_total": -0.07,
        }

        summary = build_final_run_summary(final_stats, tracker)
        trait_impact = summary["trait_impact"]

        self.assertAlmostEqual(float(trait_impact["gregariousness_mean"]), 1.01)
        self.assertAlmostEqual(float(trait_impact["gregariousness_std"]), 0.09)
        self.assertAlmostEqual(float(trait_impact["gregariousness_guided_bias"]), 0.03)
        self.assertEqual(int(trait_impact["gregariousness_guided_total"]), 14)
        self.assertEqual(int(trait_impact["gregariousness_seek_total"]), 8)
        self.assertEqual(int(trait_impact["gregariousness_avoid_total"]), 6)
        self.assertAlmostEqual(float(trait_impact["gregariousness_seek_usage_per_tick"]), 0.22)
        self.assertAlmostEqual(float(trait_impact["gregariousness_avoid_usage_per_tick"]), 0.17)
        self.assertAlmostEqual(float(trait_impact["gregariousness_seek_share"]), 0.57)
        self.assertAlmostEqual(float(trait_impact["gregariousness_avoid_share"]), 0.43)
        self.assertAlmostEqual(float(trait_impact["gregariousness_seek_users_avg"]), 1.06)
        self.assertAlmostEqual(float(trait_impact["gregariousness_seek_usage_bias"]), 0.05)
        self.assertAlmostEqual(float(trait_impact["gregariousness_avoid_users_avg"]), 0.95)
        self.assertAlmostEqual(float(trait_impact["gregariousness_avoid_usage_bias"]), -0.06)
        self.assertAlmostEqual(float(trait_impact["gregariousness_neighbor_count_avg"]), 2.4)
        self.assertAlmostEqual(float(trait_impact["gregariousness_center_distance_delta"]), -0.07)

    def test_multi_run_summary_aggregates_gregariousness_impact_metrics(self) -> None:
        run_results = [
            {
                "seed": 1,
                "extinct": False,
                "max_generation": 3,
                "final_alive": 12,
                "run_summary": {
                    "trait_impact": {
                        "gregariousness_mean": 1.05,
                        "gregariousness_std": 0.10,
                        "gregariousness_guided_bias": 0.04,
                        "gregariousness_guided_total": 10,
                        "gregariousness_seek_total": 6,
                        "gregariousness_avoid_total": 4,
                        "gregariousness_seek_usage_per_tick": 0.23,
                        "gregariousness_avoid_usage_per_tick": 0.13,
                        "gregariousness_seek_share": 0.60,
                        "gregariousness_avoid_share": 0.40,
                        "gregariousness_seek_users_avg": 1.08,
                        "gregariousness_seek_usage_bias": 0.06,
                        "gregariousness_avoid_users_avg": 0.95,
                        "gregariousness_avoid_usage_bias": -0.05,
                        "gregariousness_neighbor_count_avg": 2.5,
                        "gregariousness_center_distance_delta": -0.09,
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
                        "gregariousness_mean": 0.95,
                        "gregariousness_std": 0.06,
                        "gregariousness_guided_bias": -0.01,
                        "gregariousness_guided_total": 14,
                        "gregariousness_seek_total": 5,
                        "gregariousness_avoid_total": 9,
                        "gregariousness_seek_usage_per_tick": 0.16,
                        "gregariousness_avoid_usage_per_tick": 0.24,
                        "gregariousness_seek_share": 0.36,
                        "gregariousness_avoid_share": 0.64,
                        "gregariousness_seek_users_avg": 1.00,
                        "gregariousness_seek_usage_bias": 0.01,
                        "gregariousness_avoid_users_avg": 0.90,
                        "gregariousness_avoid_usage_bias": -0.08,
                        "gregariousness_neighbor_count_avg": 2.1,
                        "gregariousness_center_distance_delta": 0.11,
                    }
                },
            },
        ]

        summary = build_multi_run_summary(run_results)
        avg = summary["avg_trait_impact"]

        self.assertAlmostEqual(float(avg["gregariousness_mean"]), 1.0)
        self.assertAlmostEqual(float(avg["gregariousness_std"]), 0.08)
        self.assertAlmostEqual(float(avg["gregariousness_guided_bias"]), 0.015)
        self.assertAlmostEqual(float(avg["gregariousness_guided_total"]), 12.0)
        self.assertAlmostEqual(float(avg["gregariousness_seek_total"]), 5.5)
        self.assertAlmostEqual(float(avg["gregariousness_avoid_total"]), 6.5)
        self.assertAlmostEqual(float(avg["gregariousness_seek_usage_per_tick"]), 0.195)
        self.assertAlmostEqual(float(avg["gregariousness_avoid_usage_per_tick"]), 0.185)
        self.assertAlmostEqual(float(avg["gregariousness_seek_share"]), 0.48)
        self.assertAlmostEqual(float(avg["gregariousness_avoid_share"]), 0.52)
        self.assertAlmostEqual(float(avg["gregariousness_seek_users_avg"]), 1.04)
        self.assertAlmostEqual(float(avg["gregariousness_seek_usage_bias"]), 0.035)
        self.assertAlmostEqual(float(avg["gregariousness_avoid_users_avg"]), 0.925)
        self.assertAlmostEqual(float(avg["gregariousness_avoid_usage_bias"]), -0.065)

    def test_formatted_summaries_expose_gregariousness_impact_metrics(self) -> None:
        run_text = format_final_run_summary(
            {
                "trait_impact": {
                    "gregariousness_seek_total": 7,
                    "gregariousness_avoid_total": 3,
                    "gregariousness_seek_share": 0.7,
                    "gregariousness_avoid_share": 0.3,
                    "gregariousness_seek_usage_per_tick": 0.25,
                    "gregariousness_avoid_usage_per_tick": 0.11,
                }
            }
        )
        self.assertIn("gregarite:", run_text)
        self.assertIn("part_avoid=", run_text)
        self.assertIn("freq_seek=", run_text)
        self.assertIn("freq_avoid=", run_text)

        multi_text = format_multi_run_summary(
            {
                "avg_trait_impact": {
                    "gregariousness_seek_total": 6.0,
                    "gregariousness_avoid_total": 4.0,
                    "gregariousness_seek_share": 0.6,
                    "gregariousness_avoid_share": 0.4,
                    "gregariousness_seek_usage_per_tick": 0.2,
                    "gregariousness_avoid_usage_per_tick": 0.1,
                }
            }
        )
        self.assertIn("gregarite_moy:", multi_text)
        self.assertIn("part_avoid=", multi_text)
        self.assertIn("freq_seek=", multi_text)
        self.assertIn("freq_avoid=", multi_text)


if __name__ == "__main__":
    unittest.main()

