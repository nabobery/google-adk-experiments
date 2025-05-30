"""
TaskFlow Assistant - Agent Module Initialization

Exposes the root_agent for discovery by the ADK framework.
This allows the main.py to automatically load this agent.
"""

from .agent import root_agent

__all__ = ["root_agent"]
