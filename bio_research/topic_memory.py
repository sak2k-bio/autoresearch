"""
TopicMemory module for AutoResearch Bio-Medical Pipeline
Tracks topic performance and biases toward higher-performing themes
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict
from .config import config


class TopicMemory:
    def __init__(self, memory_file: str = "topic_memory.json"):
        self.memory_file = memory_file
        self.topic_performance = defaultdict(lambda: {
            'total_score': 0.0,
            'count': 0,
            'avg_score': 0.0,
            'posts_generated': 0,
            'last_updated': None
        })

        # Load existing memory if file exists
        self.load_memory()

    def load_memory(self):
        """
        Load topic memory from file
        """
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for topic, stats in data.items():
                    self.topic_performance[topic] = {
                        'total_score': stats.get('total_score', 0.0),
                        'count': stats.get('count', 0),
                        'avg_score': stats.get('avg_score', 0.0),
                        'posts_generated': stats.get('posts_generated', 0),
                        'last_updated': stats.get('last_updated')
                    }
            except (json.JSONDecodeError, FileNotFoundError):
                print(f"Could not load topic memory from {self.memory_file}, starting fresh")
                self.topic_performance.clear()

    def save_memory(self):
        """
        Save topic memory to file
        """
        data = {}
        for topic, stats in self.topic_performance.items():
            data[topic] = {
                'total_score': stats['total_score'],
                'count': stats['count'],
                'avg_score': stats['avg_score'],
                'posts_generated': stats['posts_generated'],
                'last_updated': stats['last_updated']
            }

        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def update_topic_performance(self, topic: str, score: float):
        """
        Update the performance statistics for a topic

        Args:
            topic: The topic name
            score: The performance score (0-1 scale)
        """
        current = self.topic_performance[topic]

        # Update statistics
        current['total_score'] += score
        current['count'] += 1
        current['avg_score'] = current['total_score'] / current['count']
        current['posts_generated'] += 1
        current['last_updated'] = datetime.now().isoformat()

        # Save to file
        self.save_memory()

    def get_top_performing_topics(self, n: int = 5) -> List[tuple]:
        """
        Get the top N performing topics

        Args:
            n: Number of top topics to return

        Returns:
            List of tuples (topic, avg_score) sorted by score descending
        """
        # Sort topics by average score, descending
        sorted_topics = sorted(
            self.topic_performance.items(),
            key=lambda x: x[1]['avg_score'],
            reverse=True
        )

        # Return top N topics with their average scores
        return [(topic, stats['avg_score']) for topic, stats in sorted_topics[:n]]

    def get_topic_performance_table(self) -> List[Dict[str, any]]:
        """
        Get a table of topic performance for analysis

        Returns:
            List of dictionaries with topic performance data
        """
        table = []
        for topic, stats in self.topic_performance.items():
            table.append({
                'topic': topic,
                'avg_score': round(stats['avg_score'], 2),
                'posts_generated': stats['posts_generated'],
                'total_score': round(stats['total_score'], 2),
                'count': stats['count']
            })

        # Sort by average score descending
        table.sort(key=lambda x: x['avg_score'], reverse=True)
        return table

    def bias_keywords(self, keywords: List[str], top_n: int = 3) -> List[str]:
        """
        Bias keywords toward high-performing topics based on historical performance

        Args:
            keywords: List of candidate keywords
            top_n: Number of top performing topics to prioritize

        Returns:
            List of keywords with high-performing ones prioritized
        """
        return self.get_performance_bias(keywords, top_n)

    def get_performance_bias(self, topics: List[str], top_n: int = 3) -> List[str]:
        """
        Get a list of topics biased toward high performers

        Args:
            topics: List of candidate topics
            top_n: Number of top performing topics to include

        Returns:
            List of topics with high-performing ones prioritized
        """
        top_performers = [topic for topic, _ in self.get_top_performing_topics(top_n)]

        # Create a list with high performers first, then others
        biased_list = []

        # Add top performers that are in the input list
        for topic in top_performers:
            if topic in topics and topic not in biased_list:
                biased_list.append(topic)

        # Add remaining topics that weren't in top performers
        for topic in topics:
            if topic not in biased_list:
                biased_list.append(topic)

        return biased_list

    def get_performance_summary(self) -> Dict[str, any]:
        """
        Get a summary of overall performance

        Returns:
            Dictionary with performance summary statistics
        """
        if not self.topic_performance:
            return {
                'total_topics_tracked': 0,
                'total_posts_generated': 0,
                'overall_avg_score': 0.0,
                'top_performing_topic': None,
                'topics_with_high_performance': []
            }

        total_posts = sum(stats['posts_generated'] for stats in self.topic_performance.values())
        overall_avg = sum(stats['total_score'] for stats in self.topic_performance.values()) / \
                     sum(stats['count'] for stats in self.topic_performance.values()) if sum(stats['count']) > 0 else 0.0

        # Find top performing topic
        top_topic = max(self.topic_performance.items(), key=lambda x: x[1]['avg_score'])

        # Find topics with high performance (>0.7)
        high_performers = [topic for topic, stats in self.topic_performance.items()
                          if stats['avg_score'] > 0.7]

        return {
            'total_topics_tracked': len(self.topic_performance),
            'total_posts_generated': total_posts,
            'overall_avg_score': round(overall_avg, 2),
            'top_performing_topic': {
                'name': top_topic[0],
                'score': round(top_topic[1]['avg_score'], 2)
            } if top_topic[1]['avg_score'] > 0 else None,
            'topics_with_high_performance': high_performers
        }


# Example usage:
if __name__ == "__main__":
    memory = TopicMemory()

    # Example: Update topic performance
    memory.update_topic_performance("mitochondria", 0.82)
    memory.update_topic_performance("gut_microbiome", 0.74)
    memory.update_topic_performance("metabolic_flexibility", 0.91)
    memory.update_topic_performance("lipid_signaling", 0.68)

    # Add more data for the same topics
    memory.update_topic_performance("mitochondria", 0.78)
    memory.update_topic_performance("metabolic_flexibility", 0.93)

    print("Top performing topics:")
    for topic, score in memory.get_top_performing_topics(5):
        print(f"  {topic}: {score:.2f}")

    print("\nTopic performance table:")
    table = memory.get_topic_performance_table()
    for row in table:
        print(f"  {row['topic']}: avg={row['avg_score']}, posts={row['posts_generated']}")

    print("\nPerformance summary:")
    summary = memory.get_performance_summary()
    print(f"  Total topics tracked: {summary['total_topics_tracked']}")
    print(f"  Total posts generated: {summary['total_posts_generated']}")
    print(f"  Overall average score: {summary['overall_avg_score']}")
    if summary['top_performing_topic']:
        print(f"  Top performing topic: {summary['top_performing_topic']['name']} ({summary['top_performing_topic']['score']})")
    print(f"  High performance topics: {summary['topics_with_high_performance']}")

    # Example of getting bias toward high performers
    candidate_topics = ["mitochondria", "new_topic", "gut_microbiome", "another_topic"]
    biased_topics = memory.get_performance_bias(candidate_topics, top_n=2)
    print(f"\nBiased topic order: {biased_topics}")