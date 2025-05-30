# Main entry point for Subreddit-Specific Content Tailoring Agent

import os
import asyncio
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types # Added for types.Content
from .agent import root_agent
from .config import (
    STATE_USER_TOPIC_OR_URL, 
    STATE_TARGET_SUBREDDIT, 
    STATE_CURRENT_DRAFT,
    APP_NAME # Assuming APP_NAME is defined in your config.py
)


async def run_subreddit_content_agent(user_topic_or_url: str, target_subreddit: str):
    """
    Run the Subreddit Content Tailoring Agent
    
    Args:
        user_topic_or_url: User's input topic or URL
        target_subreddit: Target subreddit for content tailoring
    
    Returns:
        The final refined content draft
    """
    session_service = InMemorySessionService()
    # Initialize runner with the root_agent and app_name
    runner = Runner(
        agent=root_agent, 
        app_name=APP_NAME, 
        session_service=session_service
    )
    
    session = await session_service.create_session(app_name=APP_NAME) # Pass app_name here too
    
    initial_state_updates = {
        STATE_USER_TOPIC_OR_URL: user_topic_or_url,
        STATE_TARGET_SUBREDDIT: target_subreddit
    }
    # Update the session state directly before running if supported, or pass as initial_event
    # For simplicity with run_async, we often construct an initial message/event if needed
    # or assume the first turn will set up based on user input if the agent is designed that way.
    # Here, we'll rely on the agent picking up from initial state passed via first message or inherent logic.

    print(f"🚀 Starting Subreddit Content Tailoring Agent")
    print(f"📝 Topic/URL: {user_topic_or_url}")
    print(f"🎯 Target Subreddit: {target_subreddit}")
    print("=" * 60)

    final_draft = None
    final_session_state = session.state # Get initial state, will be updated by events
    if final_session_state is None:
        final_session_state = {}
    final_session_state.update(initial_state_updates)

    # Construct the initial message to trigger the agent with the provided topic and subreddit
    # This is a common pattern if the agent expects user input to kick things off.
    # Alternatively, if your agent is designed to pick up STATE_USER_TOPIC_OR_URL and STATE_TARGET_SUBREDDIT
    # from the initial state without an explicit first message, this might not be strictly necessary
    # but it makes the initiation clear.
    initial_user_message = f"Create a Reddit post about '{user_topic_or_url}' for the subreddit '{target_subreddit}'."
    initial_content = types.Content(parts=[types.Part(text=initial_user_message)])

    try:
        async for event in runner.run_async(
            user_id=session.user_id, # Assuming default user_id or manage as needed
            session_id=session.id,
            new_message=initial_content,
            initial_state=initial_state_updates # Pass initial state here
        ):
            # You can inspect all events if needed for debugging:
            # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}, Actions: {event.actions}")
            if event.actions and event.actions.state_delta:
                final_session_state.update(event.actions.state_delta)
            
            if event.is_final_response():
                # The final draft should now be in the accumulated final_session_state
                pass # We will get it from final_session_state after the loop

        print("\n✅ Agent execution fully consumed!")
        print("=" * 60)
        
        if STATE_CURRENT_DRAFT in final_session_state:
            final_draft = final_session_state[STATE_CURRENT_DRAFT]
            print("📄 Final Reddit Post Draft:")
            print("-" * 40)
            print(final_draft)
            print("-" * 40)
        else:
            print("❌ No final draft was found in session state.")
            final_draft = None # Ensure it's None
            
    except Exception as e:
        print(f"❌ Error running agent: {str(e)}")
        # It's good practice to log the full traceback for async errors
        import traceback
        traceback.print_exc()
        raise
    
    return final_draft


def main():
    """Main function for interactive execution"""
    print("🤖 Subreddit-Specific Content Tailoring Agent")
    print("=" * 50)
    
    # Get user input
    user_topic_or_url = input("Enter your topic or URL: ").strip()
    if not user_topic_or_url:
        print("❌ Topic/URL cannot be empty!")
        return
    
    target_subreddit = input("Enter target subreddit (e.g., r/python): ").strip()
    if not target_subreddit:
        print("❌ Target subreddit cannot be empty!")
        return
    
    # Run the agent
    try:
        final_draft = asyncio.run(run_subreddit_content_agent(user_topic_or_url, target_subreddit))
        
        if final_draft:
            print("\n🎉 Content generation completed successfully!")
        else:
            print("\n❌ Content generation failed.")
            
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user.")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")


if __name__ == "__main__":
    # Set up environment variables if needed
    # You would typically set your API keys here:
    # os.environ["GOOGLE_API_KEY"] = "your_api_key_here"
    
    main() 