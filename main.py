#!/usr/bin/env python3
"""
Terminal Task Tracker - Main Application Entry Point

A terminal-based task tracking application with a three-pane layout
for managing tasks and project plans.
"""

import os
import sys

from app.core.task_manager import TaskManager
from app.core.plan_manager import PlanManager
from app.api.api import TaskTrackerAPI
from app.ui.terminal_ui import TerminalUI


def main():
    """Main application entry point."""
    try:
        # Create data directory if it doesn't exist
        home_dir = os.path.expanduser("~")
        data_dir = os.path.join(home_dir, ".tasktracker")
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize managers
        task_manager = TaskManager()
        plan_manager = PlanManager()
        
        # Create API
        api = TaskTrackerAPI(task_manager, plan_manager)
        
        # Run terminal UI
        ui = TerminalUI(api)
        ui.run()
        
        # Save data on exit
        api.save_all()
        
        return 0
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())