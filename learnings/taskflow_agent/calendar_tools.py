"""
TaskFlow Assistant - Calendar Management Tools

Implements calendar event management functionality with session state persistence.
Tools are defined using ADK's FunctionTool and expect ToolContext for state access.
Outputs are structured dictionaries for better LLM interpretation.
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
from google.adk.tools import FunctionTool, ToolContext


def _ensure_events_initialized(tool_context: ToolContext) -> None:
    """Ensure the events list is properly initialized in session state via ToolContext."""
    if not hasattr(tool_context.state, "events") or tool_context.state.events is None:
        tool_context.state.events = []


def _parse_natural_date(date_input: str) -> str:
    """Parse natural language date/time into a more standardized or recognizable format."""
    date_input_lower = date_input.strip().lower()
    now = datetime.now()
    
    time_str = ""
    if "morning" in date_input_lower: time_str = " at 9:00 AM"
    elif "afternoon" in date_input_lower: time_str = " at 2:00 PM"
    elif "evening" in date_input_lower: time_str = " at 6:00 PM"
        
    parsed_date_str = date_input # Fallback

    if "today" in date_input_lower:
        parsed_date_str = f"Today{time_str} ({now.strftime('%Y-%m-%d')}{time_str.replace(' at ', ' ')})"
    elif "tomorrow" in date_input_lower:
        tomorrow = now + timedelta(days=1)
        parsed_date_str = f"Tomorrow{time_str} ({tomorrow.strftime('%Y-%m-%d')}{time_str.replace(' at ', ' ')})"
    elif "next week" in date_input_lower:
        # Default to Monday of next week if no specific day is mentioned
        days_until_monday = (0 - now.weekday() + 7) % 7
        days_until_monday = days_until_monday if days_until_monday > 0 else 7 # if today is Monday, go to next week
        next_week_day = now + timedelta(days=days_until_monday)
        parsed_date_str = f"Next week (around {next_week_day.strftime('%A, %Y-%m-%d')}){time_str}"
        
    return parsed_date_str


def _find_event_by_reference(events: List[Dict], reference: str) -> tuple:
    """Find an event by number (1-based index) or summary match."""
    try:
        event_num = int(reference) - 1
        if 0 <= event_num < len(events):
            return events[event_num], event_num
    except ValueError:
        pass
    
    reference_lower = reference.lower()
    for i, event in enumerate(events):
        if reference_lower in event["summary"].lower():
            return event, i
            
    return None, -1


# Core implementation for adding an event
def _add_event_impl(summary: str, date_time: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Adds a new event to the user's calendar using ToolContext.
    Returns a structured dictionary with status and message.
    """
    _ensure_events_initialized(tool_context)
    
    if not summary.strip():
        return {"status": "error", "message": "❌ Please provide a valid event summary."}
    if not date_time.strip():
        return {"status": "error", "message": "❌ Please provide a date and time for the event."}
    
    formatted_date_time = _parse_natural_date(date_time)
    new_event = {
        "id": str(uuid.uuid4()),
        "summary": summary.strip(),
        "date_time": formatted_date_time
    }
    tool_context.state.events.append(new_event)
    event_number = len(tool_context.state.events)
    
    return {
        "status": "success",
        "message": f"📅 Added event #{event_number}: '{summary}' scheduled for {formatted_date_time}"
    }


# Core implementation for listing events
def _list_events_impl(tool_context: ToolContext, timeframe: str = "all") -> Dict[str, Any]:
    """
    Lists calendar events using ToolContext. Can filter by timeframe (currently shows all).
    Returns a structured dictionary with status and message (the formatted list).
    """
    _ensure_events_initialized(tool_context)
    
    if not tool_context.state.events:
        return {
            "status": "info",
            "message": "📅 Your calendar is empty. Add some events to get started!"
        }
    
    event_list_str = ["📅 Your Calendar Events:"]
    # TODO: Implement timeframe filtering based on parsed date_time
    for i, event in enumerate(tool_context.state.events, 1):
        event_list_str.append(f"  {i}. 🗓️ {event['summary']} - {event['date_time']}")
        
    total_events = len(tool_context.state.events)
    event_list_str.append(f"\n📊 Total events: {total_events}")
    if timeframe != "all":
        event_list_str.append(f"(Timeframe filter '{timeframe}' applied - currently shows all)")

    return {"status": "success", "message": "\n".join(event_list_str)}


# Core implementation for removing an event
def _remove_event_impl(event_reference: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Removes an event from the calendar using ToolContext.
    Returns a structured dictionary with status and message.
    """
    _ensure_events_initialized(tool_context)
    
    if not tool_context.state.events:
        return {
            "status": "info",
            "message": "📅 No events available to remove. Your calendar is empty!"
        }
    
    event, index = _find_event_by_reference(tool_context.state.events, event_reference)
    if event is None:
        return {
            "status": "error",
            "message": (f"❌ Couldn't find event '{event_reference}'. "
                        f"Try using the event number (1-{len(tool_context.state.events)}) or part of the summary.")
        }
        
    removed_event_summary = tool_context.state.events.pop(index)['summary']
    return {
        "status": "success",
        "message": f"🗑️ Removed event: '{removed_event_summary}'"
    }


# Core implementation for updating an event
def _update_event_impl(event_reference: str, tool_context: ToolContext, new_summary: str = None, new_date_time: str = None) -> Dict[str, Any]:
    """
    Updates an existing event's details (summary and/or date_time) using ToolContext.
    Returns a structured dictionary with status and message.
    """
    _ensure_events_initialized(tool_context)
    
    if not tool_context.state.events:
        return {
            "status": "info",
            "message": "📅 No events available to update. Your calendar is empty!"
        }
        
    event, index = _find_event_by_reference(tool_context.state.events, event_reference)
    if event is None:
        return {
            "status": "error",
            "message": (f"❌ Couldn't find event '{event_reference}'. "
                        f"Try using the event number (1-{len(tool_context.state.events)}) or part of the summary.")
        }

    if not new_summary and not new_date_time:
        return {
            "status": "info",
            "message": "ℹ️ No changes specified. Please provide a new summary or date/time to update."
        }
        
    updated_fields = []
    original_event_summary = event['summary'] # For the final message

    if new_summary and new_summary.strip() != event['summary']:
        event['summary'] = new_summary.strip()
        updated_fields.append(f"summary to '{event['summary']}'")
        
    if new_date_time:
        parsed_new_date_time = _parse_natural_date(new_date_time)
        if parsed_new_date_time != event['date_time']:
            event['date_time'] = parsed_new_date_time
            updated_fields.append(f"date/time to '{event['date_time']}'")
            
    if not updated_fields:
        return {
            "status": "info",
            "message": f"ℹ️ Event '{original_event_summary}' already has the specified details. No update needed."
        }
        
    tool_context.state.events[index] = event
    return {
        "status": "success",
        "message": f"📅 Updated event '{original_event_summary}' (now '{event['summary']}'): set {' and '.join(updated_fields)}."
    }

# Create FunctionTool instances for export
add_event_tool = FunctionTool(func=_add_event_impl, description=_add_event_impl.__doc__)
list_events_tool = FunctionTool(func=_list_events_impl, description=_list_events_impl.__doc__)
remove_event_tool = FunctionTool(func=_remove_event_impl, description=_remove_event_impl.__doc__)
update_event_tool = FunctionTool(func=_update_event_impl, description=_update_event_impl.__doc__) 