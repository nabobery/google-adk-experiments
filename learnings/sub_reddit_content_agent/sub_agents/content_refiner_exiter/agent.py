# ContentRefinerOrExiterAgent definition

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from ...tools import exit_loop_tool
from ...config import (
    GEMINI_MODEL,
    STATE_CURRENT_DRAFT, 
    STATE_FEEDBACK_OR_OK_SIGNAL,
    COMPLETION_PHRASE_QUALITY_CHECK
)
from .prompt import PROMPT_TEXT
from google.adk.agents.callback_context import CallbackContext

def create_content_refiner_exiter_agent():
    """Creates the ContentRefinerOrExiterAgent"""
    
    def format_instruction(context: CallbackContext):
        return PROMPT_TEXT.format(
            current_draft=context.state.get(STATE_CURRENT_DRAFT, ""),
            feedback_or_ok_signal=context.state.get(STATE_FEEDBACK_OR_OK_SIGNAL, ""),
            completion_phrase_quality_check=COMPLETION_PHRASE_QUALITY_CHECK
        )
    
    return LlmAgent(
        name="ContentRefinerOrExiterAgent",
        model=GEMINI_MODEL,
        instruction=format_instruction,
        tools=[exit_loop_tool],
        output_key=STATE_CURRENT_DRAFT
    ) 