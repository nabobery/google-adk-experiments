# Tools for Subreddit-Specific Content Tailoring Agent

import json
from google.adk.tools import ToolContext
from .config import PREDEFINED_SUBREDDIT_INFO


def exit_loop_tool(tool_context: ToolContext) -> dict:
    """Tool to exit the refinement loop when content is satisfactory."""
    tool_context.actions.escalate = True
    return {}


def fetch_subreddit_info_tool(tool_context: ToolContext, target_subreddit: str) -> dict:
    """
    Tool to fetch subreddit information including rules, tone, and good examples.
    
    Args:
        tool_context: The tool context provided by ADK
        target_subreddit: The target subreddit (e.g., "r/python")
    
    Returns:
        Dictionary containing subreddit information or error message
    """
    try:
        # Normalize subreddit name (ensure it starts with r/)
        if not target_subreddit.startswith('r/'):
            if target_subreddit.startswith('/'):
                target_subreddit = 'r' + target_subreddit
            else:
                target_subreddit = 'r/' + target_subreddit
        
        # Check if we have predefined information for this subreddit
        if target_subreddit in PREDEFINED_SUBREDDIT_INFO:
            info = PREDEFINED_SUBREDDIT_INFO[target_subreddit]
            return {
                "subreddit_rules_summary": info["rules_and_tone"],
                "good_post_examples_list": info["good_examples"],
                "status": "success"
            }
        else:
            # For subreddits not in our predefined list, return a generic response
            # In a real implementation, this would make web requests to Reddit API
            # or use web scraping to gather actual subreddit information
            return {
                "error": f"No predefined information available for {target_subreddit}. In a full implementation, this would fetch real data from Reddit API.",
                "status": "unavailable"
            }
            
    except Exception as e:
        return {
            "error": f"Error fetching subreddit information: {str(e)}",
            "status": "error"
        } 