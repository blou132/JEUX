# Run Metrics History Analysis

- Exports read: 2
- Total valid records: 2
- Invalid lines: 0

## Run status counts
- completed: 2
- failed: 0
- running: 0

## Objective counts
- rally_champion: 1
- support_gate: 1

## Report provenance
- input: recent_complete.jsonl
- compare input: recent_complete.jsonl
- comparison: present (baseline=recent_complete.jsonl, current=recent_complete.jsonl)
- records: 2
- invalid lines: 0
- ci check: enabled
- fail on regression: no
- mode: runtime

## Support gate
| Metric | Value |
|---|---|
| records | 1 |
| avg attempts | 6.00 |
| avg success | 4.00 |
| avg success rate | 66% |
| avg available ratio | 50% |
| best run | recent_gate_1 |
| worst run | recent_gate_1 |
| objective success rate | 100% |
| stddev success rate | n/a |
| stddev available ratio | n/a |
| support gate stability | unknown |

## Champion support
| Metric | Value |
|---|---|
| records | 1 |
| avg attempts | 5.00 |
| avg success | 3.00 |
| avg success rate | 60% |
| best run | recent_champ_1 |
| worst run | recent_champ_1 |
| objective success rate | 100% |
| latest tuning label | n/a |

### Champion support diagnostic
- attempts avg: 5.00
- success rate avg: 60%
- cooldown pressure: low
- unavailable pressure: low
- objective completion: 1/1
- interpretation: no major champion support pressure detected

### Champion support multi-run comparison
- attempts avg: 5.00
- success avg: 3.00
- success rate avg: 60%
- cooldown avg: 1.00
- unavailable avg: 1.00
- objective completed: 1
- objective failed: 0
- diagnostic stability: n/a
- global interpretation: stable_successful

### Support systems summary
- support_gate: rate=66% bottleneck=none
- rally_champion: rate=60% interpretation=stable_successful
- global state: complete
- interpretation: partial_data

### Support metrics quality
- state: valid
- warnings: none
- interpretation: support metrics look consistent

### Support metrics regression
- state: stable
- changed fields: none
- warning delta: +0
- interpretation: support metrics are stable compared to baseline

### Support metrics CI check
- enabled: true
- passed: true
- triggered rules: none
- interpretation: support metrics CI check passed

## Recommendations
- Support gate tuning looks stable.

## Final decision
- decision: keep_candidate_for_more_testing
- confidence: medium
- reasons: stable_complete_data
- blocking: no
- note: heuristic quick-read only (not statistical proof).

## Comparison

- Baseline exports read: 2
- Candidate exports read: 2
- Confidence: low
- Use more runs before trusting this comparison.
- Recommendation: Comparison is inconclusive.
| Metric | Baseline | Candidate | Delta | Change |
|---|---|---|---|---|
| avg_support_gate_run_success_rate | 66% | 66% | +0.0pp | +0.0% |
| avg_support_gate_run_available_ratio | 50% | 50% | +0.0pp | +0.0% |
| objective_success_rate | 100% | 100% | +0.0pp | +0.0% |
| avg_support_gate_run_attempts | 6.00 | 6.00 | +0.00 | +0.0% |
| avg_support_gate_run_success | 4.00 | 4.00 | +0.00 | +0.0% |
| stddev_support_gate_run_success_rate | n/a | n/a | n/a | n/a |
