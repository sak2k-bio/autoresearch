# Importing Outcome Data (Step by Step)

This guide shows how to log real performance data so the learning loop can improve over time.

1. Confirm the outcome log exists.
Check `autoresearch/outcomes.tsv` and make sure it has a header row:
`timestamp	impressions	clicks	likes	comments	shares	saves	outcome_score	notes`

2. Record a single post’s outcome.
Use the CLI to append a row and update learning memory:

```powershell
python autoresearch/autoresearch_bio.py --record-outcome 20260315_153055 --impressions 2500 --clicks 45 --likes 120 --comments 6 --shares 8 --saves 14 --notes "Strong niche engagement"
```

3. Optional: set a custom outcome score.
If you already computed a normalized outcome score (0–1), pass it in:

```powershell
python autoresearch/autoresearch_bio.py --record-outcome 20260315_153055 --impressions 2500 --outcome-score 0.62 --notes "Manual score override"
```

4. Bulk import outcomes from a TSV.
Create a TSV with the same header as `outcomes.tsv`, then ingest it:

```powershell
python autoresearch/autoresearch_bio.py --ingest-outcomes autoresearch/outcomes.tsv
```

5. Verify learning updates.
After recording or ingesting outcomes, a learning summary is printed and updates:

- `autoresearch/learning_memory.json` (experiments + performance_history)
- `autoresearch/topic_memory.json` (topic scores)

6. Repeat regularly.
Add outcomes daily or weekly so the system can shift toward high-performing topics and hooks.

## Notes
- `timestamp` must match the post timestamp format used in results (YYYYMMDD_HHMMSS).
- If `outcome_score` is blank, it is computed from engagement metrics.
