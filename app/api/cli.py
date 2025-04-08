import argparse
import sys
import os

from app.api.api import TaskTrackerAPI
from app.core.task_manager import TaskManager
from app.core.plan_manager import PlanManager


def create_parser():
    """Create the command line argument parser."""
    parser = argparse.ArgumentParser(description='Terminal Task Tracker CLI')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Task commands
    task_parser = subparsers.add_parser('task', help='Task operations')
    task_subparsers = task_parser.add_subparsers(dest='subcommand', help='Task subcommand')
    
    # task list
    task_list_parser = task_subparsers.add_parser('list', help='List all tasks')
    
    # task show
    task_show_parser = task_subparsers.add_parser('show', help='Show task details')
    task_show_parser.add_argument('task_id', help='Task ID')
    
    # task add
    task_add_parser = task_subparsers.add_parser('add', help='Add a new task')
    task_add_parser.add_argument('title', help='Task title')
    task_add_parser.add_argument('--description', '-d', help='Task description')
    task_add_parser.add_argument('--priority', '-p', type=int, choices=[1, 2, 3], default=1, 
                                help='Task priority (1=Low, 2=Medium, 3=High)')
    task_add_parser.add_argument('--status', '-s', 
                                choices=['not_started', 'in_progress', 'completed'], 
                                default='not_started', help='Task status')
    
    # task update
    task_update_parser = task_subparsers.add_parser('update', help='Update a task')
    task_update_parser.add_argument('task_id', help='Task ID')
    task_update_parser.add_argument('--title', '-t', help='Task title')
    task_update_parser.add_argument('--description', '-d', help='Task description')
    task_update_parser.add_argument('--priority', '-p', type=int, choices=[1, 2, 3], 
                                   help='Task priority (1=Low, 2=Medium, 3=High)')
    task_update_parser.add_argument('--status', '-s', 
                                   choices=['not_started', 'in_progress', 'completed'], 
                                   help='Task status')
    
    # task delete
    task_delete_parser = task_subparsers.add_parser('delete', help='Delete a task')
    task_delete_parser.add_argument('task_id', help='Task ID')
    
    # Plan commands
    plan_parser = subparsers.add_parser('plan', help='Plan operations')
    plan_subparsers = plan_parser.add_subparsers(dest='subcommand', help='Plan subcommand')
    
    # plan list
    plan_list_parser = plan_subparsers.add_parser('list', help='List all plan steps')
    
    # plan show
    plan_show_parser = plan_subparsers.add_parser('show', help='Show plan step details')
    plan_show_parser.add_argument('step_id', help='Step ID')
    
    # plan add
    plan_add_parser = plan_subparsers.add_parser('add', help='Add a new plan step')
    plan_add_parser.add_argument('name', help='Step name')
    plan_add_parser.add_argument('--description', '-d', help='Brief description')
    plan_add_parser.add_argument('--details', '-D', help='Detailed information')
    plan_add_parser.add_argument('--order', '-o', type=int, help='Step order (position in plan)')
    plan_add_parser.add_argument('--completed', '-c', action='store_true', 
                                help='Mark step as completed')
    
    # plan update
    plan_update_parser = plan_subparsers.add_parser('update', help='Update a plan step')
    plan_update_parser.add_argument('step_id', help='Step ID')
    plan_update_parser.add_argument('--name', '-n', help='Step name')
    plan_update_parser.add_argument('--description', '-d', help='Brief description')
    plan_update_parser.add_argument('--details', '-D', help='Detailed information')
    plan_update_parser.add_argument('--order', '-o', type=int, help='Step order (position in plan)')
    
    # plan toggle
    plan_toggle_parser = plan_subparsers.add_parser('toggle', 
                                                   help='Toggle completion status of a plan step')
    plan_toggle_parser.add_argument('step_id', help='Step ID')
    
    # plan delete
    plan_delete_parser = plan_subparsers.add_parser('delete', help='Delete a plan step')
    plan_delete_parser.add_argument('step_id', help='Step ID')
    
    # Export/Import commands
    export_parser = subparsers.add_parser('export', help='Export data to JSON file')
    export_parser.add_argument('file_path', help='Path to export file')
    
    import_parser = subparsers.add_parser('import', help='Import data from JSON file')
    import_parser.add_argument('file_path', help='Path to import file')
    
    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Initialize API
    api = TaskTrackerAPI()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        # Task commands
        if args.command == 'task':
            if args.subcommand == 'list':
                tasks = api.get_all_tasks()
                if not tasks:
                    print("No tasks found.")
                else:
                    print(f"{'ID':<36} {'Title':<30} {'Priority':<8} {'Status':<12}")
                    print("-" * 90)
                    for task in tasks:
                        print(f"{task['id']:<36} {task['title'][:30]:<30} {task['priority']:<8} {task['status']:<12}")
            
            elif args.subcommand == 'show':
                task = api.get_task(args.task_id)
                if task:
                    print(f"ID: {task['id']}")
                    print(f"Title: {task['title']}")
                    print(f"Description: {task['description']}")
                    print(f"Priority: {task['priority']}")
                    print(f"Status: {task['status']}")
                    print(f"Created: {task['created_at']}")
                    print(f"Updated: {task['updated_at']}")
                else:
                    print(f"Task not found: {args.task_id}")
            
            elif args.subcommand == 'add':
                task = api.add_task(
                    args.title,
                    args.description or "",
                    args.priority,
                    args.status
                )
                print(f"Task added: {task['id']}")
            
            elif args.subcommand == 'update':
                # Collect the fields to update
                update_fields = {}
                if args.title:
                    update_fields['title'] = args.title
                if args.description:
                    update_fields['description'] = args.description
                if args.priority:
                    update_fields['priority'] = args.priority
                if args.status:
                    update_fields['status'] = args.status
                
                task = api.update_task(args.task_id, **update_fields)
                if task:
                    print(f"Task updated: {task['id']}")
                else:
                    print(f"Task not found: {args.task_id}")
            
            elif args.subcommand == 'delete':
                result = api.delete_task(args.task_id)
                if result:
                    print(f"Task deleted: {args.task_id}")
                else:
                    print(f"Task not found: {args.task_id}")
            
            else:
                parser.print_help()
        
        # Plan commands
        elif args.command == 'plan':
            if args.subcommand == 'list':
                steps = api.get_all_plan_steps()
                if not steps:
                    print("No plan steps found.")
                else:
                    print(f"{'Order':<6} {'Completed':<10} {'ID':<36} {'Description'}")
                    print("-" * 90)
                    for step in steps:
                        completed = "[x]" if step['completed'] else "[ ]"
                        print(f"{step['order']:<6} {completed:<10} {step['id']:<36} {step['description']}")
            
            elif args.subcommand == 'show':
                step = api.get_plan_step(args.step_id)
                if step:
                    completed = "Yes" if step['completed'] else "No"
                    print(f"ID: {step['id']}")
                    print(f"Name: {step.get('name', 'N/A')}")
                    print(f"Description: {step.get('description', '')}")
                    print(f"Order: {step.get('order', 0)}")
                    print(f"Completed: {completed}")
                    
                    # Print details if available
                    details = step.get('details', '')
                    if details:
                        print("\nDetails:")
                        print(details)
                        
                    print(f"\nCreated: {step.get('created_at', 'N/A')}")
                    print(f"Updated: {step.get('updated_at', 'N/A')}")
                else:
                    print(f"Plan step not found: {args.step_id}")
            
            elif args.subcommand == 'add':
                step = api.add_plan_step(
                    args.name,
                    args.description or "",
                    args.details or "",
                    args.order,
                    args.completed
                )
                print(f"Plan step added: {step['id']}")
            
            elif args.subcommand == 'update':
                # Collect the fields to update
                update_fields = {}
                if args.name:
                    update_fields['name'] = args.name
                if args.description:
                    update_fields['description'] = args.description
                if args.details:
                    update_fields['details'] = args.details
                if args.order is not None:
                    update_fields['order'] = args.order
                
                step = api.update_plan_step(args.step_id, **update_fields)
                if step:
                    print(f"Plan step updated: {step['id']}")
                else:
                    print(f"Plan step not found: {args.step_id}")
            
            elif args.subcommand == 'toggle':
                step = api.toggle_plan_step(args.step_id)
                if step:
                    completed = "completed" if step['completed'] else "not completed"
                    print(f"Plan step {args.step_id} marked as {completed}")
                else:
                    print(f"Plan step not found: {args.step_id}")
            
            elif args.subcommand == 'delete':
                result = api.delete_plan_step(args.step_id)
                if result:
                    print(f"Plan step deleted: {args.step_id}")
                else:
                    print(f"Plan step not found: {args.step_id}")
            
            else:
                parser.print_help()
        
        # Export/Import commands
        elif args.command == 'export':
            result = api.export_data(args.file_path)
            if result:
                print(f"Data exported to {args.file_path}")
            else:
                print("Error exporting data")
        
        elif args.command == 'import':
            result = api.import_data(args.file_path)
            if result:
                print(f"Data imported from {args.file_path}")
            else:
                print("Error importing data")
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())