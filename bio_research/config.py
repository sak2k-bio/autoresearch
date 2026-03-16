"""
Configuration module for AutoResearch Bio-Medical Pipeline
"""

import os
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class BioConfig:
    # API Keys
    tavily_api_key: str = os.getenv('TAVILY_API_KEY', '')
    
    # Gemini API keys (primary + backups)
    gemini_api_keys: List[str] = None
    
    # Gemini model to use
    gemini_model: str = os.getenv('GEMINI_MODEL', 'gemini-1.5-pro')
    
    # Paper scoring thresholds
    MIN_PAPER_SCORE: float = 0.4  # Papers must score above this to proceed
    
    # Post generation thresholds
    MIN_CURIOSITY_SCORE: int = 35  # Posts must score at least this high

    # Outcome learning threshold (0-1 scale)
    MIN_OUTCOME_SCORE: float = 0.5
    
    # Generation settings
    NUM_HOOKS_TO_GENERATE: int = 10  # Number of hooks to generate per paper
    
    # Topic categories for keyword generation
    TOPIC_CATEGORIES: List[str] = None
    
    # Keyword patterns for research
    KEYWORD_PATTERNS: List[str] = None
    
    # Journal tier priorities
    JOURNAL_TIERS: Dict[str, List[str]] = None
    
    # Hashtag recommendations for LinkedIn posts
    HASHTAGS: List[str] = None

    def __post_init__(self):
        # Initialize Gemini API keys
        if self.gemini_api_keys is None:
            self.gemini_api_keys = []
            for i in range(1, 6):  # Check for up to 5 keys
                key = os.getenv(f'GEMINI_API_KEY_{i}')
                if key:
                    self.gemini_api_keys.append(key)
        
        # Initialize topic categories
        if self.TOPIC_CATEGORIES is None:
            self.TOPIC_CATEGORIES = [
                'clinical biochemistry',
                'metabolism',
                'metabolic disease',
                'human physiology',
                'biotechnology',
                'health science insights',
                'emerging biomedical discoveries'
            ]
        
        # Initialize keyword patterns
        if self.KEYWORD_PATTERNS is None:
            self.KEYWORD_PATTERNS = [
                'mechanism of',
                'novel pathway',
                'metabolic regulation',
                'biochemical signaling',
                'new biomarker',
                'unexpected mechanism',
                'recent discovery',
                'clinical relevance',
                'therapeutic target',
                'molecular mechanism'
            ]
        
        # Initialize journal tiers
        if self.JOURNAL_TIERS is None:
            self.JOURNAL_TIERS = {
                'tier_1': [
                    'Nature', 'Science', 'Cell', 'Nature Metabolism', 
                    'Nature Medicine', 'Cell Metabolism'
                ],
                'tier_2': [
                    'PNAS', 'EMBO', 'JCI', 'Nature Communications',
                    'Science Translational Medicine', 'Cell Reports'
                ],
                'tier_3': [
                    'PubMed high-impact discoveries'
                ]
            }
        
        # Initialize hashtags
        if self.HASHTAGS is None:
            self.HASHTAGS = [
                'Biotech', 'Science', 'Research', 'Innovation', 'HealthTech',
                'MedicalBreakthrough', 'Biochemistry', 'Metabolism', 'Health',
                'Technology', 'Discovery', 'ClinicalResearch', 'Biomedical',
                'Healthcare', 'Medicine', 'ScienceCommunication', 'BioTech',
                'HealthInnovation', 'MedicalResearch', 'LifeSciences'
            ]

# Global config instance
config = BioConfig()
