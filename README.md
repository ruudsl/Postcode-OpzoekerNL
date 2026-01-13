# TODO CLI - Simple Task Manager

A lightweight command-line TODO application written in Python for managing your daily tasks.

## Features

- ✅ Add, list, complete, and delete tasks
- 🎯 Priority levels (high, medium, low) with visual indicators
- 🔍 **Advanced search and filtering** - Find tasks by keyword and filter by priority or status
- 💾 Persistent storage using JSON
- 🎨 Clean, colorful terminal output
- 📝 Simple and intuitive commands

## Installation

No installation required! Just make sure you have Python 3.6+ installed.

```bash
# Make the script executable (optional)
chmod +x todo.py
```

## Usage

### Basic Commands

**Add a task:**
```bash
python todo.py add "Buy groceries"
python todo.py add "Finish project report" high
python todo.py add "Call dentist" low
```

**List tasks:**
```bash
python todo.py list              # Show active tasks
python todo.py list all          # Show all tasks including completed
```

**Complete a task:**
```bash
python todo.py complete 1        # Complete task with ID 1
```

**Delete a task:**
```bash
python todo.py delete 2          # Delete task with ID 2
```

**Set priority:**
```bash
python todo.py priority 3 high   # Set task 3 to high priority
```

### 🔍 Advanced Search & Filtering (NEW FEATURE)

The search command is a powerful feature that allows you to quickly find and filter your tasks:

**Search by keyword:**
```bash
python todo.py search "meeting"
python todo.py search "project"
```

**Filter by priority:**
```bash
python todo.py search "" high      # Show all high-priority tasks
python todo.py search "" medium    # Show all medium-priority tasks
python todo.py search "" low       # Show all low-priority tasks
```

**Filter by status:**
```bash
python todo.py search "" completed # Show completed tasks
python todo.py search "" active    # Show active (incomplete) tasks
```

**Combine search with filters:**
```bash
python todo.py search "meeting" high        # Find high-priority tasks containing "meeting"
python todo.py search "project" completed   # Find completed tasks containing "project"
```

### Help

```bash
python todo.py help
```

## Example Workflow

```bash
# Add some tasks
$ python todo.py add "Write documentation" high
✓ Added: Write documentation (ID: 1)

$ python todo.py add "Review pull requests" medium
✓ Added: Review pull requests (ID: 2)

$ python todo.py add "Update dependencies" low
✓ Added: Update dependencies (ID: 3)

# List all tasks
$ python todo.py list
============================================================
○ [1] 🔴 Write documentation
○ [2] 🟡 Review pull requests
○ [3] 🟢 Update dependencies
============================================================

# Search for specific tasks
$ python todo.py search "review"
Search results (1 found):
============================================================
○ [2] 🟡 Review pull requests
============================================================

# Filter by priority
$ python todo.py search "" high
Search results (1 found):
============================================================
○ [1] 🔴 Write documentation
============================================================

# Complete a task
$ python todo.py complete 1
✓ Completed: Write documentation

# Show all tasks including completed
$ python todo.py list all
============================================================
✓ [1] 🔴 Write documentation
○ [2] 🟡 Review pull requests
○ [3] 🟢 Update dependencies
============================================================
```

## Data Storage

Tasks are stored in `todos.json` in the same directory as the script. The file is created automatically when you add your first task.

## Priority Indicators

- 🔴 High priority
- 🟡 Medium priority
- 🟢 Low priority

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only standard library)

## Implementation Details

### Key Feature: Search and Filter

The `search_todos()` method implements a flexible filtering system:

- **Text Search**: Case-insensitive keyword matching in task descriptions
- **Priority Filtering**: Filter tasks by priority level (high/medium/low)
- **Status Filtering**: Separate active tasks from completed ones
- **Combinable Filters**: Mix text search with priority or status filters

This feature addresses a common pain point in TODO applications where users need to quickly find specific tasks or focus on certain priorities without scrolling through long lists.

### Data Structure

Each todo item contains:
- `id`: Unique identifier
- `task`: Task description
- `priority`: Priority level (high/medium/low)
- `completed`: Completion status (boolean)
- `created_at`: Creation timestamp (ISO format)
- `completed_at`: Completion timestamp (ISO format, null if not completed)

## License

This project is open source and available for anyone to use and modify.

## Contributing

Feel free to fork this project and add your own enhancements! Some ideas:
- Due dates and reminders
- Task categories/tags
- Recurring tasks
- Export to different formats
- Integration with calendar apps
