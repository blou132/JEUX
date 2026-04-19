import unittest

from debug_tools import (
    build_final_run_summary,
    build_multi_run_summary,
    create_proto_temporal_tracker,
)
from ui import format_final_run_summary, format_multi_run_summary


class BehaviorPersistenceImpactMetricsTests(unittest.TestCase):
    def test_final_summary_includes_behavior_persistence_oscillation_metrics(self) -> None:
        tracker = create_proto_temporal_tracker()
        final_stats = {
            "avg_behavior_persistence": 1.03,
            "std_behavior_persistence": 0.12,
            "behavior_persistence_hold_usage_bias_total": 0.08,
            "total_persistence_holds": 15,
            "total_search_wander_switches": 9,
            "total_search_wander_switches_prevented": 6,
            "total_search_wander_oscillation_events": 15,
            "search_wander_switch_rate_total": 0.6,
            "search_wander_prevented_rate_total": 0.4,
        }

        summary = build_final_run_summary(final_stats, tracker)
        trait_impact = summary["trait_impact"]

        self.assertAlmostEqual(float(trait_impact["behavior_persistence_mean"]), 1.03)
        self.assertAlmostEqual(float(trait_impact["behavior_persistence_std"]), 0.12)
        self.assertAlmostEqual(float(trait_impact["behavior_persistence_hold_bias"]), 0.08)
        self.assertEqual(int(trait_impact["persistence_holds_total"]), 15)
        self.assertEqual(int(trait_impact["search_wander_switches_total"]), 9)
        self.assertEqual(int(trait_impact["search_wander_switches_prevented_total"]), 6)
        self.assertEqual(int(trait_impact["search_wander_oscillation_events_total"]), 15)
        self.assertAlmostEqual(float(trait_impact["behavior_persistence_oscillation_switch_rate"]), 0.6)
        self.assertAlmostEqual(float(trait_impact["behavior_persistence_oscillation_prevented_rate"]), 0.4)

    def test_multi_run_summary_aggregates_behavior_persistence_oscillation_metrics(self) -> None:
        run_results = [
            {
                "seed": 100,
                "extinct": False,
                "max_generation": 5,
                "final_alive": 20,
                "run_summary": {
                    "trait_impact": {
                        "behavior_persistence_mean": 1.0,
                        "behavior_persistence_std": 0.10,
                        "behavior_persistence_hold_bias": 0.04,
                        "persistence_holds_total": 10,
                        "search_wander_switches_total": 6,
                        "search_wander_switches_prevented_total": 4,
                        "search_wander_oscillation_events_total": 10,
                        "behavior_persistence_oscillation_switch_rate": 0.6,
                        "behavior_persistence_oscillation_prevented_rate": 0.4,
                    }
                },
            },
            {
                "seed": 101,
                "extinct": False,
                "max_generation": 6,
                "final_alive": 22,
                "run_summary": {
                    "trait_impact": {
                        "behavior_persistence_mean": 1.1,
                        "behavior_persistence_std": 0.14,
                        "behavior_persistence_hold_bias": 0.06,
                        "persistence_holds_total": 14,
                        "search_wander_switches_total": 7,
                        "search_wander_switches_prevented_total": 7,
                        "search_wander_oscillation_events_total": 14,
                        "behavior_persistence_oscillation_switch_rate": 0.5,
                        "behavior_persistence_oscillation_prevented_rate": 0.5,
                    }
                },
            },
        ]

        summary = build_multi_run_summary(run_results)
        avg_trait_impact = summary["avg_trait_impact"]

        self.assertAlmostEqual(float(avg_trait_impact["behavior_persistence_mean"]), 1.05)
        self.assertAlmostEqual(float(avg_trait_impact["behavior_persistence_std"]), 0.12)
        self.assertAlmostEqual(float(avg_trait_impact["behavior_persistence_hold_bias"]), 0.05)
        self.assertAlmostEqual(float(avg_trait_impact["persistence_holds_total"]), 12.0)
        self.assertAlmostEqual(float(avg_trait_impact["search_wander_switches_total"]), 6.5)
        self.assertAlmostEqual(float(avg_trait_impact["search_wander_switches_prevented_total"]), 5.5)
        self.assertAlmostEqual(float(avg_trait_impact["search_wander_oscillation_events_total"]), 12.0)
        self.assertAlmostEqual(
            float(avg_trait_impact["behavior_persistence_oscillation_switch_rate"]),
            0.55,
        )
        self.assertAlmostEqual(
            float(avg_trait_impact["behavior_persistence_oscillation_prevented_rate"]),
            0.45,
        )

    def test_formatted_summaries_expose_behavior_persistence_oscillation_metrics(self) -> None:
        run_summary_text = format_final_run_summary(
            {
                "trait_impact": {
                    "behavior_persistence_hold_bias": 0.05,
                    "persistence_holds_total": 12,
                    "search_wander_switches_total": 7,
                    "search_wander_switches_prevented_total": 5,
                    "search_wander_oscillation_events_total": 12,
                    "behavior_persistence_oscillation_switch_rate": 0.58,
                    "behavior_persistence_oscillation_prevented_rate": 0.42,
                }
            }
        )
        self.assertIn("osc_bp:", run_summary_text)

        multi_summary_text = format_multi_run_summary(
            {
                "avg_trait_impact": {
                    "behavior_persistence_hold_bias": 0.04,
                    "persistence_holds_total": 10.0,
                    "search_wander_switches_total": 6.0,
                    "search_wander_switches_prevented_total": 4.0,
                    "search_wander_oscillation_events_total": 10.0,
                    "behavior_persistence_oscillation_switch_rate": 0.6,
                    "behavior_persistence_oscillation_prevented_rate": 0.4,
                }
            }
        )
        self.assertIn("osc_bp_moy:", multi_summary_text)


if __name__ == "__main__":
    unittest.main()
