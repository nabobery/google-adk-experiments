# SubredditInfoFetcherAgent definition

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from ...tools import fetch_subreddit_info_tool
from ...config import (
    GEMINI_MODEL, 
    STATE_TARGET_SUBREDDIT,
    STATE_SUBREDDIT_RULES_AND_TONE, 
    STATE_GOOD_POST_EXAMPLES, 
    STATE_FEEDBACK_OR_OK_SIGNAL,
    COMPLETION_PHRASE_SUBREDDIT_INFO_UNAVAILABLE
)
from .prompt import PROMPT_TEXT


def create_subreddit_info_fetcher_agent():
    """Creates the SubredditInfoFetcherAgent"""
    
    def format_instruction(session_state):
        target_subreddit = session_state.get(STATE_TARGET_SUBREDDIT, "")
        return PROMPT_TEXT.format(
            target_subreddit=target_subreddit,
            completion_phrase_unavailable=COMPLETION_PHRASE_SUBREDDIT_INFO_UNAVAILABLE
        )
    
    return LlmAgent(
        name="SubredditInfoFetcherAgent",
        model=LiteLlm(model_name=GEMINI_MODEL),
        instruction=format_instruction,
        tools=[fetch_subreddit_info_tool],
        output_format="json",
        output_key={
            STATE_SUBREDDIT_RULES_AND_TONE: "rules_and_tone",
            STATE_GOOD_POST_EXAMPLES: "good_examples", 
            STATE_FEEDBACK_OR_OK_SIGNAL: "feedback_signal"
        }
    ) 