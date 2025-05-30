"""
TaskFlow Assistant - Task Management Tools

Implements comprehensive task management functionality with session state persistence.
Tools are defined using ADK's FunctionTool and expect ToolContext for state access.
Outputs are structured dictionaries for better LLM interpretation.
"""

import uuid
from typing import List, Dict, Any
from google.adk.tools import FunctionTool, ToolContext


def _ensure_tasks_initialized(tool_context: ToolContext) -> None:
    """Ensure the tasks list is properly initialized in session state via ToolContext."""
    if not hasattr(tool_context.state, "tasks") or tool_context.state.tasks is None:
        tool_context.state.tasks = []


def _find_task_by_reference(tasks: List[Dict], reference: str) -> tuple:
    """
    Find a task by number (1-based index) or description match.
    Returns (task_dict, index) or (None, -1) if not found.
    """
    # Try to parse as a number first (1-based indexing for user friendliness)
    try:
        task_num = int(reference) - 1  # Convert to 0-based index
        if 0 <= task_num < len(tasks):
            return tasks[task_num], task_num
    except ValueError:
        pass
    
    # Try to find by description (partial match, case-insensitive)
    reference_lower = reference.lower()
    for i, task in enumerate(tasks):
        if reference_lower in task["description"].lower():
            return task, i
    
    return None, -1


# Core implementation for adding a task
def _add_task_impl(task_description: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Adds a new task to the user's to-do list using ToolContext.
    Returns a structured dictionary with status and message.
    
    Args:
        task_description: Description of the task to add
        
    Returns:
        Dict[str, Any]: {"status": "success" or "error", "message": "User-facing message"}
    """
    _ensure_tasks_initialized(tool_context)
    
    if not task_description.strip():
        return {"status": "error", "message": "❌ Please provide a valid task description."}
    
    new_task = {
        "id": str(uuid.uuid4()),
        "description": task_description.strip(),
        "done": False
    }
    
    tool_context.state.tasks.append(new_task)
    task_number = len(tool_context.state.tasks)
    
    return {
        "status": "success",
        "message": f"✅ Added task #{task_number}: '{task_description}' to your to-do list."
    }


# Core implementation for listing tasks
def _list_tasks_impl(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Lists all current tasks using ToolContext.
    Returns a structured dictionary with status and message (the formatted list).
    
    Returns:
        Dict[str, Any]: {"status": "success" or "info", "message": "Formatted list or info message"}
    """
    _ensure_tasks_initialized(tool_context)
    
    if not tool_context.state.tasks:
        return {
            "status": "info",
            "message": "📝 Your to-do list is empty. Add some tasks to get started!"
        }
    
    task_list_str = ["📋 Your Tasks:"]
    completed_count = 0
    
    for i, task in enumerate(tool_context.state.tasks, 1):
        status_icon = "✅" if task["done"] else "⭕"
        task_list_str.append(f"  {i}. {status_icon} {task['description']}")
        if task["done"]:
            completed_count += 1
    
    total_tasks = len(tool_context.state.tasks)
    pending_tasks = total_tasks - completed_count
    
    task_list_str.append(f"\n📊 Summary: {pending_tasks} pending, {completed_count} completed ({total_tasks} total)")
    
    return {"status": "success", "message": "\n".join(task_list_str)}


# Core implementation for completing a task
def _complete_task_impl(task_reference: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Marks a task as completed using ToolContext.
    Returns a structured dictionary with status and message.

    Args:
        task_reference: Task number (e.g., "1") or part of task description
        
    Returns:
        Dict[str, Any]: {"status": "success", "info", or "error", "message": "User-facing message"}
    """
    _ensure_tasks_initialized(tool_context)
    
    if not tool_context.state.tasks:
        return {
            "status": "info",
            "message": "📝 No tasks available to complete. Add some tasks first!"
        }
    
    task, index = _find_task_by_reference(tool_context.state.tasks, task_reference)
    
    if task is None:
        return {
            "status": "error",
            "message": (f"❌ Couldn't find task '{task_reference}'. "
                        f"Try using the task number (1-{len(tool_context.state.tasks)}) or part of the description.")
        }
    
    if task["done"]:
        return {
            "status": "info",
            "message": f"ℹ️ Task '{task['description']}' is already completed!"
        }
    
    # Mark as completed
    tool_context.state.tasks[index]["done"] = True
    task_number = index + 1
    
    return {
        "status": "success",
        "message": f"🎉 Completed task #{task_number}: '{task['description']}'"
    }


# Core implementation for removing a task
def _remove_task_impl(task_reference: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Removes a task from the to-do list using ToolContext.
    Returns a structured dictionary with status and message.

    Args:
        task_reference: Task number (e.g., "1") or part of task description
        
    Returns:
        Dict[str, Any]: {"status": "success", "info", or "error", "message": "User-facing message"}
    """
    _ensure_tasks_initialized(tool_context)
    
    if not tool_context.state.tasks:
        return {
            "status": "info",
            "message": "📝 No tasks available to remove. Your to-do list is empty!"
        }
    
    task, index = _find_task_by_reference(tool_context.state.tasks, task_reference)
    
    if task is None:
        return {
            "status": "error",
            "message": (f"❌ Couldn't find task '{task_reference}'. "
                        f"Try using the task number (1-{len(tool_context.state.tasks)}) or part of the description.")
        }
    
    # Remove the task
    removed_task_desc = tool_context.state.tasks.pop(index)['description']
    
    return {
        "status": "success",
        "message": f"🗑️ Removed task: '{removed_task_desc}'"
    }

# Create FunctionTool instances for export
add_task_tool = FunctionTool(func=_add_task_impl, description=_add_task_impl.__doc__)
list_tasks_tool = FunctionTool(func=_list_tasks_impl, description=_list_tasks_impl.__doc__)
complete_task_tool = FunctionTool(func=_complete_task_impl, description=_complete_task_impl.__doc__)
remove_task_tool = FunctionTool(func=_remove_task_impl, description=_remove_task_impl.__doc__) 