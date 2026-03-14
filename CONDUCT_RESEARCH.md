# Conducting Research Runs (Bio Pipeline)

This guide explains how to run the Bio pipeline, evaluate results, and iterate on quality. It is written for day-to-day use and focuses on practical signals and levers.

## 1. Quick Start

1. Ensure environment variables are set in `.env` or `.env.local`:
   - `TAVILY_API_KEY`
   - `GEMINI_API_KEY_1` (plus optional `GEMINI_API_KEY_2`..`_5`)
   - `GEMINI_MODEL` (optional)
2. Run a single iteration:
   ```
   python autoresearch_bio.py --run-once
   ```
3. Run continuously:
   ```
   python autoresearch_bio.py
   ```

What you should see:
- Keyword generation
- Paper discovery
- Scoring and filtering
- Post generation and curiosity scoring
- Output files written
- API call counts for Tavily and Gemini
- A learning summary of recent performance

## 2. What Gets Logged and Where

Outputs:
- `bio_results.tsv`  
  - One row after scoring (`status=scored`) and one row after optimization (`status=completed` or `completed_low_score`).
- `results/post_*.txt`  
  - Full post output per processed paper.
- `results/checkpoints/iteration_*.json`  
  - Lightweight checkpoint showing iteration start and completion.

Memory:
- `topic_memory.json`  
  - Rolling topic performance used to bias keywords.
- `learning_memory.json`  
  - Experiment history used for learning summaries and future analysis.

Console:
- API call counts per iteration: Tavily and Gemini
- Learning summary for the last N posts

## 3. Evaluation Signals

Key signals to watch:
- **Curiosity score (0-50)**: The main quality signal. Goal is 35+.
- **Success rate**: % of posts >= `MIN_CURIOSITY_SCORE`.
- **Avg curiosity (last N)**: Rolling average for recent performance.
- **Filtered paper count**: If this is 0 frequently, reduce `MIN_PAPER_SCORE` or expand search.

Healthy run characteristics:
- At least a few papers passing `MIN_PAPER_SCORE` per iteration.
- Curiosity scores trending upward or stable above 35.
- Fewer regenerations over time.

## 4. Core Optimizations (What We Use)

These are currently implemented:

1. **Topic-biased keywords**  
   - Keywords are biased toward topics that scored well in prior runs.
   - Helps reduce wasted searches and increase quality.

2. **Tier-1 journal floor**  
   - Tier-1 journals are given a minimum score floor to avoid over-filtering.

3. **Lowered `MIN_PAPER_SCORE` for early runs**  
   - Helps the pipeline produce outputs while bootstrapping.

4. **Tool call logging**  
   - Counts Tavily and Gemini calls per iteration.

5. **Early TSV append + checkpointing**  
   - Protects against data loss on abrupt stops.

## 5. Iteration Loop (Step-by-Step)

Use this loop to improve output quality:

1. Run 1-3 iterations and inspect:
   - `bio_results.tsv` for scores and statuses
   - `results/post_*.txt` for content quality
2. If **no papers pass**:
   - Lower `MIN_PAPER_SCORE` (e.g., 0.4 -> 0.3)
   - Increase Tavily `max_results`
   - Increase number of keywords used per run
3. If **papers pass but curiosity is low**:
   - Improve hooks or prompt structure
   - Increase regeneration attempts
   - Tighten topic categories toward high-performing domains
4. If **outputs are strong**:
   - Gradually raise `MIN_PAPER_SCORE` back toward 0.7
   - Reduce `max_results` to save API cost
5. Record changes and compare before/after:
   - Use rolling curiosity averages and success rate to validate improvements

## 6. What to Look For in Outputs

Good outputs:
- Clear, accurate mechanism explanation
- Curiosity-driven hook without overselling
- Clinical relevance explained in plain language
- 120-200 words with a clean narrative

Weak outputs:
- Repetitive language or generic hooks
- Missing or incorrect mechanism details
- Overly technical explanations
- Low curiosity scores (<35)

## 7. Recommended Settings (Starting Point)

For early-stage bootstrapping:
- `MIN_PAPER_SCORE`: 0.4
- Tavily `max_results`: 10
- Keywords used: 5

For tighter quality control:
- `MIN_PAPER_SCORE`: 0.7
- Tavily `max_results`: 5
- Keywords used: 3

## 8. Common Issues and Fixes

1. No papers passing filter:
   - Lower `MIN_PAPER_SCORE`
   - Expand search results
2. Low curiosity scores:
   - Tighten hooks or add stronger narrative structure
   - Consider a stricter topic bias toward better domains
3. High API usage:
   - Reduce keywords or `max_results`
4. Pipeline stops unexpectedly:
   - Check `results/checkpoints/` for the last stage

## 9. How to Iterate Safely

When testing new changes:
1. Run `--run-once` first.
2. Compare curiosity averages over the last 10 posts.
3. Only change one lever at a time.
4. Revert if performance drops for 2-3 iterations.

## 10. Practical Checklist

Before a long run:
- Confirm API keys
- Run 1-2 test iterations
- Verify `bio_results.tsv` and `results/post_*.txt` are updating

After each iteration:
- Check curiosity score and success rate
- Confirm TSV entries and text output
- Read 1-2 generated posts for quality

If you want a custom workflow or additional metrics (like cost tracking), add them here and update this guide as the process evolves.
