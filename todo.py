#!/usr/bin/env python3
"""
Simple TODO CLI Application
A command-line tool for managing your tasks
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional


class TodoManager:
    def __init__(self, filename: str = "todos.json"):
        self.filename = filename
        self.todos: List[Dict] = self._load_todos()

    def _load_todos(self) -> List[Dict]:
        """Load todos from JSON file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def _save_todos(self) -> None:
        """Save todos to JSON file"""
        with open(self.filename, 'w') as f:
            json.dump(self.todos, f, indent=2)

    def add_todo(self, task: str, priority: str = "medium") -> None:
        """Add a new todo item"""
        todo = {
            "id": len(self.todos) + 1,
            "task": task,
            "priority": priority,
            "completed": False,
            "created_at": datetime.now().isoformat(),
            "completed_at": None
        }
        self.todos.append(todo)
        self._save_todos()
        print(f"✓ Added: {task} (ID: {todo['id']})")

    def list_todos(self, show_completed: bool = False) -> None:
        """List all todos"""
        if not self.todos:
            print("No todos found. Add one with: todo add <task>")
            return

        filtered_todos = self.todos if show_completed else [t for t in self.todos if not t['completed']]

        if not filtered_todos:
            print("No todos to display.")
            return

        print("\n" + "="*60)
        for todo in filtered_todos:
            status = "✓" if todo['completed'] else "○"
            priority_marker = self._get_priority_marker(todo['priority'])
            print(f"{status} [{todo['id']}] {priority_marker} {todo['task']}")
        print("="*60 + "\n")

    def complete_todo(self, todo_id: int) -> None:
        """Mark a todo as completed"""
        for todo in self.todos:
            if todo['id'] == todo_id:
                todo['completed'] = True
                todo['completed_at'] = datetime.now().isoformat()
                self._save_todos()
                print(f"✓ Completed: {todo['task']}")
                return
        print(f"Error: Todo with ID {todo_id} not found")

    def delete_todo(self, todo_id: int) -> None:
        """Delete a todo by ID"""
        for i, todo in enumerate(self.todos):
            if todo['id'] == todo_id:
                task = todo['task']
                self.todos.pop(i)
                self._save_todos()
                print(f"✓ Deleted: {task}")
                return
        print(f"Error: Todo with ID {todo_id} not found")

    def search_todos(self, query: str, filter_by: Optional[str] = None) -> None:
        """
        Search and filter todos

        FEATURE: Advanced search and filtering
        - Search by keyword in task description
        - Filter by priority (high, medium, low)
        - Filter by completion status
        """
        results = self.todos.copy()

        # Apply text search
        if query:
            query_lower = query.lower()
            results = [t for t in results if query_lower in t['task'].lower()]

        # Apply filter
        if filter_by:
            if filter_by in ['high', 'medium', 'low']:
                results = [t for t in results if t['priority'] == filter_by]
            elif filter_by == 'completed':
                results = [t for t in results if t['completed']]
            elif filter_by == 'active':
                results = [t for t in results if not t['completed']]

        # Display results
        if not results:
            print(f"No todos found matching '{query}'" + (f" with filter '{filter_by}'" if filter_by else ""))
            return

        print(f"\nSearch results ({len(results)} found):")
        print("="*60)
        for todo in results:
            status = "✓" if todo['completed'] else "○"
            priority_marker = self._get_priority_marker(todo['priority'])
            print(f"{status} [{todo['id']}] {priority_marker} {todo['task']}")
        print("="*60 + "\n")

    def set_priority(self, todo_id: int, priority: str) -> None:
        """Set priority for a todo"""
        if priority not in ['high', 'medium', 'low']:
            print("Error: Priority must be 'high', 'medium', or 'low'")
            return

        for todo in self.todos:
            if todo['id'] == todo_id:
                todo['priority'] = priority
                self._save_todos()
                print(f"✓ Set priority to '{priority}' for: {todo['task']}")
                return
        print(f"Error: Todo with ID {todo_id} not found")

    def edit_todo(self, todo_id: int, new_task: str) -> None:
        """Edit the task description of an existing todo"""
        for todo in self.todos:
            if todo['id'] == todo_id:
                old_task = todo['task']
                todo['task'] = new_task
                self._save_todos()
                print(f"✓ Updated todo {todo_id}:")
                print(f"  Old: {old_task}")
                print(f"  New: {new_task}")
                return
        print(f"Error: Todo with ID {todo_id} not found")

    def _get_priority_marker(self, priority: str) -> str:
        """Get visual marker for priority"""
        markers = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }
        return markers.get(priority, '⚪')


def print_help():
    """Print help message"""
    help_text = """
TODO CLI - Simple Task Manager

USAGE:
    python todo.py <command> [arguments]

COMMANDS:
    add <task> [priority]     Add a new todo (priority: high, medium, low)
    list [all]                List todos (use 'all' to show completed)
    complete <id>             Mark todo as completed
    delete <id>               Delete a todo
    edit <id> <new_task>      Edit an existing todo's description
    search <query> [filter]   Search todos and filter results
                              Filters: high, medium, low, completed, active
    priority <id> <level>     Set priority (high, medium, low)
    help                      Show this help message

EXAMPLES:
    python todo.py add "Buy groceries" high
    python todo.py list
    python todo.py complete 1
    python todo.py edit 2 "Buy groceries and cook dinner"
    python todo.py search "meeting" high
    python todo.py search "" completed
    python todo.py priority 2 high

FEATURE: Advanced Search & Filtering
    The 'search' command allows you to:
    - Find todos by keyword
    - Filter by priority level (high/medium/low)
    - Filter by status (completed/active)
    - Combine search with filters
"""
    print(help_text)


def main():
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1].lower()
    manager = TodoManager()

    if command == "add":
        if len(sys.argv) < 3:
            print("Error: Please provide a task description")
            return
        task = sys.argv[2]
        priority = sys.argv[3] if len(sys.argv) > 3 else "medium"
        manager.add_todo(task, priority)

    elif command == "list":
        show_all = len(sys.argv) > 2 and sys.argv[2].lower() == "all"
        manager.list_todos(show_completed=show_all)

    elif command == "complete":
        if len(sys.argv) < 3:
            print("Error: Please provide a todo ID")
            return
        try:
            todo_id = int(sys.argv[2])
            manager.complete_todo(todo_id)
        except ValueError:
            print("Error: ID must be a number")

    elif command == "delete":
        if len(sys.argv) < 3:
            print("Error: Please provide a todo ID")
            return
        try:
            todo_id = int(sys.argv[2])
            manager.delete_todo(todo_id)
        except ValueError:
            print("Error: ID must be a number")

    elif command == "search":
        if len(sys.argv) < 3:
            print("Error: Please provide a search query (use empty string \"\" to show all)")
            return
        query = sys.argv[2]
        filter_by = sys.argv[3] if len(sys.argv) > 3 else None
        manager.search_todos(query, filter_by)

    elif command == "priority":
        if len(sys.argv) < 4:
            print("Error: Usage: todo priority <id> <level>")
            return
        try:
            todo_id = int(sys.argv[2])
            priority = sys.argv[3].lower()
            manager.set_priority(todo_id, priority)
        except ValueError:
            print("Error: ID must be a number")

    elif command == "edit":
        if len(sys.argv) < 4:
            print("Error: Usage: todo edit <id> <new_task>")
            return
        try:
            todo_id = int(sys.argv[2])
            new_task = sys.argv[3]
            manager.edit_todo(todo_id, new_task)
        except ValueError:
            print("Error: ID must be a number")

    elif command == "help":
        print_help()

    else:
        print(f"Error: Unknown command '{command}'")
        print("Use 'python todo.py help' for usage information")


if __name__ == "__main__":
    main()
