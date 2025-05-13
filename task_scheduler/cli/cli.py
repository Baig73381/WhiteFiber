"""Command line interface for the task scheduler."""
import argparse
import asyncio
import logging
import sys
import time
from typing import List, Optional, TextIO

from ..core.parser import TaskParser
from ..core.scheduler import TaskScheduler
from ..core.task import Task


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )


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


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Schedule and run tasks in parallel according to dependencies."
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "-f", "--file", 
        type=str, 
        help="Path to a file containing the task list"
    )
    input_group.add_argument(
        "-i", "--input", 
        type=str, 
        help="Task list as a string (CSV format)"
    )
    
    # Action options
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        "-v", "--validate", 
        action="store_true", 
        help="Validate the task list and output expected runtime without running tasks"
    )
    action_group.add_argument(
        "-r", "--run", 
        action="store_true", 
        help="Run the tasks and report on runtime difference"
    )
    
    # Other options
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Enable verbose output"
    )
    
    return parser.parse_args()


def main() -> None:
    """Main entry point for the command line interface."""
    args = parse_args()
    setup_logging(args.verbose)
    
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