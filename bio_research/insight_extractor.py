"""
InsightExtractor module for AutoResearch Bio-Medical Pipeline
Extracts key insights from scientific papers
"""

import re
from typing import Dict, List, Optional
from .config import config


class InsightExtractor:
    def __init__(self):
        self.key_discovery_patterns = [
            r"(?:discovered|found|identified|revealed|showed|demonstrated).*?(?:that|how|which)",
            r"(?:novel|new|first).*?(?:mechanism|pathway|finding|discovery)",
            r"(?:contrary to|unlike|different from).*?expectations?",
            r"(?:surprisingly|unexpectedly|in contrast).*?",
        ]

        self.mechanism_patterns = [
            r"(?:mechanism|pathway|process|system).*?(?:involves|includes|consists|mediated)",
            r"(?:via|through|by means of).*?(?:pathway|mechanism|process)",
            r"(?:activation|inhibition|regulation) of.*?(?:pathway|protein|process)",
        ]

        self.clinical_relevance_patterns = [
            r"(?:clinical|therapeutic|medical|treatment|disease|patient).*?(?:implication|significance|relevance)",
            r"(?:could lead to|may result in|suggests|indicates).*?(?:therapy|treatment|approach)",
            r"(?:potential|possible|promising).*?(?:application|use|benefit)",
        ]

        self.surprising_insight_patterns = [
            r"(?:contrary to|challenges|refutes|contradicts).*?(?:current|existing|traditional|established).*?(?:theory|understanding|belief|model)",
            r"(?:surprisingly|unexpectedly|remarkably).*?(?:found|discovered|observed)",
            r"(?:rethink|reconsider|redefine).*?(?:our|the current|existing).*?(?:understanding|concept|model)",
        ]

    def extract_insights(self, paper: Dict) -> Dict:
        """
        Extract key insights from a paper

        Args:
            paper: Dictionary containing paper information

        Returns:
            Dictionary with extracted insights
        """
        abstract = paper.get('abstract', '')
        title = paper.get('title', '')

        # Combine title and abstract for better extraction
        full_text = f"{title}. {abstract}"

        insights = {
            'key_discovery': self._extract_key_discovery(full_text),
            'biochemical_mechanism': self._extract_mechanism(full_text),
            'clinical_significance': self._extract_clinical_significance(full_text),
            'surprising_insight': self._extract_surprising_insight(full_text),
            'mechanistic_chain': self._extract_mechanistic_chain(full_text)
        }

        return insights

    def _extract_key_discovery(self, text: str) -> str:
        """
        Extract the key discovery from the text
        """
        for pattern in self.key_discovery_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Get the sentence containing the match
                sentences = text.split('.')
                for sentence in sentences:
                    if match.group(0).lower() in sentence.lower():
                        return sentence.strip()

        # If no pattern matches, return the first sentence that seems like a discovery
        sentences = text.split('.')
        for sentence in sentences[:3]:  # Check first 3 sentences
            if any(word in sentence.lower() for word in ['discovered', 'found', 'showed', 'revealed']):
                return sentence.strip()

        # If still no discovery found, return the first substantial sentence
        for sentence in sentences:
            if len(sentence.strip()) > 20:  # At least 20 characters
                return sentence.strip()

        return text[:200] + "..." if len(text) > 200 else text

    def _extract_mechanism(self, text: str) -> str:
        """
        Extract the biochemical mechanism from the text
        """
        for pattern in self.mechanism_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Get the sentence containing the match
                sentences = text.split('.')
                for sentence in sentences:
                    if match.group(0).lower() in sentence.lower():
                        return sentence.strip()

        # If no pattern matches, look for sentences with mechanism-related words
        sentences = text.split('.')
        for sentence in sentences:
            if any(word in sentence.lower() for word in ['pathway', 'mechanism', 'process', 'via', 'through', 'by']):
                return sentence.strip()

        return ""

    def _extract_clinical_significance(self, text: str) -> str:
        """
        Extract the clinical significance from the text
        """
        for pattern in self.clinical_relevance_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Get the sentence containing the match
                sentences = text.split('.')
                for sentence in sentences:
                    if match.group(0).lower() in sentence.lower():
                        return sentence.strip()

        # If no pattern matches, look for sentences with clinical words
        sentences = text.split('.')
        for sentence in sentences:
            if any(word in sentence.lower() for word in ['clinical', 'therapy', 'treatment', 'disease', 'patient', 'significant']):
                return sentence.strip()

        return ""

    def _extract_surprising_insight(self, text: str) -> str:
        """
        Extract the surprising or counterintuitive insight from the text
        """
        for pattern in self.surprising_insight_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Get the sentence containing the match
                sentences = text.split('.')
                for sentence in sentences:
                    if match.group(0).lower() in sentence.lower():
                        return sentence.strip()

        # If no pattern matches, look for sentences with surprising words
        sentences = text.split('.')
        for sentence in sentences:
            if any(word in sentence.lower() for word in ['surprisingly', 'unexpectedly', 'contrary', 'challenges', 'rethink']):
                return sentence.strip()

        return ""

    def _extract_mechanistic_chain(self, text: str) -> str:
        """
        Extract the mechanistic chain (cause-and-effect sequence)
        """
        # Look for patterns that suggest a sequence of events
        sequence_patterns = [
            r"(\w+)\s*(?:leads to|results in|causes|triggers)\s*(\w+)(?:\s*(?:leads to|results in|causes|triggers)\s*(\w+))*",
            r"(\w+)\s*→\s*(\w+)(?:\s*→\s*(\w+))*",
            r"first\s*(\w+),\s*then\s*(\w+)(?:,\s*then\s*(\w+))*",
        ]

        for pattern in sequence_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Format as a chain
                chain_parts = []
                for match in matches:
                    parts = [part for part in match if part]
                    if len(parts) > 1:
                        chain = " → ".join(parts)
                        chain_parts.append(chain)

                if chain_parts:
                    return "; ".join(chain_parts)

        # Alternative: Look for sentences that describe a process
        sentences = text.split('.')
        for sentence in sentences:
            if any(word in sentence.lower() for word in ['process', 'sequence', 'pathway', 'cascade', 'chain']):
                # Try to identify cause and effect relationships
                causes_effects = re.findall(r"(\w+)\s*(?:leads to|results in|causes|triggers|activates|inhibits)\s*(\w+)", sentence, re.IGNORECASE)
                if len(causes_effects) >= 2:
                    chain_elements = []
                    for cause, effect in causes_effects:
                        if not chain_elements:
                            chain_elements.extend([cause, effect])
                        elif chain_elements[-1] == cause:
                            chain_elements.append(effect)
                        else:
                            chain_elements.extend([cause, effect])

                    if len(chain_elements) >= 3:
                        return " → ".join(chain_elements)

        return ""


# Example usage:
if __name__ == "__main__":
    extractor = InsightExtractor()

    # Example paper text
    example_text = """
    Our novel discovery reveals that insulin resistance may begin in mitochondria rather than fat cells,
    which challenges the traditional understanding. We found that nutrient excess leads to mitochondrial
    overload, which increases reactive oxygen species (ROS) production. This oxidative stress subsequently
    inhibits insulin signaling pathways, ultimately resulting in metabolic dysfunction. This mechanism
    suggests that therapeutic interventions targeting mitochondrial function could be more effective than
    traditional approaches focusing solely on glucose management. Surprisingly, our results contradict
    decades of research emphasizing fat tissue as the primary driver of insulin resistance.
    """

    example_paper = {
        'title': 'Mitochondrial origins of insulin resistance',
        'abstract': example_text
    }

    insights = extractor.extract_insights(example_paper)

    print("Key Discovery:", insights['key_discovery'])
    print("\nBiochemical Mechanism:", insights['biochemical_mechanism'])
    print("\nClinical Significance:", insights['clinical_significance'])
    print("\nSurprising Insight:", insights['surprising_insight'])
    print("\nMechanistic Chain:", insights['mechanistic_chain'])