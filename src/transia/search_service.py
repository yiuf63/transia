"""Book context search service powered by DuckDuckGo."""

from duckduckgo_search import DDGS
from .standalone_utils import logger, trim

class SearchService:
    def __init__(self, max_results=3):
        self.max_results = max_results

    def search_book(self, title, author=""):
        """Searches for book background information and returns a summary."""
        query = f"book '{title}' {author} summary background"
        logger.info(f"Searching internet for: {query}")
        
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=self.max_results))
                
            if not results:
                return ""
            
            # Combine bodies into a clean summary
            snippets = []
            for r in results:
                body = r.get("body", "")
                if body:
                    snippets.append(trim(body))
            
            summary = " ".join(snippets)
            # Limit length to avoid blowing up the prompt
            if len(summary) > 1000:
                summary = summary[:1000] + "..."
                
            return summary
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return ""
