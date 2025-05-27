import logging
from google.adk.agents import Agent
from google.adk.tools import google_search
from ...tools import enhanced_web_scraping_tool
from .prompt import NEWS_SEARCH_INSTRUCTION, NEWS_SEARCH_DESCRIPTION

logger = logging.getLogger(__name__)

# Main NewsSearchAgent following ADK patterns
root_agent = Agent(
    name="NewsSearchAgent",
    model="gemini-2.0-flash",  # Required for google_search tool
    instruction=NEWS_SEARCH_INSTRUCTION,
    description=NEWS_SEARCH_DESCRIPTION,
    tools=[google_search, enhanced_web_scraping_tool]
)

# Legacy wrapper class for backward compatibility
class NewsSearchAgent:
    """Agent responsible for searching and collecting news articles"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.agent = root_agent
    
    async def search_news(self, query: str, max_articles: int = 5) -> dict:
        """
        Search for news articles related to the given query
        
        Args:
            query: The search query for finding relevant news
            max_articles: Maximum number of articles to collect
            
        Returns:
            Dictionary containing search results and article data
        """
        try:
            logger.info(f"NewsSearchAgent searching for: {query}")
            
            # Construct a comprehensive search request
            search_request = f"""
            Find {max_articles} recent news articles about: {query}
            
            Please:
            1. Search for relevant news articles using the google_search tool
            2. Select the most credible and recent articles from the results
            3. For each article, use the enhanced_scrape_article tool to extract the full content
            4. Provide a structured summary of all collected articles
            
            Focus on established news sources and ensure articles are recent (within the last month if possible).
            """
            
            # Use the ADK agent to process the request
            response = await self.agent.run_async(search_request)
            
            # Extract the final response
            final_response = ""
            async for event in response:
                if hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts'):
                        content_parts = []
                        for part in event.content.parts:
                            if hasattr(part, 'text'):
                                content_parts.append(part.text)
                        final_response = "\n".join(content_parts)
                    else:
                        final_response = str(event.content)
            
            return {
                "success": True,
                "query": query,
                "response": final_response,
                "agent_used": "NewsSearchAgent with Google ADK tools"
            }
            
        except Exception as e:
            logger.error(f"Error in news search: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    async def search_and_scrape_articles(self, query: str, num_articles: int = 3) -> dict:
        """
        Search for articles and return structured data
        
        Args:
            query: Search query
            num_articles: Number of articles to find and scrape
            
        Returns:
            Structured data with articles and metadata
        """
        try:
            search_prompt = f"""
            Search for {num_articles} recent news articles about "{query}".
            
            For each article you find:
            1. Use google_search to find relevant news articles
            2. Use enhanced_scrape_article to extract the content from each URL
            3. Return the results in a structured format
            
            Please provide the results as a clear summary including:
            - Article titles
            - Publication sources
            - Key content summaries
            - Publication dates if available
            - Any credibility indicators you notice
            """
            
            response = await self.agent.run_async(search_prompt)
            
            # Process the response stream
            final_content = ""
            async for event in response:
                if hasattr(event, 'content') and event.content:
                    # Convert content to string if it's not already
                    if hasattr(event.content, 'parts'):
                        content_parts = []
                        for part in event.content.parts:
                            if hasattr(part, 'text'):
                                content_parts.append(part.text)
                        final_content = "\n".join(content_parts)
                    else:
                        final_content = str(event.content)
            
            return {
                "success": True,
                "query": query,
                "articles_found": final_content,
                "search_method": "Google ADK Search + Enhanced Scraping"
            }
            
        except Exception as e:
            logger.error(f"Error in search and scrape: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }

# Backward compatibility functions
async def search_news_google(query: str, api_key: str = None, max_results: int = 5) -> list:
    """
    Backward compatibility function for existing code
    """
    agent = NewsSearchAgent(api_key=api_key)
    result = await agent.search_news(query, max_articles=max_results)
    
    if result.get("success"):
        # Return in the expected format for backward compatibility
        return [{"title": f"Search Results for: {query}", "content": result.get("response", "")}]
    else:
        return [{"title": "Search Error", "content": f"Error: {result.get('error', 'Unknown error')}"}]

async def scrape_article_content(url: str) -> dict:
    """
    Backward compatibility function for scraping individual articles
    """
    from ...tools import enhanced_scrape_article
    
    try:
        result = await enhanced_scrape_article(url)
        return result
    except Exception as e:
        logger.error(f"Error scraping article {url}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "url": url
        } 