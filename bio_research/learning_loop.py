"""
LearningLoop module for AutoResearch Bio-Medical Pipeline
Manages autonomous improvement loop
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict

from .config import config

class LearningLoop:
    def __init__(self, memory_file='learning_memory.json'):
        self.memory_file = memory_file
        self.load_memory()
    
    def load_memory(self):
        """Load learning memory from file"""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                self.memory = json.load(f)
        else:
            self.memory = {
                'experiments': [],
                'performance_history': [],
                'learnings': []
            }
    
    def save_memory(self):
        """Save learning memory to file"""
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def record_experiment(self, experiment_data: Dict):
        """Record a new experiment and its outcome"""
        experiment_record = {
            'timestamp': datetime.now().isoformat(),
            'experiment': experiment_data,
            'outcome': experiment_data.get('outcome', 'unknown'),
            'outcome_score': experiment_data.get('outcome_score'),
            'success': experiment_data.get('success', False),
            'topic_category': experiment_data.get('topic_category', 'unknown')
        }
        
        self.memory['experiments'].append(experiment_record)
        self.save_memory()

    def _compute_outcome_score(self, outcome: Dict) -> float:
        """
        Compute a normalized outcome score (0-1) from engagement metrics.
        Expected keys: impressions, clicks, likes, comments, shares, saves.
        """
        impressions = float(outcome.get('impressions') or 0)
        if impressions <= 0:
            return 0.0

        clicks = float(outcome.get('clicks') or 0)
        likes = float(outcome.get('likes') or 0)
        comments = float(outcome.get('comments') or 0)
        shares = float(outcome.get('shares') or 0)
        saves = float(outcome.get('saves') or 0)

        weighted = clicks + likes + (comments * 2.0) + (shares * 3.0) + (saves * 2.0)
        engagement_rate = weighted / impressions

        # Normalize: 5% weighted engagement rate maps to 1.0
        return min(1.0, engagement_rate / 0.05)

    def record_outcome(
        self,
        experiment_timestamp: str,
        outcome: Dict,
        outcome_score: Optional[float] = None,
        success: Optional[bool] = None,
    ) -> Dict:
        """
        Record outcome for a previously recorded experiment.
        Returns a summary of the update.
        """
        if outcome_score is None:
            outcome_score = self._compute_outcome_score(outcome)

        if success is None:
            success = outcome_score >= config.MIN_OUTCOME_SCORE

        matched = None
        for exp in reversed(self.memory.get('experiments', [])):
            exp_ts = exp.get('experiment', {}).get('timestamp')
            if exp_ts == experiment_timestamp:
                matched = exp
                break

        if matched is None:
            # Create a placeholder experiment entry if missing
            matched = {
                'timestamp': datetime.now().isoformat(),
                'experiment': {'timestamp': experiment_timestamp},
                'outcome': 'unknown',
                'outcome_score': None,
                'success': False,
                'topic_category': 'unknown'
            }
            self.memory['experiments'].append(matched)

        matched['outcome'] = outcome
        matched['outcome_score'] = outcome_score
        matched['success'] = success

        performance_entry = {
            'timestamp': datetime.now().isoformat(),
            'experiment_timestamp': experiment_timestamp,
            'topic_category': matched.get('topic_category', 'unknown'),
            'paper_title': matched.get('experiment', {}).get('paper_title'),
            'hook_used': matched.get('experiment', {}).get('hook_used'),
            'paper_score': matched.get('experiment', {}).get('paper_score'),
            'curiosity_score': matched.get('experiment', {}).get('curiosity_score'),
            'outcome_score': outcome_score,
            'outcome': outcome
        }
        self.memory['performance_history'].append(performance_entry)
        self.save_memory()

        return {
            'experiment_timestamp': experiment_timestamp,
            'outcome_score': outcome_score,
            'success': success,
            'matched': matched is not None
        }

    def record_learning(self, learning: Dict):
        """Record a learning summary entry."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            **learning
        }
        self.memory['learnings'].append(entry)
        self.save_memory()

    def ingest_outcomes_tsv(self, outcomes_path: str, topic_memory=None) -> Dict:
        """
        Ingest outcomes from a TSV file and update learning memory (and topic memory).

        Expected columns:
          timestamp, impressions, clicks, likes, comments, shares, saves, outcome_score (optional)
        """
        if not os.path.exists(outcomes_path):
            return {'updated': 0, 'missing': 0, 'error': f"File not found: {outcomes_path}"}

        updated = 0
        missing = 0
        outcome_topics = []
        with open(outcomes_path, 'r', encoding='utf-8') as f:
            header = f.readline().strip().split("\t")
            for line in f:
                if not line.strip():
                    continue
                parts = line.rstrip("\n").split("\t")
                row = dict(zip(header, parts))

                exp_ts = row.get('timestamp')
                if not exp_ts:
                    continue

                outcome = {
                    'impressions': row.get('impressions'),
                    'clicks': row.get('clicks'),
                    'likes': row.get('likes'),
                    'comments': row.get('comments'),
                    'shares': row.get('shares'),
                    'saves': row.get('saves'),
                    'notes': row.get('notes')
                }

                outcome_score = row.get('outcome_score')
                outcome_score = float(outcome_score) if outcome_score not in (None, "", "None") else None

                result = self.record_outcome(exp_ts, outcome, outcome_score=outcome_score)
                updated += 1

                # Update topic memory with outcome-based score (0-1 scale)
                if topic_memory is not None:
                    topic = None
                    for exp in reversed(self.memory.get('experiments', [])):
                        if exp.get('experiment', {}).get('timestamp') == exp_ts:
                            topic = exp.get('topic_category', 'unknown')
                            break
                    if topic:
                        topic_memory.update_topic_performance(topic, result['outcome_score'])
                        outcome_topics.append((topic, result['outcome_score']))

        if outcome_topics:
            topic_scores = defaultdict(list)
            for topic, score in outcome_topics:
                topic_scores[topic].append(score)
            top_topics = sorted(
                ((topic, sum(scores)/len(scores)) for topic, scores in topic_scores.items()),
                key=lambda x: x[1],
                reverse=True
            )
            self.record_learning({
                'type': 'outcome_ingest',
                'top_topics': top_topics[:5],
                'sample_size': len(outcome_topics)
            })

        return {'updated': updated, 'missing': missing}

    def append_outcome_tsv(self, outcomes_path: str, row: Dict) -> None:
        """
        Append a single outcome row to a TSV file, creating it with a header if needed.
        """
        header = [
            "timestamp",
            "impressions",
            "clicks",
            "likes",
            "comments",
            "shares",
            "saves",
            "outcome_score",
            "notes",
        ]

        def _stringify(value: object) -> str:
            if value is None:
                return ""
            value = str(value)
            return value.replace("\t", " ").replace("\r", " ").replace("\n", " ")

        file_exists = os.path.exists(outcomes_path)
        write_header = (not file_exists) or os.path.getsize(outcomes_path) == 0

        with open(outcomes_path, "a", encoding="utf-8", newline="") as f:
            if write_header:
                f.write("\t".join(header) + "\n")
            values = [_stringify(row.get(key, "")) for key in header]
            f.write("\t".join(values) + "\n")
    
    def analyze_performance(self) -> Dict:
        """Analyze performance patterns from memory"""
        if not self.memory['experiments']:
            return {}

        def _exp_score(exp: Dict) -> float:
            if exp.get('outcome_score') is not None:
                return exp.get('outcome_score', 0) * 50.0
            exp_data = exp.get('experiment', {})
            return float(exp_data.get('curiosity_score', 0) or 0)
        
        # Group experiments by topic category
        by_category = defaultdict(list)
        for exp in self.memory['experiments']:
            category = exp.get('topic_category', 'unknown')
            by_category[category].append(exp)
        
        # Calculate success rates by category
        category_performance = {}
        for category, experiments in by_category.items():
            total = len(experiments)
            successful = sum(1 for exp in experiments if exp.get('success', False))
            category_performance[category] = {
                'total_experiments': total,
                'successful_experiments': successful,
                'success_rate': successful / total if total > 0 else 0,
                'average_score': sum(_exp_score(exp) for exp in experiments) / total if total > 0 else 0
            }
        
        # Find high-performing experiments
        high_performers = [
            exp for exp in self.memory['experiments'] 
            if exp.get('success', False) and _exp_score(exp) >= 40
        ]
        
        # Identify patterns in high performers
        patterns = {
            'successful_topics': [exp['topic_category'] for exp in high_performers],
            'common_hooks': [],
            'effective_keywords': [],
            'best_paper_types': []
        }
        
        # Count topic frequency among high performers
        topic_counts = defaultdict(int)
        for exp in high_performers:
            topic = exp.get('topic_category', 'unknown')
            topic_counts[topic] += 1
        
        if topic_counts:
            patterns['most_successful_topic'] = max(topic_counts.items(), key=lambda x: x[1])[0]
        else:
            patterns['most_successful_topic'] = 'unknown'
        
        return {
            'category_performance': category_performance,
            'high_performers_count': len(high_performers),
            'patterns': patterns
        }
    
    def get_adaptation_strategies(self) -> List[str]:
        """Get strategies for adapting based on performance"""
        analysis = self.analyze_performance()
        
        strategies = []
        
        # Strategy based on category performance
        if analysis.get('category_performance'):
            best_category_items = list(analysis['category_performance'].items())
            if best_category_items:
                try:
                    best_category = max(best_category_items, key=lambda x: x[1]['success_rate'])[0]
                    
                    if best_category and analysis['category_performance'][best_category]['success_rate'] > 0.6:
                        strategies.append(f"Focus more on '{best_category}' topics - they have high success rate")
                except:
                    pass  # Handle case where max() fails
        
        # Strategy based on patterns
        if analysis.get('patterns', {}).get('most_successful_topic'):
            topic = analysis['patterns']['most_successful_topic']
            if topic != 'unknown':
                strategies.append(f"Increase frequency of '{topic}' related research")
        
        # General improvement strategies
        if len(self.memory['experiments']) < 10:
            strategies.append("Continue experimenting with different approaches - not enough data yet")
        elif len([exp for exp in self.memory['experiments'] if exp.get('success', False)]) < 3:
            strategies.append("Try more diverse approaches to improve performance")
        else:
            strategies.append("Maintain current successful strategies while exploring refinements")
        
        return strategies
    
    def adapt_behavior(self, current_behavior: Dict) -> Dict:
        """Adapt behavior based on learning"""
        strategies = self.get_adaptation_strategies()
        
        # Apply adaptations based on strategies
        adapted_behavior = current_behavior.copy()
        
        for strategy in strategies:
            if 'focus more on' in strategy.lower() and "'" in strategy:
                topic = strategy.split("'")[1]  # Extract topic from strategy
                if 'preferred_topics' not in adapted_behavior:
                    adapted_behavior['preferred_topics'] = []
                if topic not in adapted_behavior['preferred_topics']:
                    adapted_behavior['preferred_topics'].append(topic)
            
            if 'increase frequency' in strategy.lower() and "'" in strategy:
                topic = strategy.split("'")[1]  # Extract topic from strategy
                if 'frequency_bias' not in adapted_behavior:
                    adapted_behavior['frequency_bias'] = {}
                adapted_behavior['frequency_bias'][topic] = adapted_behavior['frequency_bias'].get(topic, 1) * 1.5
        
        return adapted_behavior
    
    def print_learning_summary(self):
        """Print a summary of learned patterns"""
        analysis = self.analyze_performance()

        print("="*60)
        print("AUTO LEARNING SUMMARY")
        print("="*60)
        
        print(f"\nTotal Experiments: {len(self.memory['experiments'])}")
        
        if analysis.get('category_performance'):
            print(f"\nCategory Performance:")
            for category, perf in analysis['category_performance'].items():
                print(f"  {category}: {perf['success_rate']:.2%} success rate "
                      f"({perf['successful_experiments']}/{perf['total_experiments']})")
        
        def _exp_score(exp: Dict) -> float:
            if exp.get('outcome_score') is not None:
                return exp.get('outcome_score', 0) * 50.0
            exp_data = exp.get('experiment', {})
            return float(exp_data.get('curiosity_score', 0) or 0)

        # Calculate high performers count
        high_performers = [exp for exp in self.memory['experiments'] if exp.get('success', False) and _exp_score(exp) >= 40]
        high_performer_count = len(high_performers)
        
        if len(self.memory['experiments']) > 0:
            print(f"\nHigh Performers: {high_performer_count} "
                  f"({high_performer_count/len(self.memory['experiments']):.2%} of all experiments)")
        
        if analysis.get('patterns', {}).get('most_successful_topic') and analysis['patterns']['most_successful_topic'] != 'unknown':
            print(f"\nMost Successful Topic: {analysis['patterns']['most_successful_topic']}")
        
        strategies = self.get_adaptation_strategies()
        if strategies:
            print(f"\nAdaptation Strategies:")
            for i, strategy in enumerate(strategies, 1):
                print(f"  {i}. {strategy}")
        
        print("="*60)
