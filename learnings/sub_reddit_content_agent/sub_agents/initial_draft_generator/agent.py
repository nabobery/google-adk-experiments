# InitialDraftGeneratorAgent definition

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from ...config import (
    GEMINI_MODEL,
    STATE_USER_TOPIC_OR_URL, 
    STATE_TARGET_SUBREDDIT, 
    STATE_SUBREDDIT_RULES_AND_TONE,
    STATE_FEEDBACK_OR_OK_SIGNAL, 
    STATE_CURRENT_DRAFT,
    COMPLETION_PHRASE_SUBREDDIT_INFO_UNAVAILABLE
)
from .prompt import PROMPT_TEXT
from google.adk.agents.callback_context import CallbackContext


def create_initial_draft_generator_agent():
    """Creates the InitialDraftGeneratorAgent"""
    
    def format_instruction(context: CallbackContext):
        return PROMPT_TEXT.format(
            user_topic_or_url=context.state.get(STATE_USER_TOPIC_OR_URL, ""),
            target_subreddit=context.state.get(STATE_TARGET_SUBREDDIT, ""),
            subreddit_rules_and_tone=context.state.get(STATE_SUBREDDIT_RULES_AND_TONE, ""),
            feedback_or_ok_signal=context.state.get(STATE_FEEDBACK_OR_OK_SIGNAL, ""),
            completion_phrase_unavailable=COMPLETION_PHRASE_SUBREDDIT_INFO_UNAVAILABLE
        )
    
    return LlmAgent(
        name="InitialDraftGeneratorAgent",
        model=GEMINI_MODEL,
        instruction=format_instruction,
        output_key=STATE_CURRENT_DRAFT
    ) 