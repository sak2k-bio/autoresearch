"""
KeywordGenerator module for AutoResearch Bio-Medical Pipeline
Generates research keywords using specified patterns
"""

import random
from typing import List
from .config import config


class KeywordGenerator:
    def __init__(self):
        self.patterns = config.KEYWORD_PATTERNS
        self.categories = config.TOPIC_CATEGORIES
        self.used_keywords = set()

    def generate_keywords(self, count: int = 5) -> List[str]:
        """
        Generate a list of research keywords based on patterns and categories

        Args:
            count: Number of keywords to generate

        Returns:
            List of research keywords
        """
        keywords = []

        while len(keywords) < count:
            # Randomly select a pattern and category
            pattern = random.choice(self.patterns)
            category = random.choice(self.categories)

            # Combine them to create a keyword
            keyword = f"{pattern} {category}"

            # Avoid duplicates
            if keyword not in self.used_keywords:
                self.used_keywords.add(keyword)
                keywords.append(keyword)

        return keywords

    def generate_topic_biased_keywords(self, topic_performance: dict = None, count: int = 5) -> List[str]:
        """
        Generate keywords biased toward topics that perform well

        Args:
            topic_performance: Dictionary with topic scores
            count: Number of keywords to generate

        Returns:
            List of research keywords biased toward high-performing topics
        """
        if not topic_performance:
            return self.generate_keywords(count)

        # Sort topics by performance score
        sorted_topics = sorted(topic_performance.items(), key=lambda x: x[1], reverse=True)

        # Take top performing topics
        top_topics = [topic for topic, score in sorted_topics[:3]]

        keywords = []
        while len(keywords) < count:
            # Use top performing topics more frequently
            if random.random() < 0.7:  # 70% chance to use high-performing topic
                category = random.choice(top_topics)
            else:
                category = random.choice(self.categories)

            pattern = random.choice(self.patterns)
            keyword = f"{pattern} {category}"

            if keyword not in self.used_keywords:
                self.used_keywords.add(keyword)
                keywords.append(keyword)

        return keywords


# Example usage:
if __name__ == "__main__":
    generator = KeywordGenerator()

    # Basic keyword generation
    keywords = generator.generate_keywords(5)
    print("Generated keywords:", keywords)

    # Example topic performance bias
    topic_performance = {
        "mitochondria": 82,
        "gut_microbiome": 74,
        "metabolic_flexibility": 91,
        "lipid_signaling": 68
    }

    biased_keywords = generator.generate_topic_biased_keywords(topic_performance, 5)
    print("Biased keywords:", biased_keywords)