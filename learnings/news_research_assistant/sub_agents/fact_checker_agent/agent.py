import logging
from typing import Dict, Any, List
from google.adk.agents import Agent
from ...tools import enhanced_web_scraping_tool, advanced_content_analysis_tool, google_search_tool
from .prompt import FACT_CHECKER_INSTRUCTION, FACT_CHECKER_DESCRIPTION

logger = logging.getLogger(__name__)

# Main FactCheckerAgent following ADK patterns
root_agent = Agent(
    name="FactCheckerAgent",
    model="gemini-2.5-flash-preview-05-20",  # Use Gemini 2.0 for consistency
    instruction=FACT_CHECKER_INSTRUCTION,
    description=FACT_CHECKER_DESCRIPTION,
    tools=[google_search_tool, enhanced_web_scraping_tool, advanced_content_analysis_tool]
)

# Legacy wrapper class for backward compatibility
class FactCheckerAgent:
    """Specialized agent for fact-checking claims against multiple sources"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.agent = root_agent
    
    async def fact_check_content(self, content: str, title: str = "") -> Dict[str, Any]:
        """Perform comprehensive fact-checking on content"""
        try:
            if not content:
                return {
                    "success": False,
                    "error": "No content provided for fact-checking"
                }
            
            logger.info(f"Fact-checking content: {title[:50]}...")
            
            fact_check_request = f"""
            Please fact-check the following content by:
            
            1. Extracting specific, verifiable claims from the content
            2. Using google_search to find supporting or contradicting evidence
            3. Using enhanced_scrape_article to get detailed information from sources
            4. Using advanced_analyze_content to assess source credibility
            5. Providing clear verdicts: VERIFIED, DISPUTED, UNVERIFIED, or FALSE
            
            Title: {title}
            Content: {content}
            
            Please structure your response to include:
            - List of claims identified
            - For each claim: verdict, confidence score, supporting sources
            - Overall credibility assessment
            - Summary of findings
            """
            
            response = await self.agent.run_async(fact_check_request)
            
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
                "fact_check_results": final_response,
                "agent_used": "FactCheckerAgent with ADK tools"
            }
            
        except Exception as e:
            logger.error(f"Error in fact-checking: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "title": title
            }
    
    async def verify_specific_claim(self, claim: str) -> Dict[str, Any]:
        """Verify a specific claim against multiple sources"""
        try:
            logger.info(f"Verifying claim: {claim[:100]}...")
            
            claim_verification_request = f"""
            Please verify the following specific claim:
            
            Claim: {claim}
            
            Steps to follow:
            1. Use google_search to find relevant sources about this claim
            2. Use enhanced_scrape_article to get detailed content from top sources
            3. Use advanced_analyze_content to assess source credibility
            4. Cross-reference information from multiple sources
            5. Provide a clear verdict with confidence score
            
            Please provide:
            - Verdict (VERIFIED/DISPUTED/UNVERIFIED/FALSE)
            - Confidence score (0.0 to 1.0)
            - Supporting evidence
            - Source credibility assessment
            - Reasoning for the verdict
            """
            
            response = await self.agent.run_async(claim_verification_request)
            
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
                "claim": claim,
                "verification_results": final_response,
                "agent_used": "FactCheckerAgent"
            }
            
        except Exception as e:
            logger.error(f"Error verifying claim: {str(e)}")
            return {
                "success": False,
                "claim": claim,
                "error": str(e)
            }
    
    async def compare_sources(self, topic: str, max_sources: int = 5) -> Dict[str, Any]:
        """Compare multiple sources on a topic for consistency and bias"""
        try:
            logger.info(f"Comparing sources for topic: {topic}")
            
            source_comparison_request = f"""
            Please find and compare multiple sources about the topic: {topic}
            
            Steps:
            1. Use google_search to find {max_sources} different sources about this topic
            2. Use enhanced_scrape_article to get content from each source
            3. Use advanced_analyze_content to analyze each source for bias and credibility
            4. Compare the information across sources
            5. Identify agreements, disagreements, and potential bias patterns
            
            Please provide:
            - Summary of each source's perspective
            - Credibility assessment for each source
            - Areas of agreement vs disagreement
            - Bias analysis across sources
            - Overall reliability assessment of the information
            """
            
            response = await self.agent.run_async(source_comparison_request)
            
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
                "topic": topic,
                "sources_compared": max_sources,
                "comparison_results": final_response,
                "agent_used": "FactCheckerAgent"
            }
            
        except Exception as e:
            logger.error(f"Error comparing sources: {str(e)}")
            return {
                "success": False,
                "topic": topic,
                "error": str(e)
            } 