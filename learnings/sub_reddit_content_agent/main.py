# Main entry point for Subreddit-Specific Content Tailoring Agent

import os
import asyncio
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from .agent import root_agent
from .config import STATE_USER_TOPIC_OR_URL, STATE_TARGET_SUBREDDIT, STATE_CURRENT_DRAFT


async def run_subreddit_content_agent(user_topic_or_url: str, target_subreddit: str):
    """
    Run the Subreddit Content Tailoring Agent
    
    Args:
        user_topic_or_url: User's input topic or URL
        target_subreddit: Target subreddit for content tailoring
    
    Returns:
        The final refined content draft
    """
    # Initialize session service and runner
    session_service = InMemorySessionService()
    runner = Runner(session_service=session_service)
    
    # Create a new session
    session = await session_service.create_session()
    
    # Set initial state
    initial_state = {
        STATE_USER_TOPIC_OR_URL: user_topic_or_url,
        STATE_TARGET_SUBREDDIT: target_subreddit
    }
    
    print(f"🚀 Starting Subreddit Content Tailoring Agent")
    print(f"📝 Topic/URL: {user_topic_or_url}")
    print(f"🎯 Target Subreddit: {target_subreddit}")
    print("=" * 60)
    
    try:
        # Run the agent
        result = await runner.run(
            agent=root_agent,
            session_id=session.id,
            state=initial_state
        )
        
        print("\n✅ Agent execution completed!")
        print("=" * 60)
        
        # Extract the final draft from the result
        if STATE_CURRENT_DRAFT in result.state:
            final_draft = result.state[STATE_CURRENT_DRAFT]
            print("📄 Final Reddit Post Draft:")
            print("-" * 40)
            print(final_draft)
            print("-" * 40)
            return final_draft
        else:
            print("❌ No final draft was generated.")
            return None
            
    except Exception as e:
        print(f"❌ Error running agent: {str(e)}")
        raise


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