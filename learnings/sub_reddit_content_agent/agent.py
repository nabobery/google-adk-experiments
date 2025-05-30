# Agent definitions for Subreddit-Specific Content Tailoring Agent

from google.adk.agents import SequentialAgent, LoopAgent
from .config import MAX_ITERATIONS_REFINE

# Import sub-agent creation functions
from .sub_agents.subreddit_info_fetcher.agent import create_subreddit_info_fetcher_agent
from .sub_agents.initial_draft_generator.agent import create_initial_draft_generator_agent
from .sub_agents.quality_rule_checker.agent import create_quality_rule_checker_agent
from .sub_agents.content_refiner_exiter.agent import create_content_refiner_exiter_agent


def create_refinement_loop():
    """Creates the RefinementLoop LoopAgent"""
    return LoopAgent(
        name="RefinementLoop",
        max_iterations=MAX_ITERATIONS_REFINE,
        sub_agents=[
            create_quality_rule_checker_agent(),
            create_content_refiner_exiter_agent()
        ]
    )


def create_root_agent():
    """Creates the root SequentialAgent that orchestrates the entire pipeline"""
    return SequentialAgent(
        name="SubredditContentPipeline",
        description="Generates and refines Reddit content tailored to a specific subreddit.",
        sub_agents=[
            create_subreddit_info_fetcher_agent(),
            create_initial_draft_generator_agent(),
            create_refinement_loop()
        ]
    )


# Create the root agent instance
root_agent = create_root_agent() 