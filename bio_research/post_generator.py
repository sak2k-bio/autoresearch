"""
PostGenerator module for AutoResearch Bio-Medical Pipeline
Generates viral LinkedIn posts from scientific paper insights
"""

import os
from typing import Dict, List
from .config import config

import warnings

# Handle both old and new Google GenAI libraries without triggering warnings
def get_genai_client():
    """Get the appropriate GenAI client, prioritizing the newer version"""
    try:
        import google.genai as genai_client
        return genai_client, True
    except ImportError:
        try:
            # Suppress the deprecation warning when importing the old library
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", FutureWarning)
                import google.generativeai as genai_client
            return genai_client, False  # Indicates old library
        except ImportError:
            raise ImportError("Either google-genai or google-generativeai package is required")

genai, is_new_library = get_genai_client()

class PostGenerator:
    def __init__(self):
        # Use the configured Gemini model
        self.model_name = config.gemini_model
        self.gemini_calls = 0
        
        # Initialize Gemini API with the first available key
        if config.gemini_api_keys:
            genai.configure(api_key=config.gemini_api_keys[0])
        else:
            raise ValueError("No Gemini API keys found in environment variables")
    
    def generate_post(self, paper_data: Dict, insights: Dict, simplified_mechanism: Dict, best_hook: str) -> Dict:
        """
        Generate a viral LinkedIn post from paper data and insights
        
        Args:
            paper_data: Dictionary containing paper information
            insights: Extracted insights from the paper
            simplified_mechanism: Simplified mechanism data
            best_hook: Selected best hook for the post
            
        Returns:
            Dictionary containing the generated post and metadata
        """
        # Prepare the prompt for the Gemini model
        prompt = f"""
        Transform the following scientific paper into a viral LinkedIn post that performs well in the bio-medical niche.
        
        PAPER INFORMATION:
        Title: {paper_data.get('title', 'N/A')}
        Authors: {paper_data.get('authors', 'N/A')}
        Journal: {paper_data.get('journal', 'N/A')} ({paper_data.get('year', 'N/A')})
        
        KEY INSIGHTS:
        Main Discovery: {insights.get('key_discovery', 'N/A')}
        Biochemical Mechanism: {insights.get('biochemical_mechanism', 'N/A')}
        Clinical Significance: {insights.get('clinical_significance', 'N/A')}
        Surprising Element: {insights.get('surprising_insight', 'N/A')}
        Mechanistic Chain: {insights.get('mechanistic_chain', 'N/A')}
        
        SIMPLIFIED MECHANISM:
        Simple Mechanism: {simplified_mechanism.get('simple_mechanism', 'N/A')}
        Simple Chain: {simplified_mechanism.get('simple_chain', 'N/A')}
        Visual Sequence: {simplified_mechanism.get('visualizable_sequence', 'N/A')}
        Analogy: {simplified_mechanism.get('analogy', 'N/A')}
        
        HOOK:
        {best_hook}
        
        GENERATE A LINKEDIN POST WITH THE FOLLOWING STRUCTURE:
        1. HOOK: Start with the provided hook
        2. SETUP: Explain what scientists previously believed
        3. DISCOVERY: Describe the new finding
        4. MECHANISM: Explain the biochemical pathway in simple terms
        5. IMPLICATION: State why this matters for health/metabolism/physiology
        6. QUESTION: End with a thought-provoking question
        
        REQUIREMENTS:
        - Make it engaging and easy to read (~120-200 words)
        - Maintain scientific accuracy
        - Avoid heavy jargon
        - Make complex biochemistry intuitive
        - Use the hook at the beginning
        - Include a compelling narrative arc
        
        FORMAT THE RESPONSE AS:
        LinkedIn Post:
        [Your generated post here]
        
        Hashtags:
        #[relevant hashtag] #[another hashtag] #[science hashtag] #[research hashtag] #[medical hashtag]
        """
        
        # Try each available API key until one works
        for i, api_key in enumerate(config.gemini_api_keys):
            try:
                # Configure with current key
                genai.configure(api_key=api_key)
                
                # Initialize the model
                model = genai.GenerativeModel(self.model_name)
                
                # Generate content
                self.gemini_calls += 1
                response = model.generate_content(prompt)
                
                # Parse the response
                post_text = response.text
                
                # Extract post and hashtags
                if "LinkedIn Post:" in post_text and "Hashtags:" in post_text:
                    post_part = post_text.split("LinkedIn Post:")[1].split("Hashtags:")[0].strip()
                    hashtags_part = post_text.split("Hashtags:")[1].strip()
                    
                    # Clean up hashtags
                    hashtags = [tag.strip().replace('#', '') for tag in hashtags_part.split() if tag.startswith('#')]
                    
                    return {
                        'original_post': post_part,
                        'hashtags': hashtags[:5],  # Limit to 5 hashtags
                        'generated_by_model': self.model_name
                    }
                else:
                    # If format not found, return the raw response as post
                    return {
                        'original_post': post_text,
                        'hashtags': [],
                        'generated_by_model': self.model_name
                    }
                    
            except Exception as e:
                print(f"Gemini API key {i+1} failed: {str(e)}")
                if i == len(config.gemini_api_keys) - 1:  # Last key
                    raise Exception(f"All Gemini API keys failed. Last error: {str(e)}")
                else:
                    continue  # Try next key
    
    def score_curiosity(self, post_data: Dict) -> Dict:
        """
        Score the curiosity aspects of the generated post
        
        Args:
            post_data: Dictionary containing the generated post
            
        Returns:
            Dictionary with curiosity scores for different aspects
        """
        post_content = post_data['original_post']
        
        scoring_prompt = f"""
        Score the following LinkedIn post on these curiosity dimensions (0-10 scale for each):
        
        1. Curiosity: How intriguing and attention-grabbing is the content?
        2. Clarity: How well does it explain complex concepts simply?
        3. Novelty: How surprising or novel is the information?
        4. Memorability: How likely is the reader to remember this information?
        5. Shareability: How likely is someone to share this post?
        
        POST CONTENT:
        {post_content}
        
        Respond in this exact JSON format:
        {{
            "curiosity": 0,
            "clarity": 0,
            "novelty": 0,
            "memorability": 0,
            "shareability": 0
        }}
        
        Just return the JSON object with scores, nothing else.
        """
        
        # Try each available API key until one works
        for i, api_key in enumerate(config.gemini_api_keys):
            try:
                # Configure with current key
                genai.configure(api_key=api_key)
                
                # Initialize the model
                model = genai.GenerativeModel(self.model_name)
                
                # Generate content
                self.gemini_calls += 1
                response = model.generate_content(scoring_prompt)
                
                # Parse the response
                import json
                scores = json.loads(response.text.strip())
                
                return scores
                    
            except Exception as e:
                print(f"Gemini API key {i+1} failed for scoring: {str(e)}")
                if i == len(config.gemini_api_keys) - 1:  # Last key
                    raise Exception(f"All Gemini API keys failed for scoring. Last error: {str(e)}")
                else:
                    continue  # Try next key
    
    def get_total_curiosity_score(self, curiosity_scores: Dict) -> float:
        """
        Calculate the total curiosity score from individual scores
        
        Args:
            curiosity_scores: Dictionary with individual curiosity scores
            
        Returns:
            Total curiosity score (0-50)
        """
        return (
            curiosity_scores.get('curiosity', 0) +
            curiosity_scores.get('clarity', 0) +
            curiosity_scores.get('novelty', 0) +
            curiosity_scores.get('memorability', 0) +
            curiosity_scores.get('shareability', 0)
        )
