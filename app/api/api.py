from app.core.task_manager import TaskManager
from app.core.plan_manager import PlanManager


class TaskTrackerAPI:
    def __init__(self, task_manager=None, plan_manager=None):
        """Initialize the TaskTrackerAPI with task and plan managers."""
        self.task_manager = task_manager or TaskManager()
        self.plan_manager = plan_manager or PlanManager()
    
    # Task methods
    def get_all_tasks(self):
        """Get all tasks."""
        return self.task_manager.get_all_tasks()
    
    def get_task(self, task_id):
        """Get a task by ID."""
        return self.task_manager.get_task(task_id)
    
    def add_task(self, title, description="", priority=1, status="pending"):
        """Add a new task."""
        return self.task_manager.add_task(title, description, priority, status)
    
    def update_task(self, task_id, **kwargs):
        """Update a task by ID."""
        return self.task_manager.update_task(task_id, **kwargs)
    
    def delete_task(self, task_id):
        """Delete a task by ID."""
        return self.task_manager.delete_task(task_id)
    
    # Plan methods
    def get_all_plan_steps(self):
        """Get all plan steps."""
        return self.plan_manager.get_all_steps()
    
    def get_plan_step(self, step_id):
        """Get a plan step by ID."""
        return self.plan_manager.get_step(step_id)
    
    def add_plan_step(self, name, description="", details="", order=None, completed=False):
        """Add a new plan step."""
        return self.plan_manager.add_step(name, description, details, order, completed)
    
    def update_plan_step(self, step_id, **kwargs):
        """Update a plan step by ID."""
        return self.plan_manager.update_step(step_id, **kwargs)
    
    def toggle_plan_step(self, step_id):
        """Toggle the completion status of a plan step."""
        return self.plan_manager.toggle_step(step_id)
    
    def delete_plan_step(self, step_id):
        """Delete a plan step by ID."""
        return self.plan_manager.delete_step(step_id)
    
    def reorder_plan_steps(self):
        """Reorder plan steps to ensure consistent ordering."""
        return self.plan_manager.reorder_steps()
    
    # Notes methods
    def get_notes(self):
        """Get the notes."""
        return self.task_manager.get_notes()
    
    def save_notes(self, notes_text):
        """Save notes."""
        self.task_manager.save_notes(notes_text)
        return True
    
    # Data management
    def save_all(self):
        """Save all data to files."""
        self.task_manager.save_tasks()
        self.plan_manager.save_plan()
        return True
        
    def reload_all(self):
        """Reload all data from files (for external changes like MCP)."""
        self.task_manager.reload_tasks()
        self.task_manager.reload_notes()
        self.plan_manager.reload_plan()
        return True
    
    def export_data(self, file_path):
        """Export all data to a single JSON file."""
        import json
        data = {
            "tasks": self.get_all_tasks(),
            "plan": self.get_all_plan_steps(),
            "notes": self.get_notes()
        }
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    
    def import_data(self, file_path):
        """Import data from a JSON file."""
        import json
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Clear existing data
            self.task_manager.tasks = data.get("tasks", [])
            self.plan_manager.plan_steps = data.get("plan", [])
            
            # Import notes if available
            if "notes" in data:
                self.task_manager.save_notes(data["notes"])
            
            # Save imported data
            self.save_all()
            return True
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error importing data: {e}")
            return False