# TaskTracker MCP Server

TaskTracker MCP is a Model Context Protocol compatible version of the Terminal Task Tracker application. It exposes task and project plan management capabilities through MCP, allowing Language Models to interact with your task tracking data.

## Features

- **Resources**: Access tasks, plans, and notes data
- **Tools**: Create, update, and delete tasks and plan steps
- **Prompts**: Templates for common task management activities

## Installation

```bash
# Using uv (recommended)
uv add -e .

# Or with pip
pip install -e .
```

## Usage with Claude Desktop

```bash
# Install in Claude Desktop
mcp install mcp_server_fixed.py

# Run with MCP Inspector
mcp dev mcp_server_fixed.py
```

NOTE: If you encounter errors with `mcp_server.py`, please use the fixed version `mcp_server_fixed.py` instead. The fixed version uses a global API instance for resources and properly handles context parameters for tools.

## Running Directly

```bash
# Run server directly
python mcp_server_fixed.py

# Or using MCP CLI
mcp run mcp_server_fixed.py
```

## Resources

TaskTracker exposes the following resources:

- `tasks://all` - List all tasks
- `tasks://{task_id}` - Get a specific task
- `plan://all` - List all plan steps
- `plan://{step_id}` - Get a specific plan step
- `notes://all` - Get all notes

## Tools

TaskTracker provides the following tools:

### Task Tools
- `get_all_tasks_tool` - Get all tasks
- `get_task_tool` - Get a specific task by ID
- `add_task` - Create a new task
- `update_task` - Update an existing task
- `delete_task` - Delete a task

### Plan Tools
- `get_all_plan_steps_tool` - Get all plan steps
- `get_plan_step_tool` - Get a specific plan step by ID
- `add_plan_step` - Create a new plan step
- `update_plan_step` - Update an existing plan step
- `delete_plan_step` - Delete a plan step
- `toggle_plan_step` - Toggle completion status

### Notes and Data Tools
- `get_notes_tool` - Get all notes
- `save_notes` - Save notes
- `export_data` - Export all data to JSON
- `import_data` - Import data from JSON

## Prompts

TaskTracker includes the following prompts:

- `add_task_prompt` - Template for adding a new task
- `create_plan_prompt` - Template for creating a project plan

## Example Interactions

### Adding and Retrieving Tasks

```
> call-tool add_task "Implement login feature" "Create authentication endpoints for user login" 1 "not_started"
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Implement login feature",
  "description": "Create authentication endpoints for user login",
  "priority": 1,
  "status": "not_started",
  "created_at": "2025-04-08T14:32:15.123456",
  "updated_at": "2025-04-08T14:32:15.123456"
}

> call-tool get_all_tasks_tool
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Implement login feature",
    "description": "Create authentication endpoints for user login",
    "priority": 1,
    "status": "not_started",
    "created_at": "2025-04-08T14:32:15.123456",
    "updated_at": "2025-04-08T14:32:15.123456"
  }
]

> read-resource tasks://all
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Implement login feature",
    "description": "Create authentication endpoints for user login",
    "priority": 1,
    "status": "not_started",
    "created_at": "2025-04-08T14:32:15.123456",
    "updated_at": "2025-04-08T14:32:15.123456"
  }
]
```

### Managing Project Plans

```
> call-tool add_plan_step "Design API endpoints" "Create OpenAPI specification for endpoints" "Include authentication routes" 0 false
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "Design API endpoints",
  "description": "Create OpenAPI specification for endpoints",
  "details": "Include authentication routes",
  "order": 0,
  "completed": false,
  "created_at": "2025-04-08T14:33:15.123456",
  "updated_at": "2025-04-08T14:33:15.123456"
}

> call-tool get_all_plan_steps_tool
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "Design API endpoints",
    "description": "Create OpenAPI specification for endpoints",
    "details": "Include authentication routes",
    "order": 0,
    "completed": false,
    "created_at": "2025-04-08T14:33:15.123456",
    "updated_at": "2025-04-08T14:33:15.123456"
  }
]
```

## License

MIT