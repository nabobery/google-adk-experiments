# Subreddit-Specific Content Tailoring Agent

A sophisticated multi-agent system built with Google ADK that generates and iteratively refines Reddit content tailored to specific subreddit requirements.

## 🎯 Overview

This agent takes a user-provided topic or URL and a target subreddit, then generates an initial Reddit post and iteratively refines it to meet the specific quality and rule requirements of the target subreddit.

## 🏗️ Architecture

The system demonstrates key ADK patterns:

- **Sequential Pipeline**: Coordinated multi-agent workflow
- **Iterative Refinement**: LoopAgent for continuous improvement
- **Tool Integration**: Custom tools for specialized functions
- **Dynamic Prompts**: Context-aware prompt formatting
- **Session State Management**: Persistent state across agents
- **Modular Design**: Each sub-agent is self-contained with its own definition and prompt

### Agent Hierarchy

```
SubredditContentPipeline (SequentialAgent)
├── SubredditInfoFetcherAgent (LlmAgent)
├── InitialDraftGeneratorAgent (LlmAgent)
└── RefinementLoop (LoopAgent)
    ├── QualityRuleCheckerAgent (LlmAgent)
    └── ContentRefinerOrExiterAgent (LlmAgent)
```

## 🚀 Quick Start

### Prerequisites

1. **Install Dependencies**:

   ```bash
   pip install google-adk litellm
   ```

2. **Set up API Key**:
   ```bash
   export GOOGLE_API_KEY="your_gemini_api_key_here"
   ```

### Running the Agent

#### Interactive Mode

```bash
cd learnings/sub_reddit_content_agent
python -m learnings.sub_reddit_content_agent.main
```

#### Programmatic Usage

```python
from learnings.sub_reddit_content_agent.main import run_subreddit_content_agent
import asyncio

result = asyncio.run(run_subreddit_content_agent(
    user_topic_or_url="Best practices for Python async programming",
    target_subreddit="r/python"
))
```

## 🧪 Supported Subreddits

The system comes with predefined rules and examples for:

- **r/python**: Technical Python discussions
- **r/MachineLearning**: Research-focused ML content
- **r/webdev**: Web development topics

For other subreddits, the system will generate general high-quality Reddit content.

## 📊 Example Usage

```
🤖 Subreddit-Specific Content Tailoring Agent
==================================================
Enter your topic or URL: Introduction to async/await in Python
Enter target subreddit (e.g., r/python): r/python

🚀 Starting Subreddit Content Tailoring Agent
📝 Topic/URL: Introduction to async/await in Python
🎯 Target Subreddit: r/python
============================================================

✅ Agent execution completed!
============================================================
📄 Final Reddit Post Draft:
----------------------------------------
Title: Python Async/Await: A Comprehensive Guide for Better Concurrency
Body: Async/await syntax in Python 3.5+ revolutionized how we handle...
[Content continues with proper formatting and examples]
----------------------------------------

🎉 Content generation completed successfully!
```

## 🔧 Configuration

Key settings in `config.py`:

- `GEMINI_MODEL`: Model version (default: "gemini-2.5-flash-preview-05-20")
- `MAX_ITERATIONS_REFINE`: Maximum refinement iterations (default: 5)
- `PREDEFINED_SUBREDDIT_INFO`: Subreddit rules and examples

## 📁 Project Structure

```
learnings/sub_reddit_content_agent/
├── __init__.py                     # Package initialization
├── config.py                       # Configuration constants
├── tools.py                        # Custom ADK tools
├── agent.py                        # Main agent orchestration (imports sub-agents)
├── main.py                         # Entry point
├── README.md                       # This file
├── planning.md                     # Design documentation
├── execution.md                    # Implementation report
└── sub_agents/                     # Sub-agent definitions
    ├── __init__.py
    ├── subreddit_info_fetcher/
    │   ├── __init__.py
    │   ├── prompt.py               # Agent-specific prompt
    │   └── agent.py                # Agent definition and creation function
    ├── initial_draft_generator/
    │   ├── __init__.py
    │   ├── prompt.py               # Agent-specific prompt
    │   └── agent.py                # Agent definition and creation function
    ├── quality_rule_checker/
    │   ├── __init__.py
    │   ├── prompt.py               # Agent-specific prompt
    │   └── agent.py                # Agent definition and creation function
    └── content_refiner_exiter/
        ├── __init__.py
        ├── prompt.py               # Agent-specific prompt
        └── agent.py                # Agent definition and creation function
```

## 🔧 Modular Design Benefits

### Enhanced Organization

- **Separation of Concerns**: Each sub-agent has its own directory with prompt and logic
- **Easy Maintenance**: Update individual agents without affecting others
- **Clear Ownership**: Each agent's behavior is self-contained
- **Scalability**: Add new agents by creating new sub-agent folders

### Customization

- **Individual Prompts**: Each agent's prompt can be easily modified in its `prompt.py` file
- **Independent Configuration**: Each agent manages its own state mappings and tools
- **Flexible Models**: Different agents can use different LLM models if needed

## 🚀 Future Enhancements

- **Real Reddit API Integration**: Live subreddit data fetching
- **Web Scraping**: Dynamic rule discovery
- **Advanced Quality Metrics**: Sophisticated content evaluation
- **Multi-Model Support**: Test different LLMs for different tasks
- **User Feedback Loop**: Manual refinement suggestions
- **Plugin Architecture**: Easy addition of new sub-agents

## 📖 Learn More

- Check `planning.md` for detailed design documentation
- See `execution.md` for implementation details and metrics
- Explore individual agent files in `sub_agents/*/agent.py` for specific agent behavior
- Modify prompts in `sub_agents/*/prompt.py` to customize agent instructions
