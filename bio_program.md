# autoresearch bio

This is an experiment to have the LLM autonomously find high-quality bio-medical research papers and convert them into viral LinkedIn posts.

## Setup

To set up a new bio research experiment, ensure you have:

1. **Environment variables set**:
   - `TAVILY_API_KEY` for paper discovery
   - `GEMINI_API_KEY_1`, `GEMINI_API_KEY_2`, etc. (up to 5) for post generation

2. **Dependencies installed**: Run `uv sync` to install tavily-python and google-generativeai

3. **Agree on a run tag**: propose a tag based on today's date (e.g. `bio-mar5`). The branch `autoresearch/<tag>` must not already exist — this is a fresh run.

4. **Create the branch**: `git checkout -b autoresearch/<tag>` from current master.

5. **Read the in-scope files**: The bio_research module has these key files:
   - `bio_research/config.py` — configuration for API keys and settings
   - `autoresearch_bio.py` — the main autonomous agent that implements the 5-step pipeline
   - `bio_results.tsv` — results tracking file
   - `results/post_*.txt` — full post outputs with metadata

6. **Verify API access**: Check that your Tavily and Gemini API keys are working. If not, tell the human to set the environment variables.

7. **Initialize results.tsv**: The bio_results.tsv file will be created automatically with just the header row.

## Bio Research Pipeline

The system implements the following 5-step pipeline:

**STEP 1 — Keyword Discovery**
Generate high-quality research keywords using patterns such as:
- "mechanism of"
- "novel pathway"
- "metabolic regulation"
- "biochemical signaling"
- "new biomarker"
- "unexpected mechanism"
- "recent discovery"

Prioritize topics that are surprising, counterintuitive, clinically relevant, and useful for explaining biology to a broader audience.

**STEP 2 — Paper Discovery**
Search sources using Tavily API prioritizing:
- Tier 1: Nature, Science, Cell, Nature Metabolism, Nature Medicine, Cell Metabolism
- Tier 2: PNAS, EMBO, JCI, Nature Communications
- Tier 3: Strong PubMed discoveries

Select papers that meet these criteria:
- published within the last 3–5 years OR classic high-impact papers
- strong experimental insight
- clear mechanism or discovery
- interesting implications for health or metabolism

**STEP 3 — Insight Extraction**
From the paper extract:
- the key discovery
- the biochemical mechanism
- why it matters clinically or biologically
- one surprising or memorable insight
- the mechanistic chain (e.g., Nutrient excess → mitochondrial overload → increased ROS → insulin signaling inhibition → metabolic disease)

**STEP 4 — LinkedIn Post Generation**
Convert the insight into a high-performing LinkedIn post with:
- **HOOK**: A curiosity-driven opening line
- **SETUP**: Why scientists believed something else
- **DISCOVERY**: What the new paper found
- **MECHANISM**: Explain the biochemical pathway
- **IMPLICATION**: Why this matters for metabolism, disease, or physiology
- **QUESTION**: A thoughtful question or reflection

Posts should:
- be engaging and easy to read
- maintain scientific accuracy
- avoid heavy jargon
- make complex biochemistry intuitive
- be ~120–200 words

**STEP 5 — SEO and Reach Optimization**
Add:
- strong keywords
- 3–5 relevant hashtags
- formatting for readability
- curiosity amplification scoring

## Autonomous Operation

The bio research agent runs autonomously with the following characteristics:

**What you CAN do:**
- Run the bio_research pipeline continuously
- Improve over time through the learning loop
- Adapt keyword generation based on topic performance
- Filter papers using the scoring system (only papers with score > 0.7 proceed)
- Generate high-quality LinkedIn posts that perform well

**What you CANNOT do:**
- Modify core bio_research code (this is read-only during operation)
- Install new packages not in pyproject.toml
- Modify the scoring algorithm while running

**The goal is simple: generate high-quality LinkedIn posts that score 35+/50 on curiosity metrics.**

Since the system is autonomous, you don't need to worry about manual oversight — it will continuously improve based on performance feedback. The system will bias toward topics that historically perform well.

**Quality criterion**: All posts must achieve a minimum curiosity score of 35/50. Posts below this threshold are automatically regenerated.

## Output format

For each paper the system produces:

Paper Title
Authors
Journal / Year
Key Insight

LinkedIn Post

Hashtags

The results are logged to bio_results.tsv with timestamps and quality scores, and full post details are saved to results/post_*.txt.

## Running the agent

To run the agent:

```bash
# Set up environment variables
export TAVILY_API_KEY=your_tavily_key_here
export GEMINI_API_KEY_1=your_gemini_key_here
export GEMINI_API_KEY_2=backup_key_here  # Optional backup keys
# ... etc for up to 5 Gemini keys

# Run the autonomous loop
python autoresearch_bio.py

# Or run once for testing
python autoresearch_bio.py --run-once

# Print learning summary
python autoresearch_bio.py --print-learning
```

The agent will run autonomously, continuously finding papers and generating LinkedIn posts while learning to improve over time.
