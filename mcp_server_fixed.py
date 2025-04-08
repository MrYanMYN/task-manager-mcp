#!/usr/bin/env python3
"""
MCP-compatible server for the Terminal Task Tracker

This server exposes the task tracker functionality through the Model Context Protocol (MCP).
"""
import json
import os
import logging
from typing import Dict, List, Optional, Any, Union, AsyncIterator
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from mcp.server.fastmcp import FastMCP, Context, Image
from app.core.task_manager import TaskManager
from app.core.plan_manager import PlanManager
from app.api.api import TaskTrackerAPI

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize data files
home_dir = os.path.expanduser("~")
data_dir = os.path.join(home_dir, ".tasktracker")
os.makedirs(data_dir, exist_ok=True)
task_file = os.path.join(data_dir, "tasks.json")
plan_file = os.path.join(data_dir, "plan.json")
notes_file = os.path.join(data_dir, "notes.txt")

# Global variable for API access from resources without URI parameters
global_api = None

# Set up lifespan context manager for the MCP server
@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """
    Initialize and manage the task and plan managers for the server's lifespan.
    
    This ensures that we have a single consistent instance of the managers
    throughout the server's lifecycle.
    """
    logger.info(f"Starting TaskTracker server with data directory: {data_dir}")
    
    # Initialize managers with explicit file paths
    task_manager = TaskManager(task_file, notes_file)
    plan_manager = PlanManager(plan_file)
    
    # Create API
    api = TaskTrackerAPI(task_manager, plan_manager)
    
    # Set global API for resources without URI parameters
    global global_api
    global_api = api
    
    try:
        # Yield the API instance to the server
        yield {"api": api}
    finally:
        # Ensure all data is saved on shutdown
        logger.info("Shutting down TaskTracker server, saving all data")
        api.save_all()

# Create an MCP server with the lifespan manager
mcp = FastMCP("TaskTracker", lifespan=lifespan)


# === Resources ===

@mcp.resource("tasks://all")
def get_all_tasks() -> str:
    """Get all tasks in the system as JSON."""
    # Reload data from files first to ensure we have latest changes
    global_api.reload_all()
    tasks = global_api.get_all_tasks()
    return json.dumps(tasks, indent=2)


@mcp.resource("tasks://{task_id}")
def get_task(task_id: str) -> str:
    """Get a specific task by ID."""
    # Reload data from files first to ensure we have latest changes
    global_api.reload_all()
    task = global_api.get_task(task_id)
    if task:
        return json.dumps(task, indent=2)
    return "Task not found"


@mcp.resource("plan://all")
def get_all_plan_steps() -> str:
    """Get all plan steps in the system as JSON."""
    # Reload data from files first to ensure we have latest changes
    global_api.reload_all()
    steps = global_api.get_all_plan_steps()
    return json.dumps(steps, indent=2)


@mcp.resource("plan://{step_id}")
def get_plan_step(step_id: str) -> str:
    """Get a specific plan step by ID."""
    # Reload data from files first to ensure we have latest changes
    global_api.reload_all()
    step = global_api.get_plan_step(step_id)
    if step:
        return json.dumps(step, indent=2)
    return "Plan step not found"


@mcp.resource("notes://all")
def get_notes() -> str:
    """Get all notes in the system."""
    # Reload data from files first to ensure we have latest changes
    global_api.reload_all()
    return global_api.get_notes()


# === Tools ===

@mcp.tool()
def get_all_tasks_tool(ctx: Context) -> List[Dict[str, Any]]:
    """
    Get all tasks in the system.
    
    Returns:
        List of all tasks
    """
    api = ctx.request_context.lifespan_context["api"]
    # Reload data from files first to ensure we have latest changes
    api.reload_all()
    return api.get_all_tasks()


@mcp.tool()
def get_task_tool(task_id: str, ctx: Context) -> Dict[str, Any]:
    """
    Get a specific task by ID.
    
    Args:
        task_id: The ID of the task to retrieve
        
    Returns:
        The task or an error message if not found
    """
    api = ctx.request_context.lifespan_context["api"]
    # Reload data from files first to ensure we have latest changes
    api.reload_all()
    task = api.get_task(task_id)
    if task:
        return task
    return {"error": "Task not found"}


@mcp.tool()
def get_all_plan_steps_tool(ctx: Context) -> List[Dict[str, Any]]:
    """
    Get all plan steps in the system.
    
    Returns:
        List of all plan steps
    """
    api = ctx.request_context.lifespan_context["api"]
    # Reload data from files first to ensure we have latest changes
    api.reload_all()
    return api.get_all_plan_steps()


@mcp.tool()
def get_plan_step_tool(step_id: str, ctx: Context) -> Dict[str, Any]:
    """
    Get a specific plan step by ID.
    
    Args:
        step_id: The ID of the plan step to retrieve
        
    Returns:
        The plan step or an error message if not found
    """
    api = ctx.request_context.lifespan_context["api"]
    # Reload data from files first to ensure we have latest changes
    api.reload_all()
    step = api.get_plan_step(step_id)
    if step:
        return step
    return {"error": "Plan step not found"}


@mcp.tool()
def get_notes_tool(ctx: Context) -> str:
    """
    Get all notes in the system.
    
    Returns:
        The notes text
    """
    api = ctx.request_context.lifespan_context["api"]
    # Reload data from files first to ensure we have latest changes
    api.reload_all()
    return api.get_notes()


@mcp.tool()
def add_task(title: str, ctx: Context, description: str = "", priority: int = 1, 
             status: str = "not_started") -> Dict[str, Any]:
    """
    Add a new task to the system.
    
    Args:
        title: The title of the task
        ctx: The MCP context object
        description: A detailed description of the task
        priority: Priority level (1-3, with 1 being highest)
        status: Current status (not_started, in_progress, completed)
        
    Returns:
        The newly created task
    """
    api = ctx.request_context.lifespan_context["api"]
    # Reload data from files first to ensure we have latest changes
    api.reload_all()
    task = api.add_task(title, description, priority, status)
    api.save_all()
    logger.info(f"Added task: {title} (ID: {task['id']})")
    return task


@mcp.tool()
def update_task(task_id: str, ctx: Context, title: Optional[str] = None, 
                description: Optional[str] = None, priority: Optional[int] = None,
                status: Optional[str] = None) -> Dict[str, Any]:
    """
    Update an existing task.
    
    Args:
        task_id: The ID of the task to update
        title: New title (optional)
        description: New description (optional)
        priority: New priority (optional)
        status: New status (optional)
        
    Returns:
        The updated task or None if task not found
    """
    api = ctx.request_context.lifespan_context["api"]
    # Reload data from files first to ensure we have latest changes
    api.reload_all()
    
    kwargs = {}
    if title is not None:
        kwargs["title"] = title
    if description is not None:
        kwargs["description"] = description
    if priority is not None:
        kwargs["priority"] = priority
    if status is not None:
        kwargs["status"] = status
        
    task = api.update_task(task_id, **kwargs)
    if task:
        api.save_all()
        logger.info(f"Updated task ID: {task_id}")
    else:
        logger.warning(f"Failed to update task: {task_id} - Not found")
    return task or {"error": "Task not found"}


@mcp.tool()
def delete_task(task_id: str, ctx: Context) -> Dict[str, Any]:
    """
    Delete a task.
    
    Args:
        task_id: The ID of the task to delete
        
    Returns:
        Success or failure message
    """
    api = ctx.request_context.lifespan_context["api"]
    # Reload data from files first to ensure we have latest changes
    api.reload_all()
    
    result = api.delete_task(task_id)
    if result:
        api.save_all()
        logger.info(f"Deleted task ID: {task_id}")
        return {"success": True, "message": "Task deleted successfully"}
    logger.warning(f"Failed to delete task: {task_id} - Not found")
    return {"success": False, "message": "Task not found"}


@mcp.tool()
def add_plan_step(name: str, ctx: Context, description: str = "", details: str = "",
                  order: Optional[int] = None, completed: bool = False) -> Dict[str, Any]:
    """
    Add a new plan step.
    
    Args:
        name: The name of the plan step
        description: A brief description
        details: Detailed information about the step
        order: Position in the plan (optional)
        completed: Whether the step is completed
        
    Returns:
        The newly created plan step
    """
    api = ctx.request_context.lifespan_context["api"]
    # Reload data from files first to ensure we have latest changes
    api.reload_all()
    
    step = api.add_plan_step(name, description, details, order, completed)
    api.save_all()
    logger.info(f"Added plan step: {name} (ID: {step['id']})")
    return step


@mcp.tool()
def update_plan_step(step_id: str, ctx: Context, name: Optional[str] = None,
                     description: Optional[str] = None, details: Optional[str] = None,
                     order: Optional[int] = None, completed: Optional[bool] = None) -> Dict[str, Any]:
    """
    Update an existing plan step.
    
    Args:
        step_id: The ID of the step to update
        name: New name (optional)
        description: New description (optional)
        details: New details (optional)
        order: New order (optional)
        completed: New completion status (optional)
        
    Returns:
        The updated plan step or None if not found
    """
    api = ctx.request_context.lifespan_context["api"]
    # Reload data from files first to ensure we have latest changes
    api.reload_all()
    
    kwargs = {}
    if name is not None:
        kwargs["name"] = name
    if description is not None:
        kwargs["description"] = description
    if details is not None:
        kwargs["details"] = details
    if order is not None:
        kwargs["order"] = order
    if completed is not None:
        kwargs["completed"] = completed
        
    step = api.update_plan_step(step_id, **kwargs)
    if step:
        api.save_all()
        logger.info(f"Updated plan step ID: {step_id}")
    else:
        logger.warning(f"Failed to update plan step: {step_id} - Not found")
    return step or {"error": "Plan step not found"}


@mcp.tool()
def delete_plan_step(step_id: str, ctx: Context) -> Dict[str, Any]:
    """
    Delete a plan step.
    
    Args:
        step_id: The ID of the step to delete
        
    Returns:
        Success or failure message
    """
    api = ctx.request_context.lifespan_context["api"]
    # Reload data from files first to ensure we have latest changes
    api.reload_all()
    
    result = api.delete_plan_step(step_id)
    if result:
        api.save_all()
        logger.info(f"Deleted plan step ID: {step_id}")
        return {"success": True, "message": "Plan step deleted successfully"}
    logger.warning(f"Failed to delete plan step: {step_id} - Not found")
    return {"success": False, "message": "Plan step not found"}


@mcp.tool()
def toggle_plan_step(step_id: str, ctx: Context) -> Dict[str, Any]:
    """
    Toggle the completion status of a plan step.
    
    Args:
        step_id: The ID of the step to toggle
        
    Returns:
        The updated plan step or None if not found
    """
    api = ctx.request_context.lifespan_context["api"]
    # Reload data from files first to ensure we have latest changes
    api.reload_all()
    
    step = api.toggle_plan_step(step_id)
    if step:
        api.save_all()
        logger.info(f"Toggled completion status of plan step ID: {step_id} to {step['completed']}")
    else:
        logger.warning(f"Failed to toggle plan step: {step_id} - Not found")
    return step or {"error": "Plan step not found"}


@mcp.tool()
def save_notes(notes_text: str, ctx: Context) -> Dict[str, Any]:
    """
    Save notes to the system.
    
    Args:
        notes_text: The notes text to save
        
    Returns:
        Success message
    """
    api = ctx.request_context.lifespan_context["api"]
    # Reload data from files first to ensure we have latest changes
    api.reload_all()
    
    api.save_notes(notes_text)
    api.save_all()
    logger.info("Notes saved")
    return {"success": True, "message": "Notes saved successfully"}


@mcp.tool()
def export_data(file_path: str, ctx: Context) -> Dict[str, Any]:
    """
    Export all data to a JSON file.
    
    Args:
        file_path: Path to save the exported data
        
    Returns:
        Success or failure message
    """
    api = ctx.request_context.lifespan_context["api"]
    # Reload data from files first to ensure we have latest changes
    api.reload_all()
    
    try:
        api.export_data(file_path)
        logger.info(f"Data exported to {file_path}")
        return {"success": True, "message": f"Data exported to {file_path}"}
    except Exception as e:
        logger.error(f"Export failed: {str(e)}")
        return {"success": False, "message": f"Export failed: {str(e)}"}


@mcp.tool()
def import_data(file_path: str, ctx: Context) -> Dict[str, Any]:
    """
    Import data from a JSON file.
    
    Args:
        file_path: Path to the file containing the data to import
        
    Returns:
        Success or failure message
    """
    api = ctx.request_context.lifespan_context["api"]
    # Reload data from files first to ensure we have latest changes
    api.reload_all()
    
    try:
        result = api.import_data(file_path)
        if result:
            logger.info(f"Data imported from {file_path}")
            return {"success": True, "message": "Data imported successfully"}
        logger.warning(f"Import failed from {file_path}")
        return {"success": False, "message": "Import failed"}
    except Exception as e:
        logger.error(f"Import failed: {str(e)}")
        return {"success": False, "message": f"Import failed: {str(e)}"}


# === Prompts ===

@mcp.prompt()
def add_task_prompt(title: str = "", description: str = "") -> str:
    """Create a prompt to add a new task."""
    return f"""Please add a new task with the following details:
Title: {title}
Description: {description}

Please provide any missing information and set the priority and status.
"""


@mcp.prompt()
def create_plan_prompt() -> str:
    """Create a prompt to help create a new project plan."""
    return """I need to create a new project plan. Please help me break down this project into clear steps.

For each step, I need:
1. A clear name
2. A brief description
3. Any detailed information needed to complete the step
4. The logical order of the steps

Please ask me about my project goals so you can help create an appropriate plan.
"""


# Define a main function for entry point
def main():
    """Run the MCP server."""
    mcp.run()


# Run the server if executed directly
if __name__ == "__main__":
    main()