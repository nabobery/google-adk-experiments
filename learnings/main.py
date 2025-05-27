#!/usr/bin/env python3
"""
News Research Assistant - Main Application
A comprehensive news research system using Google ADK with specialized agents.
"""

import os
import sys
import uvicorn
import asyncio
import logging
from pathlib import Path
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
from dotenv import load_dotenv

# Add current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
load_dotenv()

# Set up paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
print(f"BASE_DIR: {BASE_DIR}")
AGENT_DIR = BASE_DIR  # Directory containing the agent

# Set up DB path for sessions
SESSION_DB_URL = f"sqlite:///{os.path.join(BASE_DIR, 'sessions.db')}"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validate required environment variables
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY is required. Please set it in your .env file or environment variables.")

# Create the FastAPI app using ADK's helper
app: FastAPI = get_fast_api_app(
    agent_dir=AGENT_DIR,
    session_db_url=SESSION_DB_URL,
    allow_origins=["*"],  # In production, restrict this
    web=True,  # Enable the ADK Web UI
)

# Add custom endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/agent-info")
async def agent_info():
    """Provide agent information"""
    from news_research_assistant import root_agent

    return {
        "agent_name": root_agent.name,
        "description": root_agent.description,
        "model": str(root_agent.model),
        "capabilities": [
            "Research news topics comprehensively",
            "Verify claims and fact-check content", 
            "Analyze individual articles for quality and credibility",
            "Compare coverage across different news sources"
        ]
    }

async def run_cli_mode():
    """Run the assistant in CLI mode for testing"""
    try:
        from news_research_assistant import root_agent
        
        logger.info("Starting CLI mode...")
        print("\n🔍 News Research Assistant - CLI Mode")
        print("=" * 50)
        print("Available commands:")
        print("1. research <topic> - Research news on a topic")
        print("2. verify <claim> - Verify a specific claim")
        print("3. analyze <url> - Analyze a specific article")
        print("4. compare <topic> - Compare sources on a topic")
        print("5. quit - Exit the program")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\n📝 Enter command: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                
                if len(parts) < 2:
                    print("❌ Please provide a topic, claim, or URL after the command")
                    continue
                
                query = parts[1]
                print(f"\n🔄 Processing: {command} - {query}")
                
                # Route to appropriate method
                if command == "research":
                    result = await root_agent.research_topic(query)
                elif command == "verify":
                    result = await root_agent.verify_claim(query)
                elif command == "analyze":
                    result = await root_agent.analyze_article(query)
                elif command == "compare":
                    result = await root_agent.compare_sources(query)
                else:
                    print("❌ Unknown command. Use: research, verify, analyze, compare, or quit")
                    continue
                
                # Display results
                print_result(result, command)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error processing command: {str(e)}")
                print(f"❌ Error: {str(e)}")
                
    except Exception as e:
        logger.error(f"Failed to start CLI mode: {str(e)}")
        print(f"❌ Error starting CLI: {str(e)}")

def print_result(result: dict, command: str):
    """Print formatted results"""
    if not result.get("success", False):
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        return
    
    print(f"✅ {command.title()} completed successfully!")
    
    if command == "research":
        print(f"\n📊 Research Summary:")
        print(f"Topic: {result.get('topic', 'N/A')}")
        print(f"Articles found: {result.get('articles_found', 0)}")
        print(f"Articles analyzed: {result.get('articles_analyzed', 0)}")
        
        if result.get('research_summary'):
            print(f"\n📝 Summary: {result['research_summary']}")
        
        if result.get('recommendations'):
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(result['recommendations'], 1):
                print(f"  {i}. {rec}")
                
    elif command == "verify":
        verification = result.get('verification', {})
        print(f"\n🔍 Claim Verification:")
        print(f"Claim: {result.get('claim', 'N/A')}")
        print(f"Verdict: {verification.get('verdict', 'N/A')}")
        print(f"Confidence: {verification.get('confidence_score', 0):.2f}")
        print(f"Reason: {verification.get('reason', 'N/A')}")
        print(f"Recommendation: {result.get('recommendation', 'N/A')}")
        
    elif command == "analyze":
        quality = result.get('overall_assessment', {})
        print(f"\n📄 Article Analysis:")
        print(f"URL: {result.get('url', 'N/A')}")
        
        article_info = result.get('article_info', {})
        print(f"Title: {article_info.get('title', 'N/A')}")
        print(f"Quality: {quality.get('overall_quality', 'N/A')} (Score: {quality.get('quality_score', 0):.2f})")
        
        factors = quality.get('assessment_factors', [])
        if factors:
            print(f"Factors: {', '.join(factors)}")
            
    elif command == "compare":
        print(f"\n🔄 Source Comparison:")
        print(f"Topic: {result.get('topic', 'N/A')}")
        print(f"Sources found: {result.get('sources_found', 0)}")
        print(f"Sources analyzed: {result.get('sources_analyzed', 0)}")
        
        insights = result.get('comparison_insights', [])
        if insights:
            print(f"\n💡 Insights:")
            for i, insight in enumerate(insights, 1):
                print(f"  {i}. {insight}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="News Research Assistant")
    parser.add_argument(
        "--mode", 
        choices=["cli", "web"], 
        default="web",
        help="Run mode: cli for command line, web for web interface"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for web mode (default: 8000)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host for web mode (default: 0.0.0.0)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "cli":
        # Run CLI mode
        asyncio.run(run_cli_mode())
    else:
        # Run web mode
        logger.info(f"Starting web server on {args.host}:{args.port}")
        print(f"\n🌐 News Research Assistant Web Interface")
        print(f"🚀 Server starting on http://{args.host}:{args.port}")
        print(f"📖 Open your browser to interact with the assistant")
        print(f"📖 ADK Web UI available at: http://{args.host}:{args.port}/dev-ui")
        print(f"🛑 Press Ctrl+C to stop")
        
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            log_level="info"
        )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1) 