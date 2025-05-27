import logging
from typing import Dict, Any, List
from google.adk.agents import Agent
from ...tools import advanced_content_analysis_tool
from .prompt import CONTENT_SUMMARIZER_INSTRUCTION, CONTENT_SUMMARIZER_DESCRIPTION

logger = logging.getLogger(__name__)

# Main ContentSummarizerAgent following ADK patterns
root_agent = Agent(
    name="ContentSummarizerAgent", 
    model="gemini-2.0-flash",  # Use Gemini 2.0 for consistency
    instruction=CONTENT_SUMMARIZER_INSTRUCTION,
    description=CONTENT_SUMMARIZER_DESCRIPTION,
    tools=[advanced_content_analysis_tool]
)

# Legacy wrapper class for backward compatibility
class ContentSummarizerAgent:
    """Agent responsible for analyzing and summarizing news content"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.agent = root_agent
    
    async def analyze_article(self, content: str, title: str = "", analysis_type: str = "all") -> Dict[str, Any]:
        """
        Analyze a single article with comprehensive analysis
        
        Args:
            content: Article content to analyze
            title: Article title for context
            analysis_type: Type of analysis to perform
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            logger.info(f"ContentSummarizerAgent analyzing article: {title[:50]}...")
            
            analysis_request = f"""
            Please analyze the following article using the advanced_analyze_content tool:
            
            Title: {title}
            Content: {content}
            Analysis Type: {analysis_type}
            
            Provide a comprehensive analysis including:
            1. Key points and main themes
            2. Sentiment analysis with confidence scores
            3. Credibility assessment with indicators
            4. Bias detection and evaluation
            5. Important statistics or factual claims
            6. Overall quality and reliability assessment
            
            Please structure your response clearly with each analysis component.
            """
            
            response = await self.agent.run_async(analysis_request)
            
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
                "title": title,
                "analysis": final_response,
                "analysis_type": analysis_type,
                "agent_used": "ContentSummarizerAgent with Advanced Analysis"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing article: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "title": title
            }
    
    async def summarize_multiple_articles(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze and summarize multiple articles to find trends and insights
        
        Args:
            articles: List of articles with title, content, and metadata
            
        Returns:
            Dictionary containing comprehensive analysis of all articles
        """
        try:
            logger.info(f"ContentSummarizerAgent summarizing {len(articles)} articles")
            
            # Prepare articles for analysis
            article_summaries = []
            for i, article in enumerate(articles):
                article_text = f"""
                Article {i+1}:
                Title: {article.get('title', 'No title')}
                Source: {article.get('source', 'Unknown')}
                Content: {article.get('content', '')[:2000]}...
                """
                article_summaries.append(article_text)
            
            combined_content = "\n\n".join(article_summaries)
            
            analysis_request = f"""
            Please analyze the following collection of articles to identify trends, compare perspectives, and generate insights:
            
            {combined_content}
            
            For this analysis, please:
            1. Use advanced_analyze_content to analyze the combined content
            2. Identify common themes and trending topics across articles
            3. Compare different perspectives and viewpoints
            4. Assess overall credibility and bias patterns
            5. Highlight key agreements and disagreements between sources
            6. Generate actionable insights and recommendations
            7. Provide a diversity score based on source variety and perspective range
            
            Please structure your response to include:
            - Executive Summary
            - Key Themes and Trends  
            - Credibility Assessment
            - Bias Analysis
            - Source Diversity Analysis
            - Recommendations for Further Reading
            """
            
            response = await self.agent.run_async(analysis_request)
            
            # Process the response stream
            final_content = ""
            async for event in response:
                if hasattr(event, 'content') and event.content:
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
                "articles_count": len(articles),
                "summary": final_content,
                "analysis_method": "Multi-Article ADK Analysis"
            }
            
        except Exception as e:
            logger.error(f"Error summarizing articles: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "articles_count": len(articles) if articles else 0
            }
    
    async def generate_insights(self, content: str, focus_area: str = "general") -> Dict[str, Any]:
        """
        Generate specific insights focused on a particular area
        
        Args:
            content: Content to analyze for insights
            focus_area: Specific focus for insights (e.g., 'trends', 'credibility', 'bias', 'general')
            
        Returns:
            Dictionary containing focused insights
        """
        try:
            insights_request = f"""
            Generate focused insights from the following content with emphasis on {focus_area}:
            
            Content: {content}
            
            Please use the advanced_analyze_content tool and focus specifically on:
            {focus_area} analysis and provide actionable insights.
            
            Structure your response to provide:
            1. Key insights specific to {focus_area}
            2. Supporting evidence and indicators
            3. Potential implications
            4. Recommendations for action or further investigation
            """
            
            response = await self.agent.run_async(insights_request)
            
            # Extract the response
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
                "focus_area": focus_area,
                "insights": final_response,
                "analysis_type": "focused_insights"
            }
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "focus_area": focus_area
            }

# Backward compatibility function
async def analyze_content_quality(content: str, title: str = "") -> Dict[str, Any]:
    """
    Backward compatibility function for content quality analysis
    """
    agent = ContentSummarizerAgent()
    result = await agent.analyze_article(content, title, analysis_type="credibility")
    
    if result.get("success"):
        return {
            "quality_score": 0.75,  # Default score for backward compatibility
            "analysis": result.get("analysis", ""),
            "method": "Advanced ADK Analysis"
        }
    else:
        return {
            "quality_score": 0.0,
            "analysis": f"Analysis failed: {result.get('error', 'Unknown error')}",
            "method": "Error"
        } 