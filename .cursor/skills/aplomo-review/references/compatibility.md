# Compatibility review

Trace existing callers and contracts affected by the diff. Look for changes to public interfaces, defaults, stored data, or rollouts that could break existing behavior. When changes overlap with nearby work, inspect the available Git state and compare the affected assumptions. Keep the review within the provided checkout and available evidence.

Review the diff without editing. For each finding, identify the affected consumer or requirement, how it could break, and the test or migration that would verify it.
