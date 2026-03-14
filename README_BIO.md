# AutoResearch Bio-Medical Pipeline

Transform academic insights into high-performing LinkedIn posts with an autonomous research system that continuously discovers scientific papers and converts them into engaging professional content.

## Overview

The AutoResearch Bio-Medical Pipeline is an autonomous system that implements a 5-step process to find high-quality scientific papers in clinical biochemistry, metabolism, and related fields, then convert them into viral LinkedIn posts that perform well with both technical and non-technical audiences.

### The 5-Step Pipeline

1. **Keyword Discovery** - Generates high-quality research keywords using patterns like "mechanism of", "novel pathway", "metabolic regulation"
2. **Paper Discovery** - Searches PubMed, Google Scholar, and premium journals using Tavily API
3. **Insight Extraction** - Extracts key discoveries, mechanisms, and clinical significance
4. **LinkedIn Post Generation** - Converts insights into viral LinkedIn posts with HOOK, STORY, INSIGHT, WHY IT MATTERS structure
5. **SEO and Reach Optimization** - Adds hashtags and optimizes for engagement

### Key Features

- **Autonomous Operation**: Runs continuously without manual intervention
- **Self-Improvement**: Learns from performance metrics to generate better content
- **Quality Filtering**: Only processes papers scoring above 0.7/1.0 threshold
- **API Key Management**: Handles multiple Gemini API keys with automatic fallback
- **Topic Memory**: Tracks which topics perform best and biases selection accordingly
- **Curiosity Scoring**: Ensures posts score 35+/50 on engagement metrics

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- Tavily API key for paper discovery
- Google Gemini API keys for content generation (multiple recommended)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd autoresearch
```

2. Install dependencies:
```bash
uv sync
```

This will install all required dependencies including:
- tavily-python (for Tavily API)
- google-generativeai (for Gemini API)
- aiohttp (for async operations)

## Setup

### Environment Variables

You need to set up the following environment variables:

```bash
# Required API keys
export TAVILY_API_KEY=your_tavily_api_key_here
export GEMINI_API_KEY_1=your_primary_gemini_key_here

# Optional backup keys (recommended)
export GEMINI_API_KEY_2=your_backup_gemini_key_1
export GEMINI_API_KEY_3=your_backup_gemini_key_2
export GEMINI_API_KEY_4=your_backup_gemini_key_3
export GEMINI_API_KEY_5=your_backup_gemini_key_4
```

### API Key Acquisition

- **Tavily API Key**: Sign up at [Tavily](https://www.tavily.com/) for a free API key
- **Gemini API Key**: Get your API key from [Google AI Studio](https://aistudio.google.com/)

## Usage

### Running the Autonomous System

To run the full autonomous system:

```bash
cd autoresearch
python autoresearch_bio.py
```

The system will:
- Generate research keywords based on topic performance
- Find and score papers using Tavily API
- Extract insights and simplify complex mechanisms
- Generate and optimize LinkedIn posts
- Track performance and learn from results
- Continue indefinitely with self-improvement

### Running a Single Iteration

To run a single pipeline iteration for testing:

```bash
python autoresearch_bio.py --run-once
```

### Viewing Learning Summary

To see the system's learning report and performance metrics:

```bash
python autoresearch_bio.py --print-learning
```

## Configuration

### Key Settings

The system is configured in `bio_research/config.py`:

- `MIN_PAPER_SCORE`: Minimum score (0.0-1.0) for papers to be processed (default: 0.7)
- `MIN_CURIOSITY_SCORE`: Minimum score (0-50) for posts before regeneration (default: 35)
- `NUM_HOOKS_TO_GENERATE`: Number of hooks generated per paper (default: 10)
- `TOPIC_CATEGORIES`: Research areas to focus on
- `KEYWORD_PATTERNS`: Keyword patterns to use

### Journal Tiers

The system prioritizes papers from these journal tiers:

- **Tier 1**: Nature, Science, Cell, Nature Metabolism, Nature Medicine, Cell Metabolism
- **Tier 2**: PNAS, EMBO, JCI, Nature Communications
- **Tier 3**: Strong PubMed discoveries

## Output Format

For each paper processed, the system generates:

```
Paper Title: [Title]
Authors: [Authors]
Journal/Year: [Journal, Year]
Key Insight: [The main discovery]

LinkedIn Post: [Generated post with HOOK, STORY, INSIGHT, WHY IT MATTERS, END]

Hashtags: [3-5 relevant hashtags]
Quality Score: [0-50 based on engagement prediction]
```

Results are logged to `bio_results.tsv` with timestamps and quality metrics, and full post details are saved to `results/post_*.txt`.

## Results Tracking

The system maintains several tracking files:

- `bio_results.tsv`: Complete experiment logs with timestamps, scores, and status
- `results/post_*.txt`: Full post outputs with metadata and optimized text
- `topic_memory.json`: Performance data for different research topics
- Console output: Real-time progress and learning reports

## Troubleshooting

### Common Issues

1. **API Key Errors**: Verify all environment variables are set correctly
2. **Rate Limits**: The system handles rate limiting automatically, but ensure you have sufficient API quotas
3. **Dependency Issues**: Run `uv sync` to reinstall dependencies
4. **Connection Issues**: Check internet connectivity for API calls

### Performance Monitoring

- Monitor the quality scores in `bio_results.tsv`
- Check the learning reports every 5 iterations
- Watch for consistent patterns in successful vs. unsuccessful posts

## Architecture

The system follows a modular architecture with these key components:

- **KeywordGenerator**: Creates research-focused keywords with topic biasing
- **PaperFinder**: Interfaces with Tavily API for paper discovery
- **PaperScorer**: Critical module that filters papers using the weighted scoring formula
- **InsightExtractor**: Extracts key scientific insights
- **MechanismSimplifier**: Critical module that makes complex mechanisms understandable
- **HookGenerator**: Critical module that creates engaging post openings
- **PostGenerator**: Uses Gemini API to create viral LinkedIn posts
- **Optimizer**: Applies curiosity scoring and regeneration logic
- **TopicMemory**: Critical module that tracks topic performance
- **LearningLoop**: Manages autonomous improvement

## Performance Expectations

- **Output Quality**: 8.5-9/10 LinkedIn posts should perform well (vs. 6/10 without enhancements)
- **Processing Speed**: Approximately 1-2 posts per minute depending on API response times
- **Improvement Rate**: Quality should increase over time as the system learns
- **API Usage**: Efficient key rotation to maximize availability

## Customization

### Adding New Topics

Modify `TOPIC_CATEGORIES` in `bio_research/config.py` to add new research areas.

### Adjusting Scoring

Tune the scoring formula in `bio_research/paper_scoring.py` to emphasize different factors.

### Changing Post Structure

Modify the post generation prompts in `bio_research/post_generator.py` to change the output format.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the repository or contact the maintainers.
