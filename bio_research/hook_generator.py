"""
HookGenerator module for AutoResearch Bio-Medical Pipeline
Generates 10 possible hooks for each paper and selects the best one
"""

import random
from typing import Dict, List
from .config import config


class HookGenerator:
    def __init__(self):
        self.hook_templates = [
            # Surprising discovery hooks
            "Scientists just discovered something surprising about {topic}.",
            "Researchers have uncovered a {adj} new {aspect} that changes everything.",
            "A new study reveals something unexpected about {topic}.",
            "Scientists have made a {adj} discovery that challenges what we thought we knew about {topic}.",

            # Contrarian hooks
            "Most people think {common_belief}. But new research suggests otherwise.",
            "Everyone believes {common_belief}. Scientists now think they're wrong.",
            "What if everything we knew about {topic} was backwards?",

            # Revelation hooks
            "Here's what scientists just learned about {topic}.",
            "Scientists have finally figured out how {topic} really works.",
            "New research explains the {adj} mechanism behind {topic}.",

            # Impact hooks
            "This {adj} discovery about {topic} could change how we approach {related_aspect}.",
            "Scientists reveal why {topic} matters more than we thought.",
            "A groundbreaking study shows the real connection between {aspect1} and {aspect2}.",

            # Process hooks
            "{Aspect} doesn't work the way scientists thought. Here's what's really happening.",
            "Researchers have decoded the {adj} pathway that controls {topic}.",
            "Scientists have mapped the {adj} mechanism that drives {topic}.",

            # Challenge hooks
            "Scientists are rethinking their understanding of {topic}. Here's why.",
            "Traditional views of {topic} are being turned upside down by new research.",
            "A {adj} new theory is changing how scientists think about {topic}.",
        ]

        self.adjectives = [
            "surprising", "unexpected", "groundbreaking", "revolutionary", "novel",
            "counterintuitive", "remarkable", "fascinating", "intriguing", "paradoxical",
            "paradigm-shifting", "game-changing", "unprecedented", "innovative", "breakthrough"
        ]

        self.topic_variations = {
            "insulin resistance": ["insulin sensitivity", "blood sugar regulation", "diabetes development"],
            "mitochondrial function": ["cellular energy", "mitochondrial health", "cellular powerhouses"],
            "metabolic flexibility": ["metabolic adaptation", "energy switching", "fuel utilization"],
            "glucose metabolism": ["sugar processing", "energy metabolism", "carbohydrate handling"],
            "lipid signaling": ["fat messaging", "lipid communication", "fat-based signals"],
            "biochemical pathways": ["cellular processes", "molecular pathways", "biochemical processes"]
        }

    def generate_hooks(self, paper_data: Dict, insights: Dict) -> List[str]:
        """
        Generate 10 hooks for a paper based on its content

        Args:
            paper_data: Dictionary containing paper information
            insights: Dictionary containing extracted insights

        Returns:
            List of 10 generated hooks
        """
        hooks = []

        # Use the paper title and insights to fill in template variables
        title = paper_data.get('title', '').lower()
        abstract = paper_data.get('abstract', '').lower()

        # Extract key concepts from the paper
        topic = self._extract_topic(title, insights)
        aspect = self._extract_aspect(title, insights)
        common_belief = self._extract_common_belief(abstract, insights)
        adj = random.choice(self.adjectives)

        # Generate hooks using templates
        for i in range(10):
            template = random.choice(self.hook_templates)

            filled_hook = template.format(
                topic=topic,
                aspect=aspect,
                adj=adj,
                common_belief=common_belief,
                Aspect=aspect.capitalize(),
                aspect1=self._get_related_aspect(topic, "first"),
                aspect2=self._get_related_aspect(topic, "second"),
                related_aspect=self._get_related_aspect(topic, "first")
            )

            # Clean up the hook
            filled_hook = self._clean_hook(filled_hook)
            hooks.append(filled_hook)

        # Ensure variety by selecting from different template categories
        return self._ensure_variety(hooks)

    def _extract_topic(self, title: str, insights: Dict) -> str:
        """
        Extract the main topic from the paper
        """
        # Look in insights first
        key_discovery = insights.get('key_discovery', '').lower()
        if key_discovery:
            # Try to extract the main topic
            import re
            # Look for common topic phrases
            topic_patterns = [
                r"(\w+ resistance)",
                r"(\w+ metabolism)",
                r"(\w+ signaling)",
                r"(\w+ pathway)",
                r"(\w+ function)",
                r"(\w+ regulation)",
            ]

            for pattern in topic_patterns:
                match = re.search(pattern, key_discovery)
                if match:
                    return match.group(1)

        # If not in insights, try the title
        for pattern in topic_patterns:
            match = re.search(pattern, title)
            if match:
                return match.group(1)

        # Default to a general topic
        return "this biological process"

    def _extract_aspect(self, title: str, insights: Dict) -> str:
        """
        Extract the specific aspect being studied
        """
        # Look for specific aspects in the title or insights
        key_discovery = insights.get('key_discovery', '').lower()

        aspect_indicators = [
            "mechanism", "pathway", "process", "discovery", "finding",
            "regulation", "function", "role", "effect", "relationship"
        ]

        for indicator in aspect_indicators:
            if indicator in key_discovery:
                return indicator

        for indicator in aspect_indicators:
            if indicator in title:
                return indicator

        return "discovery"

    def _extract_common_belief(self, abstract: str, insights: Dict) -> str:
        """
        Extract what the common belief was that this study challenges
        """
        surprising_insight = insights.get('surprising_insight', '').lower()

        # Look for phrases that indicate challenged beliefs
        challenge_phrases = [
            "contrary to", "challenges", "differs from", "opposite to",
            "not what was expected", "unexpectedly", "surprisingly"
        ]

        for phrase in challenge_phrases:
            if phrase in surprising_insight:
                # Extract what was believed
                parts = surprising_insight.split(phrase)
                if len(parts) > 1:
                    return parts[0].strip() or f"the traditional view of {self._extract_topic('', insights)}"

        return f"the traditional understanding of {self._extract_topic('', insights)}"

    def _get_related_aspect(self, topic: str, position: str) -> str:
        """
        Get a related aspect for comparison hooks
        """
        # Map topics to related aspects
        related_aspects = {
            "insulin resistance": ["cell function", "blood sugar"],
            "mitochondrial function": ["cellular energy", "metabolic health"],
            "metabolic flexibility": ["energy adaptation", "fuel switching"],
            "glucose metabolism": ["energy processing", "sugar regulation"],
            "lipid signaling": ["fat communication", "cell messaging"],
            "biochemical pathways": ["cellular processes", "molecular interactions"]
        }

        topic_pair = related_aspects.get(topic, ["the process", "the outcome"])

        if position == "first":
            return topic_pair[0]
        else:
            return topic_pair[1]

    def _clean_hook(self, hook: str) -> str:
        """
        Clean up the generated hook
        """
        # Remove extra spaces
        hook = ' '.join(hook.split())

        # Ensure proper capitalization
        if hook:
            hook = hook[0].upper() + hook[1:] if hook else ""

        # Ensure it ends with a period
        if hook and not hook.endswith('.'):
            hook += '.'

        return hook

    def _ensure_variety(self, hooks: List[str]) -> List[str]:
        """
        Ensure variety in the generated hooks
        """
        # Remove duplicates while preserving order
        seen = set()
        unique_hooks = []
        for hook in hooks:
            if hook not in seen:
                seen.add(hook)
                unique_hooks.append(hook)

        # If we have fewer than 10 unique hooks, pad with variations
        while len(unique_hooks) < 10:
            original = random.choice(unique_hooks)
            # Make a slight variation
            variation = self._make_variation(original)
            if variation not in seen:
                seen.add(variation)
                unique_hooks.append(variation)

        # Return first 10
        return unique_hooks[:10]

    def _make_variation(self, hook: str) -> str:
        """
        Make a slight variation of a hook
        """
        # Simple variation by changing a word
        variations = {
            "Scientists": "Researchers",
            "Researchers": "Experts",
            "discovered": "found",
            "reveals": "shows",
            "challenges": "questions",
            "unexpected": "surprising"
        }

        for original, replacement in variations.items():
            if original in hook:
                return hook.replace(original, replacement, 1)

        # If no suitable variation found, append a qualifier
        qualifiers = [" surprisingly", " remarkably", " importantly"]
        return hook[:-1] + random.choice(qualifiers) + "."

    def select_best_hook(self, hooks: List[str], paper_data: Dict) -> str:
        """
        Select the best hook based on engagement potential
        """
        # For now, we'll use a simple scoring method
        # In a real implementation, this would use an LLM to score the hooks
        scored_hooks = [(hook, self._score_hook(hook, paper_data)) for hook in hooks]

        # Sort by score and return the best one
        best_hook = max(scored_hooks, key=lambda x: x[1])[0]
        return best_hook

    def _score_hook(self, hook: str, paper_data: Dict) -> float:
        """
        Score a hook based on engagement potential
        """
        score = 0.0

        # Bonus for curiosity-inducing words
        curiosity_words = ["surprising", "unexpected", "challenging", "reveals", "discovers", "new"]
        for word in curiosity_words:
            if word.lower() in hook.lower():
                score += 0.2

        # Bonus for contrarian statements
        contrarian_phrases = ["but", "however", "yet", "though"]
        for phrase in contrarian_phrases:
            if phrase in hook.lower():
                score += 0.15

        # Length bonus (hooks that are neither too short nor too long)
        if 10 < len(hook) < 80:
            score += 0.1

        # Cap the score
        return min(1.0, score)


# Example usage:
if __name__ == "__main__":
    generator = HookGenerator()

    # Example paper data
    example_paper = {
        'title': 'Mitochondrial dysfunction initiates insulin resistance through oxidative stress',
        'abstract': 'Our study demonstrates that mitochondrial dysfunction precedes insulin resistance, challenging the traditional view that insulin resistance occurs first. We found that nutrient excess leads to mitochondrial overload, causing increased ROS production which subsequently impairs insulin signaling.'
    }

    example_insights = {
        'key_discovery': 'Mitochondrial dysfunction initiates insulin resistance',
        'surprising_insight': 'This challenges the traditional view that insulin resistance occurs first',
        'clinical_significance': 'Therapeutic interventions targeting mitochondria could be more effective'
    }

    hooks = generator.generate_hooks(example_paper, example_insights)

    print("Generated hooks:")
    for i, hook in enumerate(hooks, 1):
        print(f"{i}. {hook}")

    best_hook = generator.select_best_hook(hooks, example_paper)
    print(f"\nBest hook: {best_hook}")