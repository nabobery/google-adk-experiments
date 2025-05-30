# SubredditInfoFetcherAgent definition

import json
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
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


def process_subreddit_info_output(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> None:
    """
    Parses the LLM's JSON output and updates the session state with individual keys.
    """
    response_text = llm_response.content.parts[0].text
    if not response_text:
        print("Warning: SubredditInfoFetcherAgent's LLM response text is empty.")
        error_msg = (
            "Error: LLM provided no output. Expected JSON with keys "
            "'rules_and_tone', 'good_examples', 'feedback_signal'."
        )
        callback_context.state[STATE_SUBREDDIT_RULES_AND_TONE] = "Unavailable - LLM provided no output"
        callback_context.state[STATE_GOOD_POST_EXAMPLES] = "Unavailable - LLM provided no output"
        callback_context.state[STATE_FEEDBACK_OR_OK_SIGNAL] = error_msg
        return

    try:
        data = json.loads(response_text)

        parsed_rules = data.get(
            "rules_and_tone", "Unavailable - Key 'rules_and_tone' missing in LLM JSON response"
        )
        parsed_examples = data.get(
            "good_examples", "Unavailable - Key 'good_examples' missing in LLM JSON response"
        )

        if "feedback_signal" not in data:
            # If the LLM is supposed to always provide feedback_signal, its absence is an error.
            # The COMPLETION_PHRASE_SUBREDDIT_INFO_UNAVAILABLE is a valid signal *from* the LLM,
            # so we should differentiate.
            feedback_signal_val = "Error: 'feedback_signal' key missing in LLM JSON response."
            print(feedback_signal_val) # Log this structural issue
        else:
            feedback_signal_val = data["feedback_signal"]

        callback_context.state[STATE_SUBREDDIT_RULES_AND_TONE] = parsed_rules
        callback_context.state[STATE_GOOD_POST_EXAMPLES] = parsed_examples
        callback_context.state[STATE_FEEDBACK_OR_OK_SIGNAL] = feedback_signal_val

    except json.JSONDecodeError:
        error_message = f"Error: Failed to decode LLM output as JSON. Raw output (first 200 chars): '{response_text[:200]}...'"
        print(error_message)
        callback_context.state[STATE_SUBREDDIT_RULES_AND_TONE] = "Unavailable - LLM output not valid JSON"
        callback_context.state[STATE_GOOD_POST_EXAMPLES] = "Unavailable - LLM output not valid JSON"
        callback_context.state[STATE_FEEDBACK_OR_OK_SIGNAL] = error_message
    except Exception as e: # Catch any other unexpected errors during processing
        error_message = f"Error processing LLM output in callback: {str(e)}. Raw output (first 200 chars): '{response_text[:200]}...'"
        print(error_message)
        callback_context.state[STATE_SUBREDDIT_RULES_AND_TONE] = "Unavailable - Error in callback processing LLM output"
        callback_context.state[STATE_GOOD_POST_EXAMPLES] = "Unavailable - Error in callback processing LLM output"
        callback_context.state[STATE_FEEDBACK_OR_OK_SIGNAL] = error_message
    return None


def create_subreddit_info_fetcher_agent():
    """Creates the SubredditInfoFetcherAgent"""
    
    def format_instruction(context: CallbackContext):
        target_subreddit = context.state.get(STATE_TARGET_SUBREDDIT, "")
        return PROMPT_TEXT.format(
            target_subreddit=target_subreddit,
            completion_phrase_unavailable=COMPLETION_PHRASE_SUBREDDIT_INFO_UNAVAILABLE
        )
    
    return LlmAgent(
        name="SubredditInfoFetcherAgent",
        model=GEMINI_MODEL,
        instruction=format_instruction,
        tools=[fetch_subreddit_info_tool],
        after_model_callback=[process_subreddit_info_output],
        output_key=None  # Callback handles state updates
    ) 