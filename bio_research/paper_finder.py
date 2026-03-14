"""
PaperFinder module for AutoResearch Bio-Medical Pipeline
Uses Tavily API to search for papers in specified categories
"""

import asyncio
import aiohttp
import time
from typing import List, Dict, Optional
from tavily import TavilyClient
from .config import config


class PaperFinder:
    def __init__(self):
        if not config.tavily_api_key:
            raise ValueError("TAVILY_API_KEY environment variable is required")

        self.client = TavilyClient(api_key=config.tavily_api_key)
        self.search_count = 0
        self.last_search_time = 0
        self.rate_limit_delay = 1  # seconds between requests
        self.tavily_calls = 0

    def _rate_limit_check(self):
        """Check and enforce rate limiting"""
        current_time = time.time()
        if current_time - self.last_search_time < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - (current_time - self.last_search_time))
        self.last_search_time = time.time()
        self.search_count += 1

    def search_papers(self, keywords: List[str]) -> List[Dict]:
        """
        Search for papers using Tavily API

        Args:
            keywords: List of keywords to search for

        Returns:
            List of papers found
        """
        all_papers = []

        for keyword in keywords:
            self._rate_limit_check()

            try:
                # Search for papers using the keyword
                self.tavily_calls += 1
                response = self.client.search(
                    query=f"{keyword} scientific paper research",
                    search_depth="advanced",  # Use advanced search for better results
                    max_results=10,
                    include_domains=[
                        "nature.com", "science.org", "cell.com",
                        "pnas.org", "embopress.org", "jci.org",
                        "pubmed.ncbi.nlm.nih.gov", "ncbi.nlm.nih.gov"
                    ],
                    exclude_domains=[],
                    include_answer=False,
                    include_images=False,
                    include_raw_content=False
                )

                # Process results
                for result in response.get('results', []):
                    paper_data = self._parse_result(result)
                    if paper_data:
                        all_papers.append(paper_data)

            except Exception as e:
                print(f"Error searching for '{keyword}': {str(e)}")
                continue

        return all_papers

    async def search_papers_async(self, keywords: List[str]) -> List[Dict]:
        """
        Async version of search_papers for better performance

        Args:
            keywords: List of keywords to search for

        Returns:
            List of papers found
        """
        all_papers = []

        for keyword in keywords:
            self._rate_limit_check()

            try:
                # Search for papers using the keyword
                self.tavily_calls += 1
                response = self.client.search(
                    query=f"{keyword} scientific paper research",
                    search_depth="advanced",
                    max_results=10,
                    include_domains=[
                        "nature.com", "science.org", "cell.com",
                        "pnas.org", "embopress.org", "jci.org",
                        "pubmed.ncbi.nlm.nih.gov", "ncbi.nlm.nih.gov"
                    ],
                    exclude_domains=[],
                    include_answer=False,
                    include_images=False,
                    include_raw_content=False
                )

                # Process results
                for result in response.get('results', []):
                    paper_data = self._parse_result(result)
                    if paper_data:
                        all_papers.append(paper_data)

            except Exception as e:
                print(f"Error searching for '{keyword}': {str(e)}")
                continue

        return all_papers

    def _parse_result(self, result: Dict) -> Optional[Dict]:
        """
        Parse a search result into paper format

        Args:
            result: Raw search result

        Returns:
            Parsed paper data or None if invalid
        """
        try:
            # Extract title
            title = result.get('title', '')

            # Extract URL
            url = result.get('url', '')

            # Extract content snippet
            content = result.get('content', '')

            # Attempt to extract authors and journal info from content or URL
            authors = self._extract_authors(content)
            journal = self._extract_journal(url)
            year = self._extract_year(content, url)

            # Create paper object
            paper = {
                'title': title,
                'authors': authors,
                'journal': journal,
                'year': year,
                'url': url,
                'abstract': content,
                'relevance_score': result.get('score', 0.0)
            }

            return paper

        except Exception as e:
            print(f"Error parsing result: {str(e)}")
            return None

    def _extract_authors(self, content: str) -> List[str]:
        """
        Extract author information from content (basic implementation)

        Args:
            content: Content string to extract from

        Returns:
            List of author names
        """
        # This is a simplified implementation
        # In a real implementation, you'd use more sophisticated NLP
        return ["Author Name"]  # Placeholder

    def _extract_journal(self, url: str) -> str:
        """
        Extract journal name from URL

        Args:
            url: URL of the paper

        Returns:
            Journal name
        """
        # Extract journal from URL
        if "nature.com" in url:
            if "nature-metabolism" in url or "metabolism" in url:
                return "Nature Metabolism"
            elif "nature-medicine" in url:
                return "Nature Medicine"
            else:
                return "Nature"
        elif "science.org" in url:
            return "Science"
        elif "cell.com" in url:
            if "cell metabolism" in url.lower():
                return "Cell Metabolism"
            else:
                return "Cell"
        elif "pnas.org" in url:
            return "PNAS"
        elif "embopress.org" in url:
            return "EMBO"
        elif "jci.org" in url:
            return "JCI"
        elif "pubmed.ncbi.nlm.nih.gov" in url or "ncbi.nlm.nih.gov" in url:
            return "PubMed"
        else:
            return "Unknown Journal"

    def _extract_year(self, content: str, url: str) -> Optional[int]:
        """
        Extract publication year from content or URL

        Args:
            content: Content string
            url: URL of the paper

        Returns:
            Publication year or None
        """
        import re

        # Try to find year in URL first (most reliable)
        year_match = re.search(r'(19|20)\d{2}', url)
        if year_match:
            return int(year_match.group())

        # Try to find year in content
        year_match = re.search(r'\b(19|20)\d{2}\b', content)
        if year_match:
            return int(year_match.group())

        return None


# Example usage:
if __name__ == "__main__":
    finder = PaperFinder()

    # Example keywords
    keywords = [
        "mechanism of metabolism carbohydrates lipids proteins",
        "novel pathway metabolic disease",
        "metabolic regulation human physiology"
    ]

    papers = finder.search_papers(keywords)
    print(f"Found {len(papers)} papers")

    for i, paper in enumerate(papers[:3]):  # Show first 3 papers
        print(f"\nPaper {i+1}: {paper['title']}")
        print(f"Authors: {', '.join(paper['authors'])}")
        print(f"Journal: {paper['journal']} ({paper['year']})")
        print(f"URL: {paper['url']}")
