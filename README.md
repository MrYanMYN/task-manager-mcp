# Terminal Task Tracker

A terminal-based task tracking application with a three-pane layout for managing tasks and project plans.

 # Image

![Terminal Task Tracker](https://github.com/MrYanMYN/task-manager-mcp/blob/master/img.png?raw=true)

## Features

- Three-pane terminal UI:
  - Task list (top left)
  - Task details (top right)
  - Project plan (bottom, full width)
- Task management:
  - Create, view, edit, and delete tasks
  - Set priorities and status
  - Add detailed descriptions
- Project plan management:
  - Define high-level project steps
  - Track step completion
  - Reorder steps
- Complete API for programmatic access
- Command-line interface for scripting
- Data persistence

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/terminal-task-tracker.git
cd terminal-task-tracker

# Install dependencies
pip install -e .
```

## Usage

### Terminal UI

To start the terminal UI:

```bash
python -m main.py
```

Key bindings:
- `Tab`: Cycle between windows
- `Up/Down`: Navigate lists
- `Enter`: Select task (in task list)
- `n`: New item (in task list or plan)
- `e`: Edit item
- `d`: Delete item
- `Space`: Toggle completion (in plan)
- `Esc`: Exit

### Command-line Interface

The CLI provides access to all functionality:

```bash
# List all tasks
python -m app.api.cli task list

# Add a new task
python -m app.api.cli task add "Implement feature X" --description "Details about feature X" --priority 2

# Mark a plan step as completed
python -m app.api.cli plan toggle STEP_ID

# Export data to JSON
python -m app.api.cli export data.json
```

### API Usage

```python
from app.core.task_manager import TaskManager
from app.core.plan_manager import PlanManager
from app.api.api import TaskTrackerAPI

# Initialize managers
task_manager = TaskManager("tasks.json")
plan_manager = PlanManager("plan.json")

# Create API
api = TaskTrackerAPI(task_manager, plan_manager)

# Add a task
task = api.add_task("Implement feature X", "Details about feature X", priority=2)

# Add a plan step
step = api.add_plan_step("Design architecture for shared operations module")

# Mark step as completed
api.toggle_plan_step(step["id"])

# Save data
api.save_all()
```

## Project Structure

```
terminal-task-tracker/
├── app/
│   ├── __init__.py
│   ├── core/               # Business logic
│   │   ├── __init__.py
│   │   ├── task_manager.py
│   │   └── plan_manager.py
│   ├── ui/                 # Terminal UI
│   │   ├── __init__.py
│   │   ├── terminal_ui.py
│   │   ├── ui_components.py
│   │   └── input_handler.py
│   └── api/                # API and CLI
│       ├── __init__.py
│       ├── api.py
│       └── cli.py
├── main.py                 # Main application entry point
└── README.md
```

## Data Storage

By default, data is stored in the `~/.tasktracker` directory:
- `tasks.json`: Tasks data
- `plan.json`: Project plan data
- `notes.json`: Notes data

## License

MIT