import json
import os
import uuid
from datetime import datetime


class TaskManager:
    def __init__(self, file_path=None, notes_file_path=None):
        """Initialize the TaskManager with optional file paths."""
        home_dir = os.path.expanduser("~")
        task_dir = os.path.join(home_dir, ".tasktracker")
        os.makedirs(task_dir, exist_ok=True)
        
        if file_path is None:
            file_path = os.path.join(task_dir, "tasks.json")
        
        if notes_file_path is None:
            notes_file_path = os.path.join(task_dir, "notes.txt")
            
        self.file_path = file_path
        self.notes_file_path = notes_file_path
        self.tasks = self._load_tasks()
        self.notes = self._load_notes()
    
    def _load_tasks(self):
        """Load tasks from the file or return an empty list if file doesn't exist."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []
        
    def reload_tasks(self):
        """Reload tasks from file (for external changes like MCP)."""
        self.tasks = self._load_tasks()
    
    def _load_notes(self):
        """Load notes from file or return empty string if file doesn't exist."""
        if os.path.exists(self.notes_file_path):
            try:
                with open(self.notes_file_path, 'r') as f:
                    return f.read()
            except:
                return ""
        return ""
        
    def reload_notes(self):
        """Reload notes from file (for external changes like MCP)."""
        self.notes = self._load_notes()
    
    def save_tasks(self):
        """Save tasks to the file."""
        with open(self.file_path, 'w') as f:
            json.dump(self.tasks, f, indent=2)
            
    def save_notes(self, notes_text):
        """Save notes to the file."""
        self.notes = notes_text
        with open(self.notes_file_path, 'w') as f:
            f.write(notes_text)
            
    def get_notes(self):
        """Get the current notes."""
        return self.notes
    
    def get_all_tasks(self):
        """Return all tasks."""
        return self.tasks
    
    def get_task(self, task_id):
        """Get a task by ID."""
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None
    
    def add_task(self, title, description="", priority=1, status="not_started"):
        """Add a new task."""
        # Validate status
        valid_statuses = ["not_started", "in_progress", "completed"]
        if status not in valid_statuses:
            status = "not_started"
            
        task = {
            "id": str(uuid.uuid4()),
            "title": title,
            "description": description,
            "priority": priority,
            "status": status,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        self.tasks.append(task)
        self.save_tasks()
        return task
    
    def update_task(self, task_id, **kwargs):
        """Update a task by ID."""
        task = self.get_task(task_id)
        if task:
            for key, value in kwargs.items():
                if key in task and key not in ["id", "created_at"]:
                    task[key] = value
            task["updated_at"] = datetime.now().isoformat()
            self.save_tasks()
            return task
        return None
    
    def delete_task(self, task_id):
        """Delete a task by ID."""
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            self.save_tasks()
            return True
        return False