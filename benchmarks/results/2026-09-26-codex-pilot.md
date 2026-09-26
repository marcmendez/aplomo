# Codex pilot — 2026-09-26

This is a single-run pilot, not a statistically stable productivity claim.

## Setup

- Codex CLI: `0.154.0-alpha.6.2`
- Tasks: 3 paired Python repository changes
- Repetitions: 1 per task and arm
- Baseline: clean fixture repository
- Treatment: the same repository after `aplomo init --agents codex`
- Scoring: 10 hidden checks covering behavior, existing-pattern reuse, boundaries, API compatibility, and tests

## Aggregate result

| Metric | Baseline | Aplomo | Difference |
|---|---:|---:|---:|
| Hidden checks passed | 10 / 10 | 10 / 10 | 0 |
| Uncached input + output tokens | 53,608 | 65,749 | +22.6% |
| Tool calls | 18 | 31 | +72.2% |
| Aplomo MCP calls | 0 | 6 | +2 per task |
| Wall time | 179.34 s | 257.78 s | +43.7% |

## Per-task result

| Task | Arm | Score | Uncached + output tokens | Tool calls | Time |
|---|---|---:|---:|---:|---:|
| Reuse existing policy | Baseline | 3 / 3 | 18,860 | 7 | 66.34 s |
| Reuse existing policy | Aplomo | 3 / 3 | 22,083 | 11 | 93.58 s |
| Respect layer boundary | Baseline | 4 / 4 | 18,544 | 7 | 68.46 s |
| Respect layer boundary | Aplomo | 4 / 4 | 24,100 | 11 | 98.34 s |
| Targeted regression fix | Baseline | 3 / 3 | 16,204 | 4 | 44.54 s |
| Targeted regression fix | Aplomo | 3 / 3 | 19,566 | 9 | 65.86 s |

All three tasks passed every hidden check in both arms. This pilot therefore establishes neither a quality uplift nor token savings. It does show that the Aplomo workflow preserved task correctness while consistently running its repository preflight and final diff review. Larger, repeated, ambiguity-heavy tasks are needed to test whether those checks reduce defects or rework.

The runner and fixtures are versioned in [`benchmarks/run_codex.py`](../run_codex.py). Token totals come from Codex JSONL `turn.completed` usage; “uncached input + output” is `input_tokens - cached_input_tokens + output_tokens`.
