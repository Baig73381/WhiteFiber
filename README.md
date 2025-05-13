# Task Scheduler

A command line tool to schedule and run a series of tasks in parallel, according to a task list specification input in text.

## Installation

```bash
# Install from the current directory
pip install -e .
```

## Task List Format

The task list should be in CSV format with the following schema:

```
name, duration in seconds, dependencies (as a list of names)
```

Example:

```
TaskA, 5, []
TaskB, 3, [TaskA]
TaskC, 2, [TaskA]
TaskD, 1, [TaskB, TaskC]
```

## Usage

### Validate a Task List

To validate a task list and see the expected runtime without running the tasks:

```bash
# From a file
task-scheduler -f tasks.txt -v

# From a string
task-scheduler -i "TaskA, 5, []
TaskB, 3, [TaskA]
TaskC, 2, [TaskA]
TaskD, 1, [TaskB, TaskC]" -v
```

### Run Tasks

To run the tasks and see the difference between expected and actual runtime:

```bash
# From a file
task-scheduler -f tasks.txt -r

# From a string
task-scheduler -i "TaskA, 5, []
TaskB, 3, [TaskA]
TaskC, 2, [TaskA]
TaskD, 1, [TaskB, TaskC]" -r
```

### Additional Options

- `--verbose`: Enable verbose output
- `-h, --help`: Show help message

## Example

```bash
# Create a task list file
echo "TaskA, 5, []
TaskB, 3, [TaskA]
TaskC, 2, [TaskA]
TaskD, 1, [TaskB, TaskC]" > tasks.txt

# Validate the task list
task-scheduler -f tasks.txt -v

# Run the tasks
task-scheduler -f tasks.txt -r
```

## Project Structure

```
task_scheduler/
├── __init__.py
├── __main__.py
├── core/
│   ├── __init__.py
│   ├── parser.py
│   ├── scheduler.py
│   └── task.py
└── cli/
    ├── __init__.py
    └── cli.py
```