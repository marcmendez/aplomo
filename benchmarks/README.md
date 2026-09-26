# Agent benchmark

This benchmark compares the same Codex coding tasks in clean temporary repositories with and without Aplomo. It measures hidden acceptance checks, token usage, tool calls, and wall-clock time.

```bash
uv run python benchmarks/run_codex.py --repetitions 3 --output benchmark-results.json
```

The task prompt, starting files, Codex version, and scorer are identical in both arms. The Aplomo arm adds only the files produced by `aplomo init --agents codex`. Runs are deliberately kept outside CI because they require an authenticated Codex account and consume model quota.

This is an engineering benchmark, not a universal productivity claim. Report the model/CLI version, number of runs, raw results, and all regressions. One run per task is a pilot; use multiple repetitions before claiming a stable effect.
