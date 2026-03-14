"""
LearningLoop module for AutoResearch Bio-Medical Pipeline
Manages autonomous improvement loop
"""

import os
import json
from datetime import datetime
from typing import Dict, List
from collections import defaultdict

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
            'success': experiment_data.get('success', False),
            'topic_category': experiment_data.get('topic_category', 'unknown')
        }
        
        self.memory['experiments'].append(experiment_record)
        self.save_memory()
    
    def analyze_performance(self) -> Dict:
        """Analyze performance patterns from memory"""
        if not self.memory['experiments']:
            return {}
        
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
                'average_score': sum(
                    exp.get('score', 0) for exp in experiments
                ) / total if total > 0 else 0
            }
        
        # Find high-performing experiments
        high_performers = [
            exp for exp in self.memory['experiments'] 
            if exp.get('success', False) and exp.get('score', 0) >= 40
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
        
        # Calculate high performers count
        high_performers = [exp for exp in self.memory['experiments'] if exp.get('success', False) and exp.get('score', 0) >= 40]
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