# QualityRuleCheckerAgent definition

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from ...config import (
    GEMINI_MODEL,
    STATE_TARGET_SUBREDDIT, 
    STATE_CURRENT_DRAFT, 
    STATE_SUBREDDIT_RULES_AND_TONE,
    STATE_GOOD_POST_EXAMPLES, 
    STATE_FEEDBACK_OR_OK_SIGNAL,
    COMPLETION_PHRASE_QUALITY_CHECK
)
from .prompt import PROMPT_TEXT
from google.adk.agents.callback_context import CallbackContext


def create_quality_rule_checker_agent():
    """Creates the QualityRuleCheckerAgent"""
    
    def format_instruction(context: CallbackContext):
        good_examples_list = context.state.get(STATE_GOOD_POST_EXAMPLES, [])
        if isinstance(good_examples_list, list):
            good_post_examples_text = "\n".join(good_examples_list) if good_examples_list else "No examples available."
        else: # Should ideally not happen if state is managed well, but good for robustness
            good_post_examples_text = str(good_examples_list) if good_examples_list else "No examples available."

        return PROMPT_TEXT.format(
            current_draft=context.state.get(STATE_CURRENT_DRAFT, ""),
            target_subreddit=context.state.get(STATE_TARGET_SUBREDDIT, ""),
            subreddit_rules_and_tone=context.state.get(STATE_SUBREDDIT_RULES_AND_TONE, ""),
            good_post_examples_text=good_post_examples_text,
            completion_phrase_quality_check=COMPLETION_PHRASE_QUALITY_CHECK
        )
    
    return LlmAgent(
        name="QualityRuleCheckerAgent",
        model=GEMINI_MODEL,
        instruction=format_instruction,
        output_key=STATE_FEEDBACK_OR_OK_SIGNAL
    ) 