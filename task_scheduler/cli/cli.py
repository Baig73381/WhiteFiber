"""Command line interface for the task scheduler."""
import argparse
import asyncio
import sys
from typing import List

from ..core.parser import TaskParser
from ..core.scheduler import TaskScheduler
from ..core.task import Task


def validate_tasks(tasks: List[Task]) -> None:
    """Validate the task list and print the expected runtime."""
    try:
        scheduler = TaskScheduler(tasks)
        expected_runtime = scheduler.get_expected_runtime()
        
        print(f"Task list is valid.")
        print(f"Expected total runtime: {expected_runtime:.2f} seconds")
        
        # Print task details
        print("\nTask details:")
        for task_name, task in scheduler.tasks.items():
            deps = ", ".join(task.dependencies) if task.dependencies else "none"
            print(f"- {task_name}: duration={task.duration}s, dependencies={deps}")
        
    except ValueError as e:
        print(f"Error validating tasks: {e}", file=sys.stderr)
        sys.exit(1)


async def run_tasks(tasks: List[Task], verbose: bool = False) -> None:
    """Run the tasks and report on the runtime difference."""
    try:
        scheduler = TaskScheduler(tasks)
        expected_runtime = scheduler.get_expected_runtime()
        
        print(f"Starting task execution...")
        print(f"Expected runtime: {expected_runtime:.2f} seconds")
        
        # Run the tasks
        actual_runtime, actual_durations = await scheduler.run_tasks()
        
        # Calculate the difference
        runtime_diff = actual_runtime - expected_runtime
        
        print(f"\nTask execution completed.")
        print(f"Actual runtime: {actual_runtime:.2f} seconds")
        print(f"Difference: {runtime_diff:.2f} seconds ({runtime_diff/expected_runtime*100:.2f}%)")
        
        if verbose:
            print("\nTask execution details:")
            for task_name, duration in actual_durations.items():
                task = scheduler.tasks[task_name]
                expected = task.duration
                diff = duration - expected
                print(f"- {task_name}: expected={expected:.2f}s, actual={duration:.2f}s, diff={diff:.2f}s")
        
    except Exception as e:
        print(f"Error running tasks: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main entry point for the command line interface."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Schedule and run tasks in parallel according to dependencies."
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("-f", "--file", help="Path to a file containing the task list")
    input_group.add_argument("-i", "--input", help="Task list as a string (CSV format)")
    
    # Action options
    parser.add_argument("-v", "--validate", action="store_true", 
                        help="Validate the task list and output expected runtime")
    parser.add_argument("-r", "--run", action="store_true", 
                        help="Run the tasks and report on runtime difference")
    
    # Other options
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    if not args.validate and not args.run:
        print("Error: Must specify either --validate or --run")
        parser.print_help()
        sys.exit(1)
    
    # Parse the task list
    try:
        if args.file:
            tasks = TaskParser.parse_file(args.file)
        else:
            tasks = TaskParser.parse_text(args.input)
    except Exception as e:
        print(f"Error parsing task list: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Perform the requested action
    if args.validate:
        validate_tasks(tasks)
    elif args.run:
        asyncio.run(run_tasks(tasks, args.verbose))


if __name__ == "__main__":
    main()