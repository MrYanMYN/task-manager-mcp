import curses
from enum import Enum

class FocusArea(Enum):
    TASKS = 0
    DETAILS = 1
    PLAN = 2
    NOTES = 3


class InputHandler:
    def __init__(self, terminal_ui):
        """Initialize the input handler with a reference to the terminal UI."""
        self.terminal_ui = terminal_ui
        self.focus = FocusArea.TASKS
    
    def handle_input(self, key):
        """
        Handle keyboard input and dispatch to appropriate handlers.
        Returns True if the application should continue, False if it should exit.
        """
        # If notes is in edit mode, we need special handling
        if self.focus == FocusArea.NOTES and self.terminal_ui.notes_win.edit_mode:
            # Escape exits edit mode in notes
            if key == 27:  # Escape
                self.terminal_ui.notes_win.toggle_edit_mode()
                self.terminal_ui.save_notes()
                return True
            
            # All other keys are processed by the notes window
            try:
                self.terminal_ui.notes_win.handle_key(key)
                return True
            except Exception as e:
                self.terminal_ui.show_message(f"Error in notes edit: {str(e)}")
                return True
        
        # Global keys (work in any context)
        if key == 27:  # Escape
            return self._handle_escape()
        elif key == 9:  # Tab
            self._cycle_focus()
            return True
        elif key == 24:  # Ctrl+X - toggle notes visibility (ASCII 24 is Ctrl+X)
            self.terminal_ui.toggle_notes_visibility()
            return True
        
        # Focus-specific input handling
        if self.focus == FocusArea.TASKS:
            return self._handle_tasks_input(key)
        elif self.focus == FocusArea.DETAILS:
            return self._handle_details_input(key)
        elif self.focus == FocusArea.PLAN:
            return self._handle_plan_input(key)
        elif self.focus == FocusArea.NOTES:
            return self._handle_notes_input(key)
        
        return True
    
    def _handle_escape(self):
        """Handle the escape key - confirm exit."""
        # Reset timeout to blocking for the confirmation dialog
        self.terminal_ui.stdscr.timeout(-1)
        
        confirm = self.terminal_ui.show_confirm_dialog(
            "Exit Confirmation", 
            "Are you sure you want to exit? Any unsaved changes will be lost."
        )
        return not confirm  # Return False to exit if confirmed
    
    def _cycle_focus(self):
        """Cycle through the focus areas."""
        focus_order = list(FocusArea)
        current_idx = focus_order.index(self.focus)
        
        # Skip Notes focus if it's not visible
        if not self.terminal_ui.notes_visible:
            # Create a filtered list without the NOTES enum
            focus_order = [f for f in focus_order if f != FocusArea.NOTES]
        
        # Find the next focus in our (potentially filtered) list
        next_idx = (focus_order.index(self.focus) + 1) % len(focus_order)
        self.focus = focus_order[next_idx]
        
        # Update UI with new focus
        self.terminal_ui.update_focus(self.focus)
        
        # Force a complete UI redraw to fix rendering artifacts
        self.terminal_ui._resize_layout()
    
    def _handle_tasks_input(self, key):
        """Handle input while focused on the task list."""
        if key == curses.KEY_UP:
            self.terminal_ui.task_list_win.select_prev()
            self._update_task_details()
        
        elif key == curses.KEY_DOWN:
            self.terminal_ui.task_list_win.select_next()
            self._update_task_details()
        
        elif key in (10, 13, curses.KEY_ENTER):  # Enter (different codes)
            # Toggle completion status when Enter is pressed
            self._toggle_selected_task()
            self._update_task_details()
        
        elif key == ord(' '):  # Space 
            # Toggle completion status when Space is pressed
            self._toggle_selected_task()
            self._update_task_details()
        
        elif key == ord('n'):  # New task
            self._new_task()
        
        elif key == ord('e'):  # Edit task
            self._edit_task()
        
        elif key == ord('d'):  # Delete task
            self._delete_task()
        
        return True
    
    def _handle_details_input(self, key):
        """Handle input while focused on the task details."""
        # There's not much to do in the details view except view
        # Maybe implement scrolling for long descriptions later
        return True
        
    def _handle_notes_input(self, key):
        """Handle input while focused on the notes."""
        if key == ord('e'):  # Edit notes
            self.terminal_ui.notes_win.toggle_edit_mode()
            return True
        
        return True
    
    def _handle_plan_input(self, key):
        """Handle input while focused on the project plan."""
        if key == curses.KEY_UP:
            self.terminal_ui.plan_win.select_prev()
        
        elif key == curses.KEY_DOWN:
            self.terminal_ui.plan_win.select_next()
        
        elif key in (10, 13, curses.KEY_ENTER):  # Enter (different codes)
            # Toggle completion when Enter is pressed
            self._toggle_plan_step()
        
        elif key == ord(' '):  # Toggle completion with Space
            self._toggle_plan_step()
        
        elif key == ord('d'):  # Toggle details view
            self.terminal_ui.plan_win.toggle_details()
        
        elif key == ord('n'):  # New plan step
            self._new_plan_step()
        
        elif key == ord('e'):  # Edit plan step
            self._edit_plan_step()
        
        elif key == ord('D'):  # Delete plan step (capital D to avoid conflict with details)
            self._delete_plan_step()
        
        return True
    
    def _update_task_details(self):
        """Update the task details window with the selected task."""
        task = self.terminal_ui.task_list_win.get_selected_task()
        self.terminal_ui.task_detail_win.set_task(task)
    
    def _new_task(self):
        """Create a new task."""
        prompts = ["Title", "Description", "Priority (1-3)"]
        values = self.terminal_ui.show_input_dialog("New Task", prompts)
        
        if values:
            title, description, priority_str = values
            
            # Validate priority
            try:
                priority = int(priority_str) if priority_str else 1
                if priority < 1 or priority > 3:
                    priority = 1
            except ValueError:
                priority = 1
            
            # Add the task
            task = self.terminal_ui.api.add_task(title, description, priority)
            
            # Refresh task list
            self.terminal_ui.refresh_tasks()
            
            # Find and select the new task
            tasks = self.terminal_ui.api.get_all_tasks()
            for i, t in enumerate(tasks):
                if t["id"] == task["id"]:
                    self.terminal_ui.task_list_win.selected_index = i
                    self.terminal_ui.task_list_win.adjust_selection()
                    self.terminal_ui.task_list_win.refresh_content()
                    self._update_task_details()
                    break
    
    def _edit_task(self):
        """Edit the selected task."""
        task = self.terminal_ui.task_list_win.get_selected_task()
        if not task:
            return
        
        # Set up the edit dialog with current values
        prompts = ["Title", "Description", "Priority (1-3)", "Status"]
        values = [
            task["title"],
            task["description"],
            str(task["priority"]),
            task["status"]
        ]
        
        new_values = self.terminal_ui.show_input_dialog("Edit Task", prompts, values)
        
        if new_values:
            title, description, priority_str, status = new_values
            
            # Validate priority
            try:
                priority = int(priority_str) if priority_str else task["priority"]
                if priority < 1 or priority > 3:
                    priority = task["priority"]
            except ValueError:
                priority = task["priority"]
            
            # Validate status
            valid_statuses = ["not_started", "in_progress", "completed"]
            if status not in valid_statuses:
                status = task["status"]
            
            # Update the task
            self.terminal_ui.api.update_task(
                task["id"],
                title=title,
                description=description,
                priority=priority,
                status=status
            )
            
            # Refresh task list and details
            self.terminal_ui.refresh_tasks()
            self._update_task_details()
    
    def _delete_task(self):
        """Delete the selected task."""
        task = self.terminal_ui.task_list_win.get_selected_task()
        if not task:
            return
        
        confirm = self.terminal_ui.show_confirm_dialog(
            "Delete Task",
            f"Are you sure you want to delete the task '{task['title']}'?"
        )
        
        if confirm:
            # Delete the task
            self.terminal_ui.api.delete_task(task["id"])
            
            # Refresh task list
            self.terminal_ui.refresh_tasks()
            self._update_task_details()
    
    def _new_plan_step(self):
        """Create a new plan step."""
        prompts = ["Name", "Description", "Details"]
        values = self.terminal_ui.show_input_dialog("New Plan Step", prompts)
        
        try:
            if values and values[0]:  # At least the name should be provided
                # Add the plan step
                name = values[0]
                description = values[1] if len(values) > 1 else ""
                details = values[2] if len(values) > 2 else ""
                
                step = self.terminal_ui.api.add_plan_step(
                    name=name,
                    description=description,
                    details=details
                )
                
                # Refresh plan
                self.terminal_ui.refresh_plan()
                
                # Only try to find and select the new step if it was successfully created
                if step and isinstance(step, dict) and "id" in step:
                    steps = self.terminal_ui.api.get_all_plan_steps()
                    for i, s in enumerate(steps):
                        if s["id"] == step["id"]:
                            self.terminal_ui.plan_win.selected_index = i
                            self.terminal_ui.plan_win.adjust_selection()
                            self.terminal_ui.plan_win.refresh_content()
                            break
        except Exception as e:
            self.terminal_ui.show_message(f"Error creating plan step: {str(e)}")
    
    def _edit_plan_step(self):
        """Edit the selected plan step."""
        step = self.terminal_ui.plan_win.get_selected_step()
        if not step:
            return
        
        # Set up the edit dialog with current values
        prompts = ["Name", "Description", "Details", "Order"]
        values = [
            step.get("name", step.get("description", "")),
            step.get("description", ""),
            step.get("details", ""),
            str(step.get("order", 0))
        ]
        
        new_values = self.terminal_ui.show_input_dialog("Edit Plan Step", prompts, values)
        
        if new_values:
            # Extract and validate values
            name = new_values[0] if len(new_values) > 0 else ""
            description = new_values[1] if len(new_values) > 1 else ""
            details = new_values[2] if len(new_values) > 2 else ""
            order_str = new_values[3] if len(new_values) > 3 else ""
            
            # Validate order
            try:
                order = int(order_str) if order_str else step.get("order", 0)
                if order < 0:
                    order = step.get("order", 0)
            except ValueError:
                order = step.get("order", 0)
            
            # Update the plan step
            self.terminal_ui.api.update_plan_step(
                step["id"],
                name=name,
                description=description,
                details=details,
                order=order
            )
            
            # Refresh plan
            self.terminal_ui.refresh_plan()
    
    def _delete_plan_step(self):
        """Delete the selected plan step."""
        step = self.terminal_ui.plan_win.get_selected_step()
        if not step:
            return
        
        confirm = self.terminal_ui.show_confirm_dialog(
            "Delete Plan Step",
            f"Are you sure you want to delete the plan step '{step['description']}'?"
        )
        
        if confirm:
            # Delete the plan step
            self.terminal_ui.api.delete_plan_step(step["id"])
            
            # Refresh plan
            self.terminal_ui.refresh_plan()
    
    def _toggle_selected_task(self):
        """Cycle through task statuses (not_started -> in_progress -> completed -> not_started)."""
        task = self.terminal_ui.task_list_win.get_selected_task()
        if not task:
            return
        
        # Cycle through the statuses
        current_status = task.get("status", "not_started")
        
        # If it's an old "pending" status, treat it as "not_started"
        if current_status == "pending":
            current_status = "not_started"
            
        status_cycle = {
            "not_started": "in_progress",
            "in_progress": "completed",
            "completed": "not_started"
        }
        
        new_status = status_cycle.get(current_status, "not_started")
        
        # Update the task
        self.terminal_ui.api.update_task(
            task["id"],
            status=new_status
        )
        
        # Refresh task list
        self.terminal_ui.refresh_tasks()
    
    def _toggle_plan_step(self):
        """Toggle the completion status of the selected plan step."""
        step = self.terminal_ui.plan_win.get_selected_step()
        if not step:
            return
        
        # Toggle the plan step
        self.terminal_ui.api.toggle_plan_step(step["id"])
        
        # Refresh plan
        self.terminal_ui.refresh_plan()