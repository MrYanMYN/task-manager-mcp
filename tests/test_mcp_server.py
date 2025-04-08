"""
Tests for the TaskTracker MCP server.
"""
import json
import pytest
from unittest.mock import MagicMock, patch

# Import the MCP server
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import mcp_server


@pytest.fixture
def mock_api():
    """Create a mock TaskTrackerAPI for testing."""
    mock = MagicMock()
    
    # Set up return values for get_all_tasks
    mock.get_all_tasks.return_value = [
        {
            "id": "test-task-1",
            "title": "Test Task 1",
            "description": "Description for test task 1",
            "priority": 1,
            "status": "not_started",
            "created_at": "2025-04-08T00:00:00",
            "updated_at": "2025-04-08T00:00:00"
        }
    ]
    
    # Set up return values for get_task
    mock.get_task.return_value = {
        "id": "test-task-1",
        "title": "Test Task 1",
        "description": "Description for test task 1",
        "priority": 1,
        "status": "not_started",
        "created_at": "2025-04-08T00:00:00",
        "updated_at": "2025-04-08T00:00:00"
    }
    
    # Set up return values for add_task
    mock.add_task.return_value = {
        "id": "new-task-1",
        "title": "New Task",
        "description": "Description for new task",
        "priority": 1,
        "status": "not_started",
        "created_at": "2025-04-08T00:00:00",
        "updated_at": "2025-04-08T00:00:00"
    }
    
    return mock


@patch("mcp_server.api")
def test_get_all_tasks(mock_api_module, mock_api):
    """Test the get_all_tasks resource."""
    # Set the mock API
    mock_api_module.get_all_tasks.return_value = mock_api.get_all_tasks.return_value
    
    # Call the function
    result = mcp_server.get_all_tasks()
    
    # Assert the result
    expected = json.dumps(mock_api.get_all_tasks.return_value, indent=2)
    assert result == expected
    mock_api_module.get_all_tasks.assert_called_once()


@patch("mcp_server.api")
def test_get_task(mock_api_module, mock_api):
    """Test the get_task resource."""
    # Set the mock API
    mock_api_module.get_task.return_value = mock_api.get_task.return_value
    
    # Call the function
    result = mcp_server.get_task("test-task-1")
    
    # Assert the result
    expected = json.dumps(mock_api.get_task.return_value, indent=2)
    assert result == expected
    mock_api_module.get_task.assert_called_once_with("test-task-1")


@patch("mcp_server.api")
def test_add_task(mock_api_module, mock_api):
    """Test the add_task tool."""
    # Set the mock API
    mock_api_module.add_task.return_value = mock_api.add_task.return_value
    
    # Call the function
    result = mcp_server.add_task(
        title="New Task",
        description="Description for new task",
        priority=1,
        status="not_started"
    )
    
    # Assert the result
    assert result == mock_api.add_task.return_value
    mock_api_module.add_task.assert_called_once_with(
        "New Task", "Description for new task", 1, "not_started"
    )
    mock_api_module.save_all.assert_called_once()


def test_add_task_prompt():
    """Test the add_task_prompt."""
    result = mcp_server.add_task_prompt(
        title="Test Task", 
        description="Task description"
    )
    
    assert "Test Task" in result
    assert "Task description" in result


def test_create_plan_prompt():
    """Test the create_plan_prompt."""
    result = mcp_server.create_plan_prompt()
    
    assert "project plan" in result.lower()
    assert "clear steps" in result.lower()