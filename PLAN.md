# AutoResearch Bio-Medical Pipeline Implementation Plan

## Overview
This plan outlines the implementation of an autonomous bio-medical research-to-LinkedIn post generator that extends the existing autoresearch framework. The system will continuously find high-quality scientific papers in clinical biochemistry, metabolism, and related fields, then convert them into engaging LinkedIn posts.

## Architecture Components

### 1. KeywordGenerator
- Generate research keywords using patterns: "mechanism of", "novel pathway", "metabolic regulation", etc.
- Prioritize surprising, counterintuitive, clinically relevant topics
- Bias toward topics that historically perform well based on TopicMemory

### 2. PaperFinder
- Use Tavily API to search for papers in clinical biochemistry, metabolism, etc.
- Prioritize papers from tiered journal hierarchy:
  - Tier 1: Nature, Science, Cell, Nature Metabolism, Nature Medicine, Cell Metabolism
  - Tier 2: PNAS, EMBO, JCI, Nature Communications
  - Tier 3: Strong PubMed discoveries
- Handle API rate limiting and key rotation automatically

### 3. PaperScorer (NEW CRITICAL MODULE)
- Apply scoring formula:
  ```
  score =
    novelty_score * 0.35 +
    clinical_relevance * 0.25 +
    counterintuitive_factor * 0.20 +
    journal_impact * 0.10 +
    recency * 0.10
  ```
- Only pass papers with score > 0.7 to next stage
- Filter out incremental/obscure results that don't perform well on LinkedIn

### 4. InsightExtractor
- Extract key discovery, mechanism, clinical significance, surprising insight
- NEW: Extract "mechanistic chain" - biochemical pathway sequences

### 5. MechanismSimplifier (NEW CRITICAL MODULE)
- Transform complex biochemical mechanisms into simple, visualizable chains
- Create clear cause-and-effect sequences that are easy to understand

### 6. PostGenerator
- Generate posts with viral structure:
  - HOOK: The surprising claim
  - SETUP: Why scientists believed something else
  - DISCOVERY: What the new paper found
  - MECHANISM: Explain the biochemical pathway
  - IMPLICATION: Why this matters for disease/biology
  - QUESTION: Invite reflection

### 7. HookGenerator (NEW CRITICAL MODULE)
- Generate 10 possible hooks for each paper
- Select the best one based on curiosity tension and engagement potential
- Use patterns that drive high engagement

### 8. Optimizer
- Curiosity amplification scoring (0-10 for Curiosity, Clarity, Novelty, Memorability, Shareability)
- Regenerate posts scoring below 35/50
- Add SEO optimization and relevant hashtags

### 9. TopicMemory (NEW CRITICAL MODULE)
- Track topic performance: topic | avg_score | posts_generated
- Bias toward higher-performing themes
- Learn which topics generate the most engagement

### 10. LearningLoop
- Maintain autonomous improvement
- Incorporate TopicMemory feedback
- Refine all components based on performance metrics
- NEW: Capture real outcome metrics (engagement, clicks, saves, etc.)
- NEW: Persist performance_history entries tied to experiment timestamps
- NEW: Update learnings with concrete adjustments (topic weights, hook patterns)

## Implementation Steps

### Phase 1: Infrastructure Setup
1. Create bio_research directory structure
2. Set up configuration files for API keys
3. Create bio_results.tsv for tracking
4. Set up bio_program.md with instructions

### Phase 2: Core Modules Development
1. Implement KeywordGenerator
2. Implement PaperFinder with Tavily API integration
3. Implement PaperScorer with scoring algorithm
4. Implement InsightExtractor

### Phase 3: Enhancement Modules
1. Implement MechanismSimplifier
2. Implement PostGenerator with viral structure
3. Implement HookGenerator with 10-hook generation
4. Implement Optimizer with curiosity scoring

### Phase 4: Intelligence Modules
1. Implement TopicMemory for topic performance tracking
2. Implement LearningLoop for autonomous improvement
3. Implement OutcomeTracker to record real performance signals
4. Implement FeedbackIntegrator to update TopicMemory + learnings
3. Integrate all modules into cohesive pipeline

### Phase 5: Testing and Validation
1. Test individual components
2. Test end-to-end pipeline
3. Validate output quality against requirements
4. Fine-tune scoring algorithms

### Phase 6: Deployment and Operation
1. Create autonomous execution loop
2. Set up monitoring and logging
3. Document usage instructions
4. Validate autonomous learning capability

## Dependencies to Add
- tavily-python (for Tavily API)
- google-generativeai (for Gemini API)
- Additional dependencies as needed for scientific paper parsing

## Success Criteria
- Generate 8.5-9/10 LinkedIn posts that perform well
- Achieve quality scores consistently above 35/50
- Demonstrate autonomous improvement over time with outcome-based metrics
- Successfully integrate with existing autoresearch framework
- Operate without interfering with existing LLM training functionality
