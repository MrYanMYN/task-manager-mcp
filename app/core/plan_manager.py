import json
import os
import uuid
from datetime import datetime


class PlanManager:
    def __init__(self, file_path=None):
        """Initialize the PlanManager with an optional file path."""
        if file_path is None:
            home_dir = os.path.expanduser("~")
            plan_dir = os.path.join(home_dir, ".tasktracker")
            os.makedirs(plan_dir, exist_ok=True)
            file_path = os.path.join(plan_dir, "plan.json")
        
        self.file_path = file_path
        self.plan_steps = self._load_plan()
    
    def _load_plan(self):
        """Load plan steps from the file or return an empty list if file doesn't exist."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                    # Ensure we always return a list
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and "steps" in data:
                        return data["steps"]
                    else:
                        # If it's not a list or doesn't have steps key, return empty list
                        return []
            except (json.JSONDecodeError, IOError):
                return []
        return []
        
    def reload_plan(self):
        """Reload plan steps from file (for external changes like MCP)."""
        self.plan_steps = self._load_plan()
    
    def save_plan(self):
        """Save plan steps to the file."""
        # Ensure plan_steps is a list before saving
        if not isinstance(self.plan_steps, list):
            self.plan_steps = []
            
        with open(self.file_path, 'w') as f:
            json.dump(self.plan_steps, f, indent=2)
    
    def get_all_steps(self):
        """Return all plan steps."""
        # Ensure we always return a list
        if not isinstance(self.plan_steps, list):
            self.plan_steps = []
        return self.plan_steps
    
    def get_step(self, step_id):
        """Get a plan step by ID."""
        # Ensure plan_steps is a list
        if not isinstance(self.plan_steps, list):
            self.plan_steps = []
            return None
            
        for step in self.plan_steps:
            if step["id"] == step_id:
                return step
        return None
    
    def add_step(self, name, description="", details="", order=None, completed=False):
        """Add a new plan step."""
        # Ensure plan_steps is a list
        if not isinstance(self.plan_steps, list):
            self.plan_steps = []
        
        if order is None:
            # Place at the end by default
            order = len(self.plan_steps)
        
        step = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "details": details,
            "order": order,
            "completed": completed,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Insert at the specified order
        self.plan_steps.append(step)
        self.reorder_steps()
        self.save_plan()
        return step
    
    def update_step(self, step_id, **kwargs):
        """Update a plan step by ID."""
        step = self.get_step(step_id)
        if step:
            for key, value in kwargs.items():
                if key in step and key not in ["id", "created_at"]:
                    step[key] = value
            step["updated_at"] = datetime.now().isoformat()
            
            # If order changed, reorder all steps
            if "order" in kwargs:
                self.reorder_steps()
                
            self.save_plan()
            return step
        return None
    
    def toggle_step(self, step_id):
        """Toggle the completion status of a plan step."""
        step = self.get_step(step_id)
        if step:
            step["completed"] = not step["completed"]
            step["updated_at"] = datetime.now().isoformat()
            self.save_plan()
            return step
        return None
    
    def delete_step(self, step_id):
        """Delete a plan step by ID."""
        # Ensure plan_steps is a list
        if not isinstance(self.plan_steps, list):
            self.plan_steps = []
            return False
            
        step = self.get_step(step_id)
        if step:
            self.plan_steps.remove(step)
            self.reorder_steps()
            self.save_plan()
            return True
        return False
    
    def reorder_steps(self):
        """Reorder steps to ensure consistent ordering."""
        # Ensure plan_steps is a list
        if not isinstance(self.plan_steps, list):
            self.plan_steps = []
            return
            
        # Sort by the current order
        self.plan_steps.sort(key=lambda x: x.get("order", 0))
        
        # Update order field to match actual position
        for i, step in enumerate(self.plan_steps):
            step["order"] = i