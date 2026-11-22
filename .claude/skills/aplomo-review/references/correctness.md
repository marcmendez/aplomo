# Correctness review

Trace the changed behavior through a normal entry point. Compare it with the requested behavior and check relevant edge cases, retry or failure paths, and any affected invariants. Run the smallest test set that exercises the behavior through that entry point when available.

Review the diff without editing. For each finding, give the affected file and line and a concrete scenario where behavior would be wrong. Distinguish test results from behavior inspected by reading.
