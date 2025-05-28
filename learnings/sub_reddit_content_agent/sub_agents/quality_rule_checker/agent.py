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


def create_quality_rule_checker_agent():
    """Creates the QualityRuleCheckerAgent"""
    
    def format_instruction(session_state):
        good_examples = session_state.get(STATE_GOOD_POST_EXAMPLES, [])
        if isinstance(good_examples, list):
            good_examples_text = "\n".join(good_examples) if good_examples else "No examples available"
        else:
            good_examples_text = str(good_examples)
            
        return PROMPT_TEXT.format(
            target_subreddit=session_state.get(STATE_TARGET_SUBREDDIT, ""),
            current_draft=session_state.get(STATE_CURRENT_DRAFT, ""),
            subreddit_rules_and_tone=session_state.get(STATE_SUBREDDIT_RULES_AND_TONE, ""),
            good_post_examples=good_examples_text,
            completion_phrase_ok=COMPLETION_PHRASE_QUALITY_CHECK
        )
    
    return LlmAgent(
        name="QualityRuleCheckerAgent",
        model=LiteLlm(model_name=GEMINI_MODEL),
        instruction=format_instruction,
        output_key=STATE_FEEDBACK_OR_OK_SIGNAL
    ) 