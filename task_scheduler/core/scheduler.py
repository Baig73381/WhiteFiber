"""Task scheduler implementation."""
import asyncio
import concurrent.futures
import logging
import time
from typing import Dict, List, Set, Tuple, Optional

from .task import Task

logger = logging.getLogger(__name__)


class TaskScheduler:
    """Schedules and executes tasks based on their dependencies."""
    
    def __init__(self, tasks: List[Task]):
        """Initialize the scheduler with a list of tasks."""
        self.tasks: Dict[str, Task] = {task.name: task for task in tasks}
        self._validate_tasks()
        self._calculate_critical_path()
    
    def _validate_tasks(self) -> None:
        """Validate the task list for errors."""
        # Check for duplicate task names
        if len(self.tasks) != len([task.name for task in self.tasks.values()]):
            raise ValueError("Duplicate task names found")
        
        # Check for missing dependencies
        for task in self.tasks.values():
            for dep in task.dependencies:
                if dep not in self.tasks:
                    raise ValueError(f"Task '{task.name}' depends on non-existent task '{dep}'")
        
        # Check for circular dependencies
        self._check_circular_dependencies()
    
    def _check_circular_dependencies(self) -> None:
        """Check for circular dependencies in the task graph."""
        visited = set()
        temp_visited = set()
        
        def dfs(task_name: str) -> None:
            """Depth-first search to detect cycles."""
            if task_name in temp_visited:
                cycle_path = " -> ".join(temp_visited) + " -> " + task_name
                raise ValueError(f"Circular dependency detected: {cycle_path}")
            
            if task_name in visited:
                return
            
            temp_visited.add(task_name)
            
            for dep in self.tasks[task_name].dependencies:
                dfs(dep)
            
            temp_visited.remove(task_name)
            visited.add(task_name)
        
        for task_name in self.tasks:
            if task_name not in visited:
                dfs(task_name)
    
    def _calculate_critical_path(self) -> None:
        """Calculate the critical path and expected total runtime."""
        # Calculate earliest start times
        earliest_start_times = {}
        
        def calculate_earliest_start(task_name: str) -> float:
            """Calculate the earliest start time for a task."""
            if task_name in earliest_start_times:
                return earliest_start_times[task_name]
            
            task = self.tasks[task_name]
            if not task.dependencies:
                earliest_start = 0
            else:
                earliest_start = max(
                    calculate_earliest_start(dep) + self.tasks[dep].duration
                    for dep in task.dependencies
                )
            
            earliest_start_times[task_name] = earliest_start
            return earliest_start
        
        for task_name in self.tasks:
            calculate_earliest_start(task_name)
        
        # Calculate expected end times
        self.expected_end_times = {
            task_name: earliest_start_times[task_name] + self.tasks[task_name].duration
            for task_name in self.tasks
        }
        
        # Calculate total expected runtime
        self.expected_runtime = max(self.expected_end_times.values()) if self.expected_end_times else 0
    
    def get_expected_runtime(self) -> float:
        """Get the expected total runtime based on the critical path."""
        return self.expected_runtime
    
    def get_ready_tasks(self, completed_tasks: Set[str]) -> List[str]:
        """Get tasks that are ready to run (all dependencies satisfied)."""
        ready_tasks = []
        
        for task_name, task in self.tasks.items():
            if task_name not in completed_tasks and all(dep in completed_tasks for dep in task.dependencies):
                ready_tasks.append(task_name)
        
        return ready_tasks
    
    async def execute_task(self, task_name: str, executor: concurrent.futures.ThreadPoolExecutor) -> Tuple[str, float]:
        """Execute a single task and return its name and actual duration."""
        task = self.tasks[task_name]
        logger.info(f"Starting task: {task_name}")
        
        start_time = time.time()
        
        # Execute the task in a thread pool to simulate work
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(executor, time.sleep, task.duration)
        
        end_time = time.time()
        actual_duration = end_time - start_time
        
        logger.info(f"Completed task: {task_name} (duration: {actual_duration:.2f}s)")
        return task_name, actual_duration
    
    async def run_tasks(self) -> Tuple[float, Dict[str, float]]:
        """Run all tasks respecting dependencies and return actual runtime and task durations."""
        start_time = time.time()
        completed_tasks: Set[str] = set()
        actual_durations: Dict[str, float] = {}
        
        # Create a thread pool for executing tasks
        with concurrent.futures.ThreadPoolExecutor() as executor:
            while len(completed_tasks) < len(self.tasks):
                # Get tasks that are ready to run
                ready_tasks = self.get_ready_tasks(completed_tasks)
                
                if not ready_tasks:
                    if len(completed_tasks) < len(self.tasks):
                        raise RuntimeError("No tasks ready to run but not all tasks completed. Possible deadlock.")
                    break
                
                # Run ready tasks in parallel
                tasks = [self.execute_task(task_name, executor) for task_name in ready_tasks]
                results = await asyncio.gather(*tasks)
                
                # Update completed tasks and durations
                for task_name, duration in results:
                    completed_tasks.add(task_name)
                    actual_durations[task_name] = duration
        
        end_time = time.time()
        actual_runtime = end_time - start_time
        
        return actual_runtime, actual_durations