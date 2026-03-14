"""
PaperScorer module for AutoResearch Bio-Medical Pipeline
Scores papers based on novelty, clinical relevance, and other factors
"""

import re
from datetime import datetime
from typing import Dict, List
from .config import config


class PaperScorer:
    def __init__(self):
        # Keywords that indicate novelty
        self.novelty_indicators = [
            "novel", "discovery", "new", "first", "breakthrough",
            "unexpected", "surprising", "paradigm", "revolutionary",
            "innovative", "groundbreaking", "unique", "original"
        ]

        # Keywords that indicate clinical relevance
        self.clinical_indicators = [
            "clinical", "patient", "therapy", "treatment", "disease",
            "diagnosis", "biomarker", "drug", "intervention",
            "medical", "health", "pathway", "mechanism", "target"
        ]

        # Keywords that indicate counterintuitive findings
        self.counterintuitive_indicators = [
            "contrary", "opposite", "unexpected", "paradox", "challenge",
            "rethink", "reconsider", "surprising", "contradicts",
            "against", "reversal", "inconsistent", "different"
        ]

    def score_paper(self, paper: Dict) -> float:
        """
        Score a paper based on multiple factors

        Args:
            paper: Dictionary containing paper information

        Returns:
            Score between 0 and 1
        """
        # Calculate individual scores
        novelty_score = self._calculate_novelty_score(paper)
        clinical_relevance = self._calculate_clinical_relevance(paper)
        counterintuitive_factor = self._calculate_counterintuitive_score(paper)
        journal_impact = self._calculate_journal_impact(paper)
        recency = self._calculate_recency_score(paper)

        # Apply weighted formula
        total_score = (
            novelty_score * 0.35 +
            clinical_relevance * 0.25 +
            counterintuitive_factor * 0.20 +
            journal_impact * 0.10 +
            recency * 0.10
        )

        return min(1.0, max(0.0, total_score))  # Clamp between 0 and 1

    def _calculate_novelty_score(self, paper: Dict) -> float:
        """
        Calculate novelty score based on title and abstract
        """
        text = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()

        score = 0
        for indicator in self.novelty_indicators:
            if indicator in text:
                score += 0.1  # Add points for each indicator found

        # Cap at 1.0
        return min(1.0, score)

    def _calculate_clinical_relevance(self, paper: Dict) -> float:
        """
        Calculate clinical relevance score based on keywords and context
        """
        text = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()

        score = 0
        for indicator in self.clinical_indicators:
            if indicator in text:
                score += 0.1

        # Check for specific clinical context
        clinical_context_indicators = [
            "metabolism", "biochemistry", "physiology", "disease",
            "pathway", "signaling", "regulation", "homeostasis"
        ]

        for indicator in clinical_context_indicators:
            if indicator in text:
                score += 0.05

        return min(1.0, score)

    def _calculate_counterintuitive_score(self, paper: Dict) -> float:
        """
        Calculate counterintuitive score based on surprising findings
        """
        text = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()

        score = 0
        for indicator in self.counterintuitive_indicators:
            if indicator in text:
                score += 0.2  # Higher weight for counterintuitive findings

        return min(1.0, score)

    def _calculate_journal_impact(self, paper: Dict) -> float:
        """
        Calculate journal impact score based on tier
        """
        journal = paper.get('journal', '').lower()

        # Tier 1 journals (highest impact)
        tier_1 = ['nature', 'science', 'cell', 'nature metabolism', 'nature medicine', 'cell metabolism']
        if any(tier in journal for tier in tier_1):
            return 1.0

        # Tier 2 journals
        tier_2 = ['pnas', 'embo', 'jci', 'nature communications']
        if any(tier in journal for tier in tier_2):
            return 0.8

        # Tier 3 (PubMed)
        if 'pubmed' in journal or 'ncbi' in journal:
            return 0.6

        # Other journals
        return 0.5

    def _calculate_recency_score(self, paper: Dict) -> float:
        """
        Calculate recency score based on publication year
        """
        year_str = str(paper.get('year', ''))

        # Try to extract year from string
        year = None
        if year_str.isdigit():
            year = int(year_str)
        else:
            # Try to find 4-digit year in string
            import re
            match = re.search(r'(19|20)\d{2}', year_str)
            if match:
                year = int(match.group())

        if year is None:
            return 0.5  # Default medium score if no year found

        current_year = datetime.now().year
        years_since_publication = current_year - year

        # Score decreases with age, but never goes below 0.1
        if years_since_publication <= 1:
            return 1.0
        elif years_since_publication <= 3:
            return 0.8
        elif years_since_publication <= 5:
            return 0.6
        elif years_since_publication <= 10:
            return 0.4
        else:
            return 0.2

    def score_papers(self, papers: List[Dict]) -> List[Dict]:
        """
        Score multiple papers and add the score to each paper dictionary

        Args:
            papers: List of papers to score

        Returns:
            List of papers with scores added to each paper dictionary
        """
        scored_papers = []
        for paper in papers:
            score = self.score_paper(paper)
            paper_copy = paper.copy()  # Create a copy to avoid modifying original
            paper_copy['score'] = score
            scored_papers.append(paper_copy)

        return scored_papers

    def filter_papers_by_score(self, papers: List[Dict]) -> List[Dict]:
        """
        Filter papers to only include those with scores above the threshold

        Args:
            papers: List of papers to filter

        Returns:
            List of papers with scores above MIN_PAPER_SCORE
        """
        filtered_papers = []
        for paper in papers:
            # If paper doesn't have a score yet, calculate it
            if 'score' not in paper:
                paper['score'] = self.score_paper(paper)
            if paper['score'] >= config.MIN_PAPER_SCORE:
                filtered_papers.append(paper)

        return filtered_papers


# Example usage:
if __name__ == "__main__":
    scorer = PaperScorer()

    # Example paper
    example_paper = {
        'title': 'Unexpected mechanism of insulin resistance in mitochondrial dysfunction',
        'authors': ['Smith, J.', 'Doe, A.'],
        'journal': 'Nature Metabolism',
        'year': 2024,
        'url': 'https://nature.com/example',
        'abstract': 'Our novel discovery challenges the traditional understanding of insulin resistance. We found that the mechanism begins in mitochondria rather than fat cells, which is contrary to current paradigms.'
    }

    score = scorer.score_paper(example_paper)
    print(f"Paper score: {score:.2f}")

    # Example papers to filter
    papers = [
        {
            'title': 'Incremental improvement in glucose measurement',
            'journal': 'Lab Tech Journal',
            'year': 2020,
            'abstract': 'We made a small improvement to our glucose measurement technique.'
        },
        example_paper
    ]

    filtered = scorer.filter_papers_by_score(papers)
    print(f"Filtered {len(papers)} papers down to {len(filtered)} based on score threshold.")