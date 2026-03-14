"""
Optimizer module for AutoResearch Bio-Medical Pipeline
Handles SEO optimization, hashtag addition, and curiosity amplification
"""

from typing import Dict, List
from .config import config


class Optimizer:
    def __init__(self):
        self.hashtags = config.HASHTAGS

    def optimize_post(self, post: str, scores: Dict[str, float], paper_data: Dict) -> Dict[str, str]:
        """
        Optimize the post for SEO and engagement

        Args:
            post: The generated LinkedIn post
            scores: Dictionary of curiosity scores
            paper_data: Dictionary containing paper information

        Returns:
            Dictionary with optimized post, hashtags, and metadata
        """
        optimized_post = self._format_for_readability(post)
        hashtags = self._generate_hashtags(paper_data, post)

        result = {
            'optimized_post': optimized_post,
            'hashtags': hashtags,
            'curiosity_score': scores,
            'total_curiosity_score': sum(scores.values()),
            'needs_regeneration': sum(scores.values()) < config.MIN_CURIOSITY_SCORE
        }

        return result

    def _format_for_readability(self, post: str) -> str:
        """
        Format the post for better readability on LinkedIn
        """
        # Ensure proper paragraph breaks
        paragraphs = post.split('\n\n')

        # Add spacing for better readability
        formatted_paragraphs = []
        for para in paragraphs:
            if para.strip():  # Only add non-empty paragraphs
                formatted_paragraphs.append(para.strip())

        formatted_post = '\n\n'.join(formatted_paragraphs)

        # Add bullet points or line breaks for longer sections
        sentences = formatted_post.split('. ')
        if len(sentences) > 4:  # If there are multiple sentences
            # Join with proper spacing
            formatted_post = '.\n\n'.join(sentences)
            # Clean up any double periods
            formatted_post = formatted_post.replace('.\n\n.', '.\n\n')

        return formatted_post.strip()

    def _generate_hashtags(self, paper_data: Dict, post: str) -> List[str]:
        """
        Generate relevant hashtags based on paper content and topic
        """
        # Extract keywords from the paper title and content
        title = paper_data.get('title', '').lower()
        content = post.lower()

        # Determine relevant hashtags based on content
        relevant_tags = []

        # Topic-based hashtags
        if any(term in title or term in content for term in ['metabolism', 'glucose', 'insulin', 'diabetes']):
            relevant_tags.extend(['#Metabolism', '#Diabetes', '#Glucose'])

        if any(term in title or term in content for term in ['biochemistry', 'biochemical', 'enzyme', 'pathway']):
            relevant_tags.extend(['#Biochemistry', '#ClinicalBiochemistry'])

        if any(term in title or term in content for term in ['physiology', 'physiological', 'organ', 'tissue']):
            relevant_tags.extend(['#Physiology', '#HumanPhysiology'])

        if any(term in title or term in content for term in ['biotech', 'biotechnology', 'therapeutic', 'treatment']):
            relevant_tags.extend(['#Biotech', '#Biotechnology'])

        if any(term in title or term in content for term in ['disease', 'medical', 'clinic', 'health']):
            relevant_tags.extend(['#MedicalScience', '#HealthScience'])

        # Add general science tags
        relevant_tags.extend(['#Science', '#Research'])

        # Remove duplicates while preserving order
        unique_tags = []
        for tag in relevant_tags:
            if tag not in unique_tags:
                unique_tags.append(tag)

        # Limit to 5 hashtags maximum
        return unique_tags[:5]

    def regenerate_if_needed(self, post_data: Dict, generator, paper_data: Dict, insights: Dict, simplified_mechanism: Dict, best_hook: str) -> Dict[str, str]:
        """
        Regenerate the post if the curiosity score is below the threshold

        Args:
            post_data: Dictionary containing the current post and scores
            generator: PostGenerator instance to regenerate the post
            paper_data: Dictionary containing paper information
            insights: Dictionary containing extracted insights
            simplified_mechanism: Dictionary containing simplified mechanisms
            best_hook: The selected best hook for the post

        Returns:
            Dictionary with optimized post, hashtags, and metadata
        """
        if not post_data['needs_regeneration']:
            return post_data

        print(f"Regenerating post - Current score: {post_data['total_curiosity_score']}/{config.MIN_CURIOSITY_SCORE}")

        # Regenerate the post
        regenerated_post = generator.generate_post(paper_data, insights, simplified_mechanism, best_hook)

        # Rescore the regenerated post
        new_scores = generator.score_curiosity(regenerated_post)
        total_score = generator.get_total_curiosity_score(new_scores)

        # Optimize the regenerated post
        optimized = self.optimize_post(regenerated_post['original_post'], new_scores, paper_data)

        print(f"Regenerated post score: {optimized['total_curiosity_score']}/{config.MIN_CURIOSITY_SCORE}")

        return optimized


# Example usage:
if __name__ == "__main__":
    optimizer = Optimizer()

    # Example post and scores
    example_post = """Scientists just discovered something surprising about insulin resistance.

Most people think insulin resistance is caused by fat. But a new study suggests the real trigger may start inside mitochondria.

The research shows that nutrient excess leads to mitochondrial overload, which increases ROS production. This oxidative stress subsequently inhibits insulin signaling, leading to metabolic dysfunction.

This changes how we think about diabetes prevention."""

    example_scores = {
        'curiosity': 8.0,
        'clarity': 7.5,
        'novelty': 8.5,
        'memorability': 7.0,
        'shareability': 8.0
    }

    example_paper = {
        'title': 'Mitochondrial dysfunction initiates insulin resistance through oxidative stress',
        'journal': 'Nature Metabolism'
    }

    optimized_result = optimizer.optimize_post(example_post, example_scores, example_paper)

    print("Optimized Post:")
    print(optimized_result['optimized_post'])
    print(f"\nHashtags: {' '.join(optimized_result['hashtags'])}")
    print(f"Total Curiosity Score: {optimized_result['total_curiosity_score']}/50")
    print(f"Needs Regeneration: {optimized_result['needs_regeneration']}")
