# Architecture (AutoResearch Bio Pipeline)

This is a simple, visual overview of how the pipeline works, what levers you can tune, what gets evaluated, and where results and monitoring live.

## 1. End-to-End Flow

```mermaid
flowchart TD
  A[Run: autoresearch_bio.py] --> B[Env Loader]
  B --> C[KeywordGenerator]
  C --> D[PaperFinder (Tavily)]
  D --> E[PaperScorer]
  E -->|score >= MIN_PAPER_SCORE| F[InsightExtractor]
  E -->|score < MIN_PAPER_SCORE| X[Skip Paper]
  F --> G[MechanismSimplifier]
  G --> H[HookGenerator]
  H --> I[PostGenerator (Gemini)]
  I --> J[Curiosity Scoring]
  J --> K[Optimizer]
  K --> L[Results Output]
  L --> M[LearningLoop + TopicMemory]
```

## 2. Major Components and Code Files

![alt text](flow-charts/mermaid-diagram.png)

```mermaid
flowchart LR
  subgraph Core
    A1[autoresearch_bio.py\nMain orchestration]
    A2[bio_research/config.py\nSettings + thresholds]
  end

  subgraph Research
    B1[keyword_generator.py\nKeyword creation]
    B2[paper_finder.py\nTavily search]
    B3[paper_scoring.py\nQuality scoring]
    B4[insight_extractor.py\nExtract insights]
    B5[mechanism_simplifier.py\nSimplify mechanism]
  end

  subgraph Generation
    C1[hook_generator.py\nHooks]
    C2[post_generator.py\nGemini posts + scoring]
    C3[optimizer.py\nFormatting + hashtags]
  end

  subgraph Learning
    D1[topic_memory.py\nTopic performance]
    D2[learning_loop.py\nExperiment memory]
  end

  A1 --> A2
  A1 --> B1 --> B2 --> B3 --> B4 --> B5
  A1 --> C1 --> C2 --> C3
  A1 --> D1
  A1 --> D2
```

## 3. Evals, Optimizations, and Levers

![alt text](<flow-charts/mermaid-diagram (1).png>)

```mermaid
flowchart TD
  E1[Eval: Paper Score] -->|MIN_PAPER_SCORE| P[Paper Pass/Fail]
  E2[Eval: Curiosity Score] -->|MIN_CURIOSITY_SCORE| Q[Post Pass/Regenerate]

  L1[Lever: MIN_PAPER_SCORE] --> E1
  L2[Lever: MAX_RESULTS] --> E1
  L3[Lever: Keywords Used] --> E1
  L4[Lever: Topic Bias] --> E1

  L5[Lever: Hook Quality] --> E2
  L6[Lever: Prompt Structure] --> E2
  L7[Lever: Regeneration Attempts] --> E2
```

## 4. Outputs and Monitoring

![alt text](<flow-charts/mermaid-diagram (2).png>)

```mermaid
flowchart TD
  O1[bio_results.tsv\nScores + status] --> M1[Monitoring]
  O2[results/post_*.txt\nFull posts] --> M1
  O3[results/checkpoints/*.json\nDurability] --> M1
  O4[topic_memory.json\nTopic bias] --> M1
  O5[learning_memory.json\nExperiment history] --> M1
  O6[Console logs\nAPI counts + learning summary] --> M1
```

## 5. Where to Look for Each Concern

Levers:

- `MIN_PAPER_SCORE`, `MIN_CURIOSITY_SCORE`: `bio_research/config.py`
- Search breadth: `bio_research/paper_finder.py`
- Keyword generation and bias: `bio_research/keyword_generator.py` and `topic_memory.py`
- Curiosity scoring: `bio_research/post_generator.py`

Monitoring:

- Run logs: console output
- Aggregated results: `bio_results.tsv`
- Full posts: `results/post_*.txt`
- Learning history: `learning_memory.json`
- Topic performance: `topic_memory.json`

Iteration workflow:

- See `CONDUCT_RESEARCH.md` for step-by-step iteration and evaluation guidance.
