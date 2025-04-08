import curses

class Window:
    def __init__(self, stdscr, height, width, y, x, title=""):
        """Initialize a window with a border and optional title."""
        self.win = stdscr.subwin(height, width, y, x)
        self.height = height
        self.width = width
        self.title = title
        self.win.box()
        self.set_title(title)
        self.content_window = self.win.derwin(height - 2, width - 2, 1, 1)
        self.selected_index = 0
        self.scroll_offset = 0
        self.max_visible_items = height - 2
    
    def set_title(self, title):
        """Set the window title."""
        self.title = title
        if title:
            title_str = f" {title} "
            x = max(1, (self.width - len(title_str)) // 2)
            self.win.addstr(0, x, title_str)
    
    def clear(self):
        """Clear the content window."""
        self.content_window.clear()
    
    def refresh(self):
        """Refresh the window and its content."""
        self.win.box()
        self.set_title(self.title)
        self.win.refresh()
        self.content_window.refresh()
    
    def get_content_dimensions(self):
        """Get the usable dimensions of the content window."""
        return self.height - 2, self.width - 2
    
    def resize(self, height, width, y, x):
        """Resize and move the window."""
        self.height = height
        self.width = width
        self.win.resize(height, width)
        self.win.mvwin(y, x)
        self.content_window = self.win.derwin(height - 2, width - 2, 1, 1)
        self.max_visible_items = height - 2
        self.refresh()
    
    def display_message(self, message):
        """Display a message in the content window."""
        self.clear()
        self.content_window.addstr(0, 0, message)
        self.refresh()


class TaskListWindow(Window):
    def __init__(self, stdscr, height, width, y, x, title="Tasks"):
        """Initialize a task list window."""
        super().__init__(stdscr, height, width, y, x, title)
        self.tasks = []
    
    def set_tasks(self, tasks):
        """Set the tasks to display."""
        self.tasks = tasks
        self.adjust_selection()
        self.refresh_content()
    
    def adjust_selection(self):
        """Adjust selection index and scroll offset to valid values."""
        if not self.tasks:
            self.selected_index = 0
            self.scroll_offset = 0
            return
        
        # Ensure selected_index is in valid range
        if self.selected_index >= len(self.tasks):
            self.selected_index = len(self.tasks) - 1
        
        # Adjust scroll offset to keep selected item visible
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.max_visible_items:
            self.scroll_offset = self.selected_index - self.max_visible_items + 1
    
    def refresh_content(self):
        """Refresh the task list content."""
        self.clear()
        content_height, content_width = self.get_content_dimensions()
        
        if not self.tasks:
            self.content_window.addstr(0, 0, "No tasks")
            self.refresh()
            return
        
        # Display visible tasks
        for i in range(min(self.max_visible_items, len(self.tasks))):
            idx = i + self.scroll_offset
            if idx >= len(self.tasks):
                break
            
            task = self.tasks[idx]
            
            # Highlight selected task
            if idx == self.selected_index:
                self.content_window.attron(curses.A_REVERSE)
            
            # Format priority indicator
            priority_markers = ["!", "!!", "!!!"]
            priority_str = priority_markers[task['priority'] - 1] if 1 <= task['priority'] <= 3 else ""
            
            # Format status with icons
            status_map = {
                "not_started": "[ ]",  # Empty square
                "in_progress": "[→]",  # Arrow (in progress)
                "completed": "[✓]",    # Checkmark
                # For backward compatibility
                "pending": "[ ]"
            }
            status_str = status_map.get(task['status'], "[ ]")
            
            # Truncate title if needed
            max_title_width = content_width - len(priority_str) - len(status_str) - 2
            title = task['title']
            if len(title) > max_title_width:
                title = title[:max_title_width-3] + "..."
            
            # Display task line
            task_str = f"{status_str} {title} {priority_str}"
            self.content_window.addstr(i, 0, task_str)
            
            if idx == self.selected_index:
                self.content_window.attroff(curses.A_REVERSE)
        
        self.refresh()
    
    def select_next(self):
        """Select the next task if available."""
        if self.tasks and self.selected_index < len(self.tasks) - 1:
            self.selected_index += 1
            self.adjust_selection()
            self.refresh_content()
    
    def select_prev(self):
        """Select the previous task if available."""
        if self.tasks and self.selected_index > 0:
            self.selected_index -= 1
            self.adjust_selection()
            self.refresh_content()
    
    def get_selected_task(self):
        """Get the currently selected task."""
        if self.tasks and 0 <= self.selected_index < len(self.tasks):
            return self.tasks[self.selected_index]
        return None


class TaskDetailWindow(Window):
    def __init__(self, stdscr, height, width, y, x, title="Task Details"):
        """Initialize a task detail window."""
        super().__init__(stdscr, height, width, y, x, title)
        self.task = None
    
    def set_task(self, task):
        """Set the task to display details for."""
        self.task = task
        self.refresh_content()
    
    def refresh_content(self):
        """Refresh the task detail content."""
        self.clear()
        
        if not self.task:
            self.content_window.addstr(0, 0, "No task selected")
            self.refresh()
            return
        
        # Display task properties
        content_height, content_width = self.get_content_dimensions()
        
        # Map priority and status to more readable forms
        priority_map = {1: "Low", 2: "Medium", 3: "High"}
        status_map = {
            "not_started": "Not Started",
            "in_progress": "In Progress",
            "completed": "Completed",
            # For backward compatibility
            "pending": "Not Started"
        }
        
        priority = priority_map.get(self.task['priority'], "Unknown")
        status = status_map.get(self.task['status'], "Unknown")
        
        # Display task details
        y = 0
        self.content_window.addstr(y, 0, f"Title: {self.task['title']}")
        y += 2
        
        self.content_window.addstr(y, 0, f"Status: {status}")
        y += 1
        self.content_window.addstr(y, 0, f"Priority: {priority}")
        y += 2
        
        # Display description with word wrapping
        self.content_window.addstr(y, 0, "Description:")
        y += 1
        
        description = self.task['description'] or "No description provided."
        words = description.split()
        
        if words:
            line = ""
            for word in words:
                # Check if adding this word would exceed width
                if len(line) + len(word) + 1 > content_width:
                    self.content_window.addstr(y, 0, line)
                    y += 1
                    line = word
                else:
                    if line:
                        line += " " + word
                    else:
                        line = word
            
            # Add the last line if it has content
            if line:
                self.content_window.addstr(y, 0, line)
                y += 1
        
        # Display created/updated timestamps
        y += 1
        created = self.task.get('created_at', '').split('T')[0]
        updated = self.task.get('updated_at', '').split('T')[0]
        
        if created:
            self.content_window.addstr(y, 0, f"Created: {created}")
            y += 1
        if updated and updated != created:
            self.content_window.addstr(y, 0, f"Updated: {updated}")
        
        self.refresh()


class NotesWindow(Window):
    def __init__(self, stdscr, height, width, y, x, title="Notes"):
        """Initialize a notes window."""
        super().__init__(stdscr, height, width, y, x, title)
        self.notes = ""
        self.edit_mode = False
        self.cursor_pos = 0
        self.scroll_offset = 0
        
        # Enable keypad for special key handling
        self.content_window.keypad(True)
    
    def set_notes(self, notes):
        """Set the notes to display."""
        self.notes = notes if notes else ""
        self.refresh_content()
    
    def get_notes(self):
        """Get the current notes."""
        return self.notes
    
    def toggle_edit_mode(self):
        """Toggle between view and edit mode."""
        self.edit_mode = not self.edit_mode
        if self.edit_mode:
            curses.curs_set(1)  # Show cursor
        else:
            curses.curs_set(0)  # Hide cursor
        self.refresh_content()
        return self.edit_mode
    
    def handle_key(self, key):
        """Handle keyboard input in edit mode."""
        if not self.edit_mode:
            return False
        
        try:
            # Simple key handling - safer approach
            if key in (10, 13, curses.KEY_ENTER):  # Enter
                # Add a newline at end for simplicity
                self.notes += "\n"
                
            elif key in (curses.KEY_BACKSPACE, 127, 8):  # Backspace
                # Remove last character if there are any
                if len(self.notes) > 0:
                    self.notes = self.notes[:-1]
                    
            elif 32 <= key <= 126:  # Printable ASCII characters
                # Add character to the end
                self.notes += chr(key)
            
            # Refresh after any change
            self.refresh_content()
            return True
            
        except Exception as e:
            # Log error by adding to notes
            self.notes += f"\nError: {str(e)}\n"
            self.refresh_content()
            return True
    
    def adjust_scroll(self):
        """Adjust scroll offset to keep cursor visible."""
        content_height, content_width = self.get_content_dimensions()
        
        # Count lines up to cursor
        lines_to_cursor = self.notes[:self.cursor_pos].count('\n')
        
        # Adjust scroll if cursor is off screen
        if lines_to_cursor < self.scroll_offset:
            self.scroll_offset = lines_to_cursor
        elif lines_to_cursor >= self.scroll_offset + content_height:
            self.scroll_offset = lines_to_cursor - content_height + 1
    
    def refresh_content(self):
        """Refresh the notes content."""
        try:
            self.clear()
            content_height, content_width = self.get_content_dimensions()
            
            # Simplified content display
            if not self.notes:
                if self.edit_mode:
                    self.content_window.addstr(0, 0, "Type to add notes...")
                else:
                    self.content_window.addstr(0, 0, "No notes. Press 'e' to edit.")
            else:
                # Just display the most recent part of notes (last few lines)
                lines = self.notes.split('\n')
                
                # Display only what fits in the window
                max_lines = min(content_height - 1, len(lines))
                start_line = max(0, len(lines) - max_lines)
                
                for i in range(max_lines):
                    line_idx = start_line + i
                    if line_idx < len(lines):
                        # Truncate line if needed
                        display_line = lines[line_idx]
                        if len(display_line) > content_width - 1:
                            display_line = display_line[:content_width - 1]
                        
                        self.content_window.addstr(i, 0, display_line)
            
            # Add help text at bottom
            if self.edit_mode and content_height > 1:
                help_text = "Esc: Save & exit edit mode"
                if len(help_text) > content_width - 1:
                    help_text = help_text[:content_width - 1]
                self.content_window.addstr(content_height - 1, 0, help_text)
                
            # In edit mode, position cursor at the end of content
            if self.edit_mode:
                # Count displayed lines to find end position
                line_count = min(max_lines if 'max_lines' in locals() else 0, content_height - 1)
                if line_count > 0:
                    self.content_window.move(line_count - 1, 0)
                else:
                    self.content_window.move(0, 0)
            
            self.refresh()
        except Exception as e:
            # If there's an error, try a minimal refresh
            try:
                self.clear()
                self.content_window.addstr(0, 0, "Notes")
                self.refresh()
            except:
                pass


class PlanWindow(Window):
    def __init__(self, stdscr, height, width, y, x, title="Project Plan"):
        """Initialize a project plan window."""
        super().__init__(stdscr, height, width, y, x, title)
        self.steps = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.show_details = False  # Flag to control if details are shown
    
    def set_steps(self, steps):
        """Set the plan steps to display."""
        self.steps = steps
        self.adjust_selection()
        self.refresh_content()
    
    def adjust_selection(self):
        """Adjust selection index and scroll offset to valid values."""
        if not self.steps:
            self.selected_index = 0
            self.scroll_offset = 0
            return
        
        # Ensure selected_index is in valid range
        if self.selected_index < 0:
            self.selected_index = 0
        elif self.selected_index >= len(self.steps):
            self.selected_index = max(0, len(self.steps) - 1)
        
        # Adjust scroll offset to keep selected item visible
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.max_visible_items:
            self.scroll_offset = max(0, self.selected_index - self.max_visible_items + 1)
    
    def refresh_content(self):
        """Refresh the plan content."""
        self.clear()
        content_height, content_width = self.get_content_dimensions()
        
        if not self.steps:
            self.content_window.addstr(0, 0, "No plan steps")
            self.refresh()
            return
            
        selected_step = self.get_selected_step()
        
        # If showing details for the selected step
        if self.show_details and selected_step:
            self._display_step_details(selected_step, content_height, content_width)
            return
            
        # Otherwise display the list of steps
        list_height = min(content_height, len(self.steps))
        
        # Display visible steps
        for i in range(min(self.max_visible_items, len(self.steps))):
            idx = i + self.scroll_offset
            if idx >= len(self.steps):
                break
            
            try:
                step = self.steps[idx]
                
                # Highlight selected step
                if idx == self.selected_index:
                    self.content_window.attron(curses.A_REVERSE)
                
                # Format step with order and completion status
                completion_status = "[✓]" if step['completed'] else "[ ]"
                
                # Get name or fallback to description for backward compatibility
                name = step.get('name', step.get('description', 'Unnamed step'))
                
                # Truncate name if needed
                max_name_width = content_width - 10
                if len(name) > max_name_width:
                    name = name[:max_name_width-3] + "..."
                
                # Display step line with safe index access
                order = step.get('order', 0)
                step_str = f"{order + 1:2d}. {completion_status} {name}"
                self.content_window.addstr(i, 0, step_str)
                
                if idx == self.selected_index:
                    self.content_window.attroff(curses.A_REVERSE)
            except (IndexError, KeyError) as e:
                # Handle any index errors gracefully
                self.content_window.addstr(i, 0, f"Error displaying step: {str(e)}")
                
        # Add a help line at the bottom if there's space
        if content_height > list_height + 1:
            help_text = "Enter/Space: Toggle completion | D: Show/hide details"
            self.content_window.addstr(content_height - 1, 0, help_text)
            
        self.refresh()
        
    def _display_step_details(self, step, height, width):
        """Display detailed information for a plan step."""
        y = 0
        
        # Display step name
        name = step.get('name', 'Unnamed step')
        self.content_window.addstr(y, 0, f"Name: {name}")
        y += 2
        
        # Display completion status
        completed = "Completed" if step.get('completed', False) else "Not completed"
        self.content_window.addstr(y, 0, f"Status: {completed}")
        y += 2
        
        # Display description
        description = step.get('description', '')
        if description:
            self.content_window.addstr(y, 0, "Description:")
            y += 1
            
            # Word wrap description
            words = description.split()
            line = ""
            for word in words:
                if len(line) + len(word) + 1 > width:
                    self.content_window.addstr(y, 0, line)
                    y += 1
                    line = word
                else:
                    if line:
                        line += " " + word
                    else:
                        line = word
            
            if line:
                self.content_window.addstr(y, 0, line)
                y += 1
            
            y += 1
        
        # Display detailed information
        details = step.get('details', '')
        if details:
            self.content_window.addstr(y, 0, "Details:")
            y += 1
            
            # Word wrap details
            words = details.split()
            line = ""
            for word in words:
                if len(line) + len(word) + 1 > width:
                    self.content_window.addstr(y, 0, line)
                    y += 1
                    line = word
                else:
                    if line:
                        line += " " + word
                    else:
                        line = word
            
            if line:
                self.content_window.addstr(y, 0, line)
                y += 1
        
        # Add a help line at the bottom
        help_text = "D: Return to plan list"
        self.content_window.addstr(height - 1, 0, help_text)
        
        self.refresh()
    
    def select_next(self):
        """Select the next step if available."""
        if self.steps and self.selected_index < len(self.steps) - 1:
            self.selected_index += 1
            self.adjust_selection()
            self.refresh_content()
    
    def select_prev(self):
        """Select the previous step if available."""
        if self.steps and self.selected_index > 0:
            self.selected_index -= 1
            self.adjust_selection()
            self.refresh_content()
    
    def get_selected_step(self):
        """Get the currently selected plan step."""
        try:
            if self.steps and 0 <= self.selected_index < len(self.steps):
                return self.steps[self.selected_index]
        except (IndexError, KeyError):
            pass
        return None
        
    def toggle_details(self):
        """Toggle between displaying the step list and the details of the selected step."""
        if self.get_selected_step():
            self.show_details = not self.show_details
            self.refresh_content()
            return True
        return False


class InputDialog:
    def __init__(self, stdscr, title, prompts, initial_values=None):
        """
        Initialize an input dialog with multiple fields.
        
        Args:
            stdscr: The main curses window
            title: Dialog title
            prompts: List of field prompts
            initial_values: List of initial values for fields (optional)
        """
        self.stdscr = stdscr
        self.title = title
        self.prompts = prompts
        
        # Initialize with empty values or provided initial values
        if initial_values is None:
            self.values = ["" for _ in range(len(prompts))]
        else:
            self.values = initial_values.copy()
        
        # Dialog dimensions
        screen_height, screen_width = stdscr.getmaxyx()
        self.width = min(60, screen_width - 4)
        self.height = len(prompts) * 2 + 4  # 2 lines per field + borders + buttons
        
        # Center dialog
        self.y = (screen_height - self.height) // 2
        self.x = (screen_width - self.width) // 2
        
        # Create window
        self.win = stdscr.subwin(self.height, self.width, self.y, self.x)
        self.win.keypad(True)  # Enable keypad mode for special keys
        self.current_field = 0
        self.cursor_pos = len(self.values[0]) if self.values and self.values[0] else 0
    
    def show(self):
        """Show the dialog and handle input."""
        curses.curs_set(1)  # Show cursor
        
        # Enable special keys like backspace
        self.win.keypad(True)
        
        # Main input loop
        while True:
            self.draw()
            key = self.win.getch()
            
            if key == curses.KEY_ENTER or key == 10 or key == 13:  # Enter (different codes)
                curses.curs_set(0)  # Hide cursor
                return self.values
            
            elif key == 27:  # Escape
                curses.curs_set(0)  # Hide cursor
                return None
            
            elif key == curses.KEY_UP and self.current_field > 0:
                self.current_field -= 1
                self.cursor_pos = len(self.values[self.current_field])
            
            elif key == curses.KEY_DOWN and self.current_field < len(self.prompts) - 1:
                self.current_field += 1
                self.cursor_pos = len(self.values[self.current_field])
            
            elif key == 9:  # Tab
                self.current_field = (self.current_field + 1) % len(self.prompts)
                self.cursor_pos = len(self.values[self.current_field])
            
            elif key == curses.KEY_LEFT and self.cursor_pos > 0:
                self.cursor_pos -= 1
            
            elif key == curses.KEY_RIGHT and self.cursor_pos < len(self.values[self.current_field]):
                self.cursor_pos += 1
            
            elif key in (curses.KEY_BACKSPACE, 127, 8):  # Different backspace codes
                if self.cursor_pos > 0:
                    self.values[self.current_field] = (
                        self.values[self.current_field][:self.cursor_pos - 1] + 
                        self.values[self.current_field][self.cursor_pos:]
                    )
                    self.cursor_pos -= 1
            
            elif key == curses.KEY_DC:  # Delete
                if self.cursor_pos < len(self.values[self.current_field]):
                    self.values[self.current_field] = (
                        self.values[self.current_field][:self.cursor_pos] + 
                        self.values[self.current_field][self.cursor_pos + 1:]
                    )
            
            elif 32 <= key <= 126:  # Printable characters
                self.values[self.current_field] = (
                    self.values[self.current_field][:self.cursor_pos] + 
                    chr(key) + 
                    self.values[self.current_field][self.cursor_pos:]
                )
                self.cursor_pos += 1
    
    def draw(self):
        """Draw the dialog box and input fields."""
        self.win.clear()
        self.win.box()
        
        # Draw title
        if self.title:
            title_str = f" {self.title} "
            x = max(1, (self.width - len(title_str)) // 2)
            self.win.addstr(0, x, title_str)
        
        # Draw input fields
        for i, prompt in enumerate(self.prompts):
            y = i * 2 + 1
            self.win.addstr(y, 2, f"{prompt}:")
            
            # Draw input field
            field_x = 2
            field_y = y + 1
            field_width = self.width - 4
            field_value = self.values[i]
            
            # Draw input value
            self.win.addstr(field_y, field_x, field_value)
            
            # Draw cursor if this is the active field
            if i == self.current_field:
                self.win.move(field_y, field_x + self.cursor_pos)
        
        # Draw instructions
        self.win.addstr(self.height - 1, 2, "Enter: Save | Esc: Cancel")
        
        self.win.refresh()


class ConfirmDialog:
    def __init__(self, stdscr, title, message):
        """Initialize a confirmation dialog."""
        self.stdscr = stdscr
        self.title = title
        self.message = message
        
        # Dialog dimensions
        screen_height, screen_width = stdscr.getmaxyx()
        self.width = min(50, screen_width - 4)
        
        # Calculate height based on message length
        message_lines = (len(message) // (self.width - 4)) + 1
        self.height = message_lines + 4  # Message + borders + buttons
        
        # Center dialog
        self.y = (screen_height - self.height) // 2
        self.x = (screen_width - self.width) // 2
        
        # Create window
        self.win = stdscr.subwin(self.height, self.width, self.y, self.x)
        self.selected = 0  # 0 = No, 1 = Yes
    
    def show(self):
        """Show the dialog and handle input."""
        # Enable keypad mode for special keys
        self.win.keypad(True)
        
        # Main input loop
        while True:
            self.draw()
            key = self.win.getch()
            
            if key == curses.KEY_ENTER or key == 10 or key == 13:  # Enter (different codes)
                return self.selected == 1  # Return True if "Yes" selected
            
            elif key == 27:  # Escape
                return False
            
            elif key == curses.KEY_LEFT or key == curses.KEY_RIGHT:
                self.selected = 1 - self.selected  # Toggle between 0 and 1
                
            # Add handling for y/n keys
            elif key in (ord('y'), ord('Y')):
                return True
                
            elif key in (ord('n'), ord('N')):
                return False
    
    def draw(self):
        """Draw the confirmation dialog."""
        self.win.clear()
        self.win.box()
        
        # Draw title
        if self.title:
            title_str = f" {self.title} "
            x = max(1, (self.width - len(title_str)) // 2)
            self.win.addstr(0, x, title_str)
        
        # Draw message
        message_words = self.message.split()
        line = ""
        y = 1
        
        for word in message_words:
            if len(line) + len(word) + 1 <= self.width - 4:
                if line:
                    line += " " + word
                else:
                    line = word
            else:
                self.win.addstr(y, 2, line)
                y += 1
                line = word
        
        if line:
            self.win.addstr(y, 2, line)
        
        # Draw buttons
        button_y = self.height - 2
        no_x = self.width // 3 - 2
        yes_x = 2 * self.width // 3 - 2
        
        if self.selected == 0:
            self.win.attron(curses.A_REVERSE)
        self.win.addstr(button_y, no_x, " No ")
        if self.selected == 0:
            self.win.attroff(curses.A_REVERSE)
        
        if self.selected == 1:
            self.win.attron(curses.A_REVERSE)
        self.win.addstr(button_y, yes_x, " Yes ")
        if self.selected == 1:
            self.win.attroff(curses.A_REVERSE)
        
        self.win.refresh()