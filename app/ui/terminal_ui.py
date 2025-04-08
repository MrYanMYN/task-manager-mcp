import curses
import traceback
import os
import time

from app.ui.ui_components import TaskListWindow, TaskDetailWindow, PlanWindow, NotesWindow, InputDialog, ConfirmDialog
from app.ui.input_handler import InputHandler, FocusArea


class TerminalUI:
    def __init__(self, api):
        """Initialize the terminal UI with a reference to the API."""
        self.api = api
        self.stdscr = None
        self.task_list_win = None
        self.task_detail_win = None
        self.plan_win = None
        self.notes_win = None
        self.input_handler = None
        self.notes_visible = True  # Flag to control notes visibility
        
        # File modification tracking
        self.last_tasks_mtime = 0
        self.last_plan_mtime = 0
        self.last_notes_mtime = 0
        self.last_check_time = 0
        self.file_check_interval = 1.0  # Check for file changes every second
    
    def run(self):
        """Run the terminal UI."""
        try:
            # Start curses application
            curses.wrapper(self._main)
        except Exception as e:
            # If an error occurs, restore terminal and show traceback
            if self.stdscr:
                # Reset timeout to blocking before exiting to prevent potential issues
                self.stdscr.timeout(-1)
                curses.endwin()
            print(f"An error occurred: {str(e)}")
            traceback.print_exc()
    
    def _main(self, stdscr):
        """Main function for the curses application."""
        self.stdscr = stdscr
        
        # Set up curses
        curses.curs_set(0)  # Hide cursor
        stdscr.clear()
        
        # Set up input handler
        self.input_handler = InputHandler(self)
        
        # Create initial layout
        self._create_layout()
        
        # Initial data load
        try:
            self.refresh_tasks()
            self.refresh_plan()
            self.refresh_notes()
            
            # Initialize last modified times after initial load
            task_file = self.api.task_manager.file_path
            plan_file = self.api.plan_manager.file_path
            notes_file = self.api.task_manager.notes_file_path
            
            if os.path.exists(task_file):
                self.last_tasks_mtime = os.path.getmtime(task_file)
            if os.path.exists(plan_file):
                self.last_plan_mtime = os.path.getmtime(plan_file)
            if os.path.exists(notes_file):
                self.last_notes_mtime = os.path.getmtime(notes_file)
                
            self.last_check_time = time.time()
            
        except Exception as e:
            self.show_message(f"Error loading data: {str(e)}")
        
        # Main event loop
        while True:
            # Check for external file changes (e.g., from MCP)
            self.check_file_changes()
            
            # Update the screen
            stdscr.refresh()
            
            # Configure timeout for getch to allow polling for file changes
            stdscr.timeout(100)  # 100ms timeout
            
            # Get input (returns -1 if no input available)
            key = stdscr.getch()
            
            # Reset timeout to blocking mode if we actually got a key
            if key != -1:
                stdscr.timeout(-1)
                # Handle input (exit if handler returns False)
                if not self.input_handler.handle_input(key):
                    break
            else:
                # No input, just continue the loop to check for file changes
                continue
    
    def _create_layout(self):
        """Create the initial window layout."""
        screen_height, screen_width = self.stdscr.getmaxyx()
        
        # Calculate dimensions for initial layout
        top_height = screen_height // 2
        main_width = screen_width - 30  # Reserve 30 cols for notes on the right
        task_width = main_width // 2
        detail_width = main_width - task_width
        plan_height = screen_height - top_height
        notes_width = screen_width - main_width
        
        # Create windows
        self.task_list_win = TaskListWindow(
            self.stdscr, top_height, task_width, 0, 0, "Tasks"
        )
        
        self.task_detail_win = TaskDetailWindow(
            self.stdscr, top_height, detail_width, 0, task_width, "Task Details"
        )
        
        self.plan_win = PlanWindow(
            self.stdscr, plan_height, main_width, top_height, 0, "Project Plan"
        )
        
        self.notes_win = NotesWindow(
            self.stdscr, screen_height, notes_width, 0, main_width, "Notes"
        )
        
        # Initial refresh
        self.task_list_win.refresh()
        self.task_detail_win.refresh()
        self.plan_win.refresh()
        
        if self.notes_visible:
            self.notes_win.refresh()
    
    def toggle_notes_visibility(self):
        """Toggle the visibility of the notes window."""
        self.notes_visible = not self.notes_visible
        
        # If hiding and notes is the active focus, change focus to tasks
        if not self.notes_visible and self.input_handler.focus == FocusArea.NOTES:
            self.input_handler.focus = FocusArea.TASKS
            self.update_focus(FocusArea.TASKS)
        
        # Redraw layout (this will resize all windows accordingly)
        self._resize_layout()
        
        # If notes are hidden, make sure we redraw all other windows
        if not self.notes_visible:
            # Ensure each window is refreshed with its contents
            self.task_list_win.refresh_content()
            self.task_detail_win.refresh_content()
            self.plan_win.refresh_content()
            
            # Refresh the stdscr to ensure proper redraw of everything
            self.stdscr.refresh()
            
        return self.notes_visible
    
    def _resize_layout(self):
        """Resize the window layout."""
        screen_height, screen_width = self.stdscr.getmaxyx()
        
        # Calculate dimensions based on notes visibility
        if self.notes_visible:
            main_width = screen_width - 30  # Reserve 30 cols for notes on the right
            notes_width = screen_width - main_width
        else:
            main_width = screen_width  # Use full width when notes are hidden
            notes_width = 0
            
        top_height = screen_height // 2
        task_width = main_width // 2
        detail_width = main_width - task_width
        plan_height = screen_height - top_height
        
        # Resize windows
        self.task_list_win.resize(top_height, task_width, 0, 0)
        self.task_detail_win.resize(top_height, detail_width, 0, task_width)
        self.plan_win.resize(plan_height, main_width, top_height, 0)
        
        # Only resize notes window if visible
        if self.notes_visible:
            self.notes_win.resize(screen_height, notes_width, 0, main_width)
        
        # Refresh content
        self.task_list_win.refresh_content()
        self.task_detail_win.refresh_content()
        self.plan_win.refresh_content()
        
        # Only refresh notes if visible
        if self.notes_visible:
            self.notes_win.refresh_content()
    
    def refresh_tasks(self):
        """Refresh task list and details."""
        tasks = self.api.get_all_tasks()
        
        # Sort tasks by priority (high to low) and then by status
        tasks.sort(key=lambda x: (-x['priority'], x['status']))
        
        self.task_list_win.set_tasks(tasks)
        
        # Update task details if there's a selected task
        selected_task = self.task_list_win.get_selected_task()
        self.task_detail_win.set_task(selected_task)
    
    def refresh_plan(self):
        """Refresh the project plan."""
        try:
            steps = self.api.get_all_plan_steps()
            
            # Validate steps before setting them
            if steps is None:
                steps = []
                
            # Steps are already sorted by order in the API
            self.plan_win.set_steps(steps)
        except Exception as e:
            # Handle errors gracefully
            self.plan_win.set_steps([])
            raise Exception(f"Failed to load plan: {str(e)}")
    
    def refresh_notes(self):
        """Load and refresh the notes content."""
        notes = self.api.get_notes()
        self.notes_win.set_notes(notes)
    
    def save_notes(self):
        """Save the current notes content."""
        notes_text = self.notes_win.get_notes()
        self.api.save_notes(notes_text)
        
    def check_file_changes(self):
        """Check if any data files have been modified externally (like by MCP)."""
        current_time = time.time()
        
        # Only check periodically to reduce file system access
        if current_time - self.last_check_time < self.file_check_interval:
            return False
            
        self.last_check_time = current_time
        changes_detected = False
        
        # Get file paths from the API's managers
        task_file = self.api.task_manager.file_path
        plan_file = self.api.plan_manager.file_path
        notes_file = self.api.task_manager.notes_file_path
        
        # Check if any data files have been modified
        tasks_changed = os.path.exists(task_file) and os.path.getmtime(task_file) > self.last_tasks_mtime
        plan_changed = os.path.exists(plan_file) and os.path.getmtime(plan_file) > self.last_plan_mtime
        notes_changed = os.path.exists(notes_file) and os.path.getmtime(notes_file) > self.last_notes_mtime
        
        if tasks_changed or plan_changed or notes_changed:
            # Update last modified times
            if tasks_changed:
                self.last_tasks_mtime = os.path.getmtime(task_file)
            if plan_changed:
                self.last_plan_mtime = os.path.getmtime(plan_file)
            if notes_changed:
                self.last_notes_mtime = os.path.getmtime(notes_file)
            
            # Reload all data from files
            self.api.reload_all()
            
            # Refresh UI components
            self.refresh_tasks()
            self.refresh_plan()
            self.refresh_notes()
            
            changes_detected = True
                
        return changes_detected
    
    def update_focus(self, focus):
        """Update the UI focus."""
        # Reset all titles first
        self.task_list_win.set_title("Tasks")
        self.task_detail_win.set_title("Task Details")
        self.plan_win.set_title("Project Plan")
        if self.notes_visible:
            self.notes_win.set_title("Notes")
        
        # Highlight the active window by changing its title
        if focus == FocusArea.TASKS:
            self.task_list_win.set_title("Tasks [Active]")
        elif focus == FocusArea.DETAILS:
            self.task_detail_win.set_title("Task Details [Active]")
        elif focus == FocusArea.PLAN:
            self.plan_win.set_title("Project Plan [Active]")
        elif focus == FocusArea.NOTES and self.notes_visible:
            self.notes_win.set_title("Notes [Active]")
        
        # Clear screen to remove artifacts
        self.stdscr.erase()
        self.stdscr.refresh()
        
        # Refresh the content of all windows
        self.task_list_win.refresh_content()
        self.task_detail_win.refresh_content()
        self.plan_win.refresh_content()
        
        # Only refresh notes if visible
        if self.notes_visible:
            self.notes_win.refresh_content()
    
    def show_input_dialog(self, title, prompts, initial_values=None):
        """Show an input dialog and return the entered values or None if canceled."""
        dialog = InputDialog(self.stdscr, title, prompts, initial_values)
        result = dialog.show()
        
        # Redraw the entire screen after dialog closes
        self.stdscr.clear()
        self.stdscr.refresh()
        self._resize_layout()
        
        return result
    
    def show_confirm_dialog(self, title, message):
        """Show a confirmation dialog and return True if confirmed, False otherwise."""
        dialog = ConfirmDialog(self.stdscr, title, message)
        result = dialog.show()
        
        # Redraw the entire screen after dialog closes
        self.stdscr.clear()
        self.stdscr.refresh()
        self._resize_layout()
        
        return result
    
    def show_message(self, message):
        """Show a temporary message at the bottom of the screen."""
        screen_height, screen_width = self.stdscr.getmaxyx()
        
        # Create a small window for the message
        msg_height = 3
        msg_width = min(len(message) + 4, screen_width - 4)
        msg_y = (screen_height - msg_height) // 2
        msg_x = (screen_width - msg_width) // 2
        
        # Create message window
        msg_win = self.stdscr.subwin(msg_height, msg_width, msg_y, msg_x)
        msg_win.box()
        msg_win.addstr(1, 2, message[:msg_width - 4])
        msg_win.addstr(msg_height - 1, 2, "Press any key to continue")
        msg_win.refresh()
        
        # Wait for a key press
        self.stdscr.getch()
        
        # Redraw the entire screen
        self.stdscr.clear()
        self.stdscr.refresh()
        self._resize_layout()