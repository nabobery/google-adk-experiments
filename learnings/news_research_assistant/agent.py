import logging
from typing import Dict, Any, List
import asyncio
import html  # Import the html module

from google.adk.agents import Agent
from .prompt import MAIN_COORDINATOR_INSTRUCTION, MAIN_COORDINATOR_DESCRIPTION

# Import sub-agents from their new structure
from .sub_agents.news_search_agent.agent import NewsSearchAgent
from .sub_agents.content_summarizer_agent.agent import ContentSummarizerAgent
from .sub_agents.fact_checker_agent.agent import FactCheckerAgent
from .sub_agents.news_search_agent.agent import root_agent as news_search_agent
from .sub_agents.content_summarizer_agent.agent import root_agent as content_summarizer_agent
from .sub_agents.fact_checker_agent.agent import root_agent as fact_checker_agent

logger = logging.getLogger(__name__)

# Main News Research Assistant Agent following ADK patterns
root_agent = Agent(
    name="NewsResearchCoordinator",
    model="gemini-2.5-flash-preview-05-20",
    instruction=MAIN_COORDINATOR_INSTRUCTION,
    description=MAIN_COORDINATOR_DESCRIPTION,
    # global_instruction=MAIN_COORDINATOR_INSTRUCTION,
    tools=[],  # No direct tools - coordinates through sub-agents
    sub_agents=[news_search_agent, content_summarizer_agent, fact_checker_agent]
)

# Legacy wrapper class for complex operations and backward compatibility
class NewsResearchAssistant:
    """
    Main News Research Assistant using Google ADK with proper agent coordination
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.main_agent = root_agent
        
        # Initialize sub-agents
        self.news_search_agent = NewsSearchAgent(api_key=api_key)
        self.content_summarizer_agent = ContentSummarizerAgent(api_key=api_key)
        self.fact_checker_agent = FactCheckerAgent(api_key=api_key)
    
    async def research_topic(self, query: str, max_articles: int = 5, analysis_depth: str = "comprehensive") -> Dict[str, Any]:
        """
        Conduct comprehensive research on a given topic
        
        Args:
            query: The topic or question to research
            max_articles: Maximum number of articles to analyze
            analysis_depth: Level of analysis ('basic', 'detailed', 'comprehensive')
            
        Returns:
            Dictionary containing research results and analysis
        """
        try:
            logger.info(f"NewsResearchAssistant researching: {query}")
            
            # Step 1: Search for relevant articles
            logger.info("Step 1: Searching for relevant articles...")
            search_results = await self.news_search_agent.search_and_scrape_articles(
                query=query, 
                num_articles=max_articles
            )
            
            if not search_results.get("success"):
                return {
                    "success": False,
                    "error": f"Search failed: {search_results.get('error', 'Unknown error')}",
                    "query": query
                }
            
            # Step 2: Analyze and summarize the content
            logger.info("Step 2: Analyzing and summarizing content...")
            
            # Convert search results to articles format for summarizer
            articles_for_analysis = [{
                "title": f"Research Results for: {query}",
                "content": search_results.get("articles_found", ""),
                "source": "Multiple Sources via Google Search"
            }]
            
            summary_results = await self.content_summarizer_agent.summarize_multiple_articles(articles_for_analysis)
            
            if not summary_results.get("success"):
                return {
                    "success": False,
                    "error": f"Analysis failed: {summary_results.get('error', 'Unknown error')}",
                    "query": query
                }
            
            # Step 3: Generate comprehensive research report
            logger.info("Step 3: Generating comprehensive research report...")
            
            research_prompt = f"""
            Based on the following research conducted on "{query}", please provide a comprehensive research summary:
            
            **Search Results:**
            {search_results.get('articles_found', 'No articles found')}
            
            **Analysis Results:**
            {summary_results.get('summary', 'No analysis available')}
            
            Please structure your response as a comprehensive research report including:
            1. Executive Summary
            2. Key Findings
            3. Source Analysis and Credibility Assessment
            4. Different Perspectives and Viewpoints
            5. Recommendations for Decision Making
            6. Areas for Further Research
            
            Focus on providing actionable insights and highlighting any important considerations for the user.
            """
            
            final_report_response = await self.main_agent.run_async(research_prompt)
            
            # Extract the final report
            final_report = ""
            async for event in final_report_response:
                if hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts'):
                        content_parts = []
                        for part in event.content.parts:
                            if hasattr(part, 'text'):
                                content_parts.append(part.text)
                        final_report = "\n".join(content_parts)
                    else:
                        final_report = str(event.content)
            
            return {
                "success": True,
                "query": query,
                "research_report": final_report,
                "search_results": search_results,
                "analysis_results": summary_results,
                "methodology": {
                    "search_agent": "NewsSearchAgent with Google ADK Search",
                    "analysis_agent": "ContentSummarizerAgent with Advanced Analysis",
                    "coordination": "NewsResearchCoordinator",
                    "articles_analyzed": max_articles,
                    "analysis_depth": analysis_depth
                },
                "metadata": {
                    "total_agents_used": 3,
                    "primary_tools": ["google_search", "enhanced_web_scraping", "advanced_content_analysis"],
                    "model_used": "gemini-2.5-flash-preview-05-20"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in research_topic: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    async def quick_search(self, query: str, num_articles: int = 3) -> Dict[str, Any]:
        """
        Perform a quick search and basic analysis
        
        Args:
            query: The search query
            num_articles: Number of articles to find
            
        Returns:
            Dictionary containing quick search results
        """
        try:
            logger.info(f"Quick search for: {query}")
            
            # Use search agent directly for quick results
            search_results = await self.news_search_agent.search_news(query, max_articles=num_articles)
            
            if search_results.get("success"):
                return {
                    "success": True,
                    "query": query,
                    "quick_results": search_results.get("response", ""),
                    "method": "Quick Search via NewsSearchAgent",
                    "articles_count": num_articles
                }
            else:
                return {
                    "success": False,
                    "error": search_results.get("error", "Search failed"),
                    "query": query
                }
                
        except Exception as e:
            logger.error(f"Error in quick_search: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    async def analyze_article(self, content: str, title: str = "", analysis_type: str = "all") -> Dict[str, Any]:
        """
        Analyze a specific article using the content summarizer agent
        
        Args:
            content: Article content to analyze
            title: Article title
            analysis_type: Type of analysis to perform
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            logger.info(f"Analyzing article: {title[:50]}...")
            
            analysis_results = await self.content_summarizer_agent.analyze_article(
                content=content,
                title=title,
                analysis_type=analysis_type
            )
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error analyzing article: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "title": title
            }
    
    async def verify_claim(self, claim: str) -> Dict[str, Any]:
        """
        Verify a specific claim using the fact checker agent
        
        Args:
            claim: The claim to verify
            
        Returns:
            Dictionary containing verification results
        """
        try:
            logger.info(f"Verifying claim: {claim[:50]}...")
            
            verification_results = await self.fact_checker_agent.verify_specific_claim(claim)
            
            return verification_results
            
        except Exception as e:
            logger.error(f"Error verifying claim: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "claim": claim
            }
    
    async def compare_sources(self, topic: str, max_sources: int = 5) -> Dict[str, Any]:
        """
        Compare multiple sources on a topic for consistency and bias
        
        Args:
            topic: The topic to compare sources for
            max_sources: Maximum number of sources to compare
            
        Returns:
            Dictionary containing source comparison results
        """
        try:
            logger.info(f"Comparing sources for topic: {topic}")
            
            comparison_results = await self.fact_checker_agent.compare_sources(topic, max_sources)
            
            return comparison_results
            
        except Exception as e:
            logger.error(f"Error comparing sources: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "topic": topic
            }
    
    async def get_insights(self, topic: str, focus_area: str = "trends") -> Dict[str, Any]:
        """
        Generate focused insights on a specific topic
        
        Args:
            topic: The topic to generate insights for
            focus_area: Area of focus ('trends', 'credibility', 'bias', 'general')
            
        Returns:
            Dictionary containing focused insights
        """
        try:
            logger.info(f"Generating insights for: {html.escape(topic)} (focus: {html.escape(focus_area)})")
            
            # First, get recent content on the topic
            search_results = await self.news_search_agent.search_and_scrape_articles(topic, num_articles=3)
            
            if not search_results.get("success"):
                return {
                    "success": False,
                    "error": f"Could not gather content for insights: {search_results.get('error')}",
                    "topic": topic
                }
            
            # Generate focused insights
            insights_results = await self.content_summarizer_agent.generate_insights(
                content=search_results.get("articles_found", ""),
                focus_area=focus_area
            )
            
            return insights_results
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "topic": topic,
                "focus_area": focus_area
            }

# Backward compatibility wrapper
class NewsResearchAgent:
    """Backward compatibility wrapper for existing code"""
    
    def __init__(self, api_key: str = None):
        self.assistant = NewsResearchAssistant(api_key=api_key)
    
    async def research_topic(self, query: str, max_articles: int = 5) -> Dict[str, Any]:
        """Backward compatibility method"""
        return await self.assistant.research_topic(query, max_articles)
    
    async def search_news(self, query: str) -> Dict[str, Any]:
        """Backward compatibility method"""
        return await self.assistant.quick_search(query)

# Main function for direct execution
async def main():
    """Main function for testing the news research assistant"""
    assistant = NewsResearchAssistant()
    
    # Example usage
    query = "artificial intelligence latest developments"
    print(f"Researching: {query}")
    
    result = await assistant.research_topic(query, max_articles=3)
    
    if result.get("success"):
        print("\n=== RESEARCH RESULTS ===")
        print(result.get("research_report", "No report generated"))
        print(f"\nMethodology: {result.get('methodology', {})}")
    else:
        print(f"Research failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())