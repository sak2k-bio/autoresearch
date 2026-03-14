"""
AutoResearch Bio-Medical Pipeline
Autonomous system for discovering high-quality scientific papers and converting them to viral LinkedIn posts
"""

import os
import sys
import time
import argparse
import json
from datetime import datetime
from typing import Dict, List

# Load environment variables first
try:
    from utils.env_loader import load_env_with_dotenv, load_env_variables
    load_env_with_dotenv()
    load_env_variables()
except ImportError:
    print("utils.env_loader not found, attempting manual .env loading...")
    # Manual .env loading as fallback
    import pathlib
    from pathlib import Path
    
    # Look for .env files and load them
    current_dir = Path.cwd()
    for _ in range(4):
        for env_file in ['.env.local', '.env', '.env.example']:
            env_path = current_dir / env_file
            if env_path.exists():
                try:
                    with open(env_path, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip()
                                
                                # Remove quotes if present
                                if (value.startswith('"') and value.endswith('"')) or \
                                   (value.startswith("'") and value.endswith("'")):
                                    value = value[1:-1]
                                
                                # Only set if not already set to avoid overriding system vars
                                if key not in os.environ:
                                    os.environ[key] = value
                except Exception as e:
                    print(f"Warning: Could not load {env_path}: {e}")
        
        if current_dir.parent == current_dir:
            break
        current_dir = current_dir.parent

# Import the modules after loading environment
from bio_research.keyword_generator import KeywordGenerator
from bio_research.paper_finder import PaperFinder
from bio_research.paper_scoring import PaperScorer
from bio_research.insight_extractor import InsightExtractor
from bio_research.mechanism_simplifier import MechanismSimplifier
from bio_research.hook_generator import HookGenerator
from bio_research.post_generator import PostGenerator
from bio_research.optimizer import Optimizer
from bio_research.topic_memory import TopicMemory
from bio_research.learning_loop import LearningLoop
from bio_research.config import config

class AutoResearchBio:
    def __init__(self):
        # Initialize all components
        self.keyword_generator = KeywordGenerator()
        self.paper_finder = PaperFinder()
        self.paper_scoring = PaperScorer()
        self.insight_extractor = InsightExtractor()
        self.mechanism_simplifier = MechanismSimplifier()
        self.hook_generator = HookGenerator()
        self.post_generator = PostGenerator()
        self.optimizer = Optimizer()
        self.topic_memory = TopicMemory()
        self.learning_loop = LearningLoop()
        
        # Track statistics
        self.stats = {
            'papers_processed': 0,
            'posts_generated': 0,
            'total_iterations': 0,
            'start_time': datetime.now()
        }
    
    def run_pipeline(self):
        """Run a single iteration of the complete pipeline"""
        print(f"\n[REFRESH] Starting pipeline iteration #{self.stats['total_iterations'] + 1}")
        iteration_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_path = os.path.join("results", "checkpoints", f"iteration_{iteration_timestamp}.json")
        self._write_checkpoint(checkpoint_path, {
            "iteration": self.stats['total_iterations'] + 1,
            "timestamp": iteration_timestamp,
            "stage": "started"
        })
        tavily_calls_start = getattr(self.paper_finder, "tavily_calls", 0)
        gemini_calls_start = getattr(self.post_generator, "gemini_calls", 0)
        
        try:
            # Step 1: Generate research keywords
            print("[SEARCH] Generating research keywords...")
            topic_performance = {topic: avg for topic, avg in self.topic_memory.get_top_performing_topics(5)}
            if topic_performance:
                keywords = self.keyword_generator.generate_topic_biased_keywords(topic_performance)
                print("   Using topic-biased keywords based on performance memory")
            else:
                keywords = self.keyword_generator.generate_keywords()
            print(f"   Generated {len(keywords)} keywords: {keywords}")
            
            # Bias keywords based on topic memory
            biased_keywords = self.topic_memory.bias_keywords(keywords)
            print(f"   Biased keywords based on performance: {biased_keywords[:3]}")
            
            # Step 2: Find papers using keywords
            print("[BOOK] Finding relevant papers...")
            papers = self.paper_finder.search_papers(biased_keywords[:5])  # Use top 5 keywords
            print(f"   Found {len(papers)} papers")
            
            if not papers:
                print("   [CROSS] No papers found, skipping iteration")
                return
            
            # Step 3: Score papers for quality
            print("[CHART] Scoring papers...")
            scored_papers = self.paper_scoring.score_papers(papers)
            filtered_papers = self.paper_scoring.filter_papers_by_score(scored_papers)
            print(f"   Filtered to {len(filtered_papers)} high-quality papers (score > {config.MIN_PAPER_SCORE})")
            
            if not filtered_papers:
                print("   [CROSS] No high-quality papers found, skipping iteration")
                return
            
            # Process each high-quality paper
            for i, paper in enumerate(filtered_papers[:2]):  # Process top 2 papers
                print(f"\n[NOTE] Processing paper {i+1}/{len(filtered_papers[:2])}: {paper['title'][:50]}...")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Step 4: Extract insights from paper
                print("   [LAB] Extracting key insights...")
                insights = self.insight_extractor.extract_insights(paper)
                print(f"   Extracted insights: {insights.get('key_discovery', 'N/A')[:60]}...")
                
                # Step 5: Simplify complex mechanisms
                print("   [BRAIN] Simplifying mechanisms...")
                mechanism_str = insights.get('biochemical_mechanism', '')
                mechanistic_chain_str = insights.get('mechanistic_chain', '')
                simplified_mechanism = self.mechanism_simplifier.simplify_mechanism(mechanism_str, mechanistic_chain_str)
                print(f"   Simplified: {simplified_mechanism.get('simple_mechanism', 'N/A')[:60]}...")
                
                # Step 6: Generate hooks for engagement
                print("   [IDEA] Generating engagement hooks...")
                hooks = self.hook_generator.generate_hooks(paper, insights)
                best_hook = self.hook_generator.select_best_hook(hooks, paper)
                print(f"   Best hook: {best_hook[:60]}...")
                
                # Step 7: Generate viral LinkedIn post
                print("   [PEN]  Generating LinkedIn post...")
                post_data = self.post_generator.generate_post(paper, insights, simplified_mechanism, best_hook)
                
                # Step 8: Score curiosity of the post
                print("   [TEST_TUBE] Scoring post curiosity...")
                curiosity_scores = self.post_generator.score_curiosity(post_data)
                total_curiosity = self.post_generator.get_total_curiosity_score(curiosity_scores)
                print(f"   Curiosity score: {total_curiosity}/50")

                # Early TSV append after scoring, before optimization
                self._append_results_tsv({
                    'timestamp': timestamp,
                    'paper_title': paper.get('title', ''),
                    'authors': paper.get('authors', ''),
                    'journal': paper.get('journal', ''),
                    'year': paper.get('year', ''),
                    'url': paper.get('url', ''),
                    'paper_score': paper.get('score', ''),
                    'model': post_data.get('generated_by_model', ''),
                    'curiosity_score': total_curiosity,
                    'curiosity_scores': curiosity_scores,
                    'hashtags': [],
                    'status': 'scored'
                })
                
                # Regenerate if score is too low
                regeneration_count = 0
                while total_curiosity < config.MIN_CURIOSITY_SCORE and regeneration_count < 3:
                    print(f"   [RETRY] Regenerating post (attempt {regeneration_count + 1})...")
                    post_data = self.post_generator.generate_post(paper, insights, simplified_mechanism, best_hook)
                    curiosity_scores = self.post_generator.score_curiosity(post_data)
                    total_curiosity = self.post_generator.get_total_curiosity_score(curiosity_scores)
                    print(f"   New curiosity score: {total_curiosity}/50")
                    regeneration_count += 1
                
                # Step 9: Optimize post for engagement
                print("   [ROCKET] Optimizing post...")
                optimized_post = self.optimizer.optimize_post(post_data['original_post'], curiosity_scores, paper)
                
                # Step 10: Save results
                print("   [DISK] Saving results...")
                filename = f"results/post_{timestamp}_{i+1}.txt"
                
                # Create results directory if it doesn't exist
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Title: {paper['title']}\n")
                    f.write(f"Authors: {paper.get('authors', 'N/A')}\n")
                    f.write(f"Journal: {paper['journal']} ({paper['year']})\n")
                    f.write(f"Link: {paper.get('url', 'N/A')}\n")
                    f.write(f"Score: {paper.get('score', 'N/A')}\n")
                    f.write(f"Generated by: {post_data.get('generated_by_model', 'Unknown')}\n")
                    f.write(f"Curiosity Score: {total_curiosity}/50\n")
                    f.write(f"Individual Scores: {curiosity_scores}\n")
                    f.write(f"\nOriginal Post:\n{post_data['original_post']}\n")
                    f.write(f"\nOptimized Post:\n{optimized_post['optimized_post']}\n")
                    f.write(f"\nHashtags: {' '.join(optimized_post['hashtags'])}\n")

                # Append to bio_results.tsv for aggregated tracking
                self._append_results_tsv({
                    'timestamp': timestamp,
                    'paper_title': paper.get('title', ''),
                    'authors': paper.get('authors', ''),
                    'journal': paper.get('journal', ''),
                    'year': paper.get('year', ''),
                    'url': paper.get('url', ''),
                    'paper_score': paper.get('score', ''),
                    'model': post_data.get('generated_by_model', ''),
                    'curiosity_score': total_curiosity,
                    'curiosity_scores': curiosity_scores,
                    'hashtags': optimized_post.get('hashtags', []),
                    'status': 'completed' if total_curiosity >= config.MIN_CURIOSITY_SCORE else 'completed_low_score'
                })
                
                # Update stats
                self.stats['papers_processed'] += 1
                self.stats['posts_generated'] += 1
                
                # Record experiment in learning loop
                topic_category = self._categorize_topic(paper['title'])
                experiment_data = {
                    'topic_category': topic_category,
                    'paper_title': paper['title'],
                    'paper_score': paper.get('score', 0),
                    'curiosity_score': total_curiosity,
                    'hook_used': best_hook[:30] + '...',
                    'success': total_curiosity >= config.MIN_CURIOSITY_SCORE,
                    'timestamp': timestamp
                }
                self.learning_loop.record_experiment(experiment_data)
                self.topic_memory.update_topic_performance(topic_category, total_curiosity / 50.0)
                
                print(f"   [CHECK] Post saved to {filename}")
                
                # Small delay to avoid overwhelming APIs
                time.sleep(2)
        
        except Exception as e:
            print(f"[CROSS] Error in pipeline iteration: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.stats['total_iterations'] += 1
            self._write_checkpoint(checkpoint_path, {
                "iteration": self.stats['total_iterations'],
                "timestamp": iteration_timestamp,
                "stage": "completed",
                "papers_processed": self.stats['papers_processed'],
                "posts_generated": self.stats['posts_generated']
            })
            tavily_calls_end = getattr(self.paper_finder, "tavily_calls", 0)
            gemini_calls_end = getattr(self.post_generator, "gemini_calls", 0)
            tavily_calls_delta = max(0, tavily_calls_end - tavily_calls_start)
            gemini_calls_delta = max(0, gemini_calls_end - gemini_calls_start)
            print(f"[CHART] Stats - Iterations: {self.stats['total_iterations']}, "
                  f"Papers: {self.stats['papers_processed']}, Posts: {self.stats['posts_generated']}")
            print(f"[TOOL] API calls this run - Tavily: {tavily_calls_delta}, Gemini: {gemini_calls_delta}")
            self._print_learning_snapshot(10)
    
    def _categorize_topic(self, title: str) -> str:
        """Categorize the paper topic based on keywords in the title"""
        title_lower = title.lower()
        
        categories = {
            'clinical biochemistry': ['biochemistry', 'enzyme', 'metabolite', 'protein', 'assay'],
            'metabolism': ['metabolism', 'metabolic', 'glucose', 'lipid', 'energy', 'pathway'],
            'metabolic disease': ['diabetes', 'obesity', 'disease', 'syndrome', 'disorder', 'condition'],
            'human physiology': ['physiology', 'human', 'organ', 'tissue', 'cellular', 'function'],
            'biotechnology': ['biotech', 'therapy', 'treatment', 'drug', 'pharma', 'biological'],
            'health science insights': ['health', 'medical', 'clinic', 'patient', 'treatment', 'care'],
            'emerging biomedical discoveries': ['novel', 'discovery', 'new', 'recent', 'innovative', 'breakthrough']
        }
        
        for category, keywords in categories.items():
            if any(keyword in title_lower for keyword in keywords):
                return category
        
        return 'general'

    def _print_learning_snapshot(self, last_n: int = 10):
        """Print a brief rolling performance summary."""
        experiments = self.learning_loop.memory.get('experiments', [])
        if not experiments:
            print("[LEARN] No experiments yet to summarize")
            return

        recent = experiments[-last_n:]
        if not recent:
            print("[LEARN] No recent experiments to summarize")
            return

        scores = [exp.get('curiosity_score', 0) for exp in recent]
        successes = [exp.get('success', False) for exp in recent]
        avg_score = sum(scores) / len(scores) if scores else 0
        success_rate = sum(1 for s in successes if s) / len(successes) if successes else 0
        print(f"[LEARN] Last {len(recent)} posts - Avg curiosity: {avg_score:.1f}/50, Success rate: {success_rate:.0%}")

    def _append_results_tsv(self, row: Dict[str, object], tsv_path: str = "bio_results.tsv"):
        """Append a row to the bio_results.tsv file, adding a header if needed."""
        header = [
            "timestamp",
            "paper_title",
            "authors",
            "journal",
            "year",
            "url",
            "paper_score",
            "model",
            "curiosity_score",
            "curiosity_scores",
            "hashtags",
            "status",
        ]

        def _stringify(value: object) -> str:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            else:
                value = str(value)
            return value.replace("\t", " ").replace("\r", " ").replace("\n", " ")

        file_exists = os.path.exists(tsv_path)
        write_header = (not file_exists) or os.path.getsize(tsv_path) == 0

        with open(tsv_path, "a", encoding="utf-8", newline="") as f:
            if write_header:
                f.write("\t".join(header) + "\n")
            values = [_stringify(row.get(key, "")) for key in header]
            f.write("\t".join(values) + "\n")

    def _write_checkpoint(self, path: str, payload: Dict[str, object]):
        """Write a lightweight checkpoint file for iteration progress."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    
    def print_stats(self):
        """Print current statistics"""
        runtime = datetime.now() - self.stats['start_time']
        print(f"\n[CHART] PIPELINE STATISTICS")
        print(f"Runtime: {runtime}")
        print(f"Total iterations: {self.stats['total_iterations']}")
        print(f"Papers processed: {self.stats['papers_processed']}")
        print(f"Posts generated: {self.stats['posts_generated']}")
        if self.stats['total_iterations'] > 0:
            print(f"Avg. time per iteration: {runtime.total_seconds() / self.stats['total_iterations']:.2f}s")
    
    def run_continuous(self, interval_minutes: int = 60):
        """Run the pipeline continuously with specified interval"""
        print(f"[ROCKET] Starting continuous pipeline (interval: {interval_minutes} minutes)")
        
        try:
            while True:
                self.run_pipeline()
                
                print(f"\n[TIMER] Waiting {interval_minutes} minutes until next iteration...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n[STOP] Pipeline interrupted by user")
        except Exception as e:
            print(f"\n[CROSS] Fatal error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.print_stats()
            self.learning_loop.print_learning_summary()

def main():
    parser = argparse.ArgumentParser(description='AutoResearch Bio-Medical Pipeline')
    parser.add_argument('--run-once', action='store_true', help='Run a single iteration and exit')
    parser.add_argument('--continuous', action='store_true', help='Run continuously (default)')
    parser.add_argument('--interval', type=int, default=60, help='Interval in minutes for continuous mode (default: 60)')
    parser.add_argument('--print-learning', action='store_true', help='Print learning summary and exit')
    
    args = parser.parse_args()
    
    # Check for required environment variables
    if not os.getenv('TAVILY_API_KEY'):
        print("[CROSS] Error: TAVILY_API_KEY environment variable not set")
        print("Please set your Tavily API key before running the pipeline")
        print("\nExample .env file:")
        print("TAVILY_API_KEY=your_actual_tavily_api_key_here")
        print("GEMINI_API_KEY_1=your_primary_gemini_key")
        print("GEMINI_MODEL=gemini-1.5-pro")
        sys.exit(1)
    
    autoresearch_bio = AutoResearchBio()
    
    if args.print_learning:
        autoresearch_bio.learning_loop.print_learning_summary()
        return
    
    if args.run_once:
        autoresearch_bio.run_pipeline()
        autoresearch_bio.print_stats()
        autoresearch_bio.learning_loop.print_learning_summary()
    elif args.continuous or not (args.run_once or args.print_learning):
        autoresearch_bio.run_continuous(args.interval)
    else:
        autoresearch_bio.run_continuous(args.interval)

if __name__ == "__main__":
    main()
