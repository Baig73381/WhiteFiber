"""Task scheduler implementation."""
import asyncio
import concurrent.futures
import logging
import time
from typing import Dict, List, Set, Tuple

from .task import Task

logger = logging.getLogger(__name__)


class TaskScheduler:
    """Schedules and executes tasks based on their dependencies."""
    
    def __init__(self, tasks: List[Task]):
        """Initialize the scheduler with a list of tasks."""
        self.tasks = {task.name: task for task in tasks}
        self.validate_tasks()
        self.calculate_expected_runtime()
    
    def validate_tasks(self) -> bool:
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
        visited = set()
        temp_visited = set()
        
        def check_cycle(task_name, path=None):
            if path is None:
                path = []
                
            if task_name in temp_visited:
                cycle = " -> ".join(path) + " -> " + task_name
                raise ValueError(f"Circular dependency detected: {cycle}")
            
            if task_name in visited:
                return
            
            temp_visited.add(task_name)
            path.append(task_name)
            
            for dep in self.tasks[task_name].dependencies:
                check_cycle(dep, path)
            
            path.pop()
            temp_visited.remove(task_name)
            visited.add(task_name)
        
        for task_name in self.tasks:
            if task_name not in visited:
                check_cycle(task_name, [])
        
        return True
    
    def calculate_expected_runtime(self) -> float:
        """Calculate the expected total runtime based on the critical path."""
        earliest_finish = {}
        
        def get_finish_time(task_name):
            if task_name in earliest_finish:
                return earliest_finish[task_name]
            
            task = self.tasks[task_name]
            
            if not task.dependencies:
                finish_time = task.duration
            else:
                finish_time = max(get_finish_time(dep) for dep in task.dependencies) + task.duration
            
            earliest_finish[task_name] = finish_time
            return finish_time
        
        # Calculate finish time for all tasks
        for task_name in self.tasks:
            get_finish_time(task_name)
        
        self.expected_runtime = max(earliest_finish.values()) if earliest_finish else 0
        return self.expected_runtime
    
    def get_expected_runtime(self) -> float:
        """Get the expected total runtime."""
        return self.expected_runtime
    
    async def execute_task(self, task_name: str, executor: concurrent.futures.ThreadPoolExecutor) -> Tuple[str, float]:
        """Execute a single task and return its name and actual duration."""
        task = self.tasks[task_name]
        print(f"Starting task: {task_name}")
        
        start_time = time.time()
        
        # Execute the task in a thread pool to simulate work
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(executor, time.sleep, task.duration)
        
        end_time = time.time()
        actual_duration = end_time - start_time
        
        print(f"Completed task: {task_name} (took {actual_duration:.2f}s)")
        return task_name, actual_duration
    
    async def run_tasks(self) -> Tuple[float, Dict[str, float]]:
        """Run all tasks respecting dependencies and return actual runtime and task durations."""
        start_time = time.time()
        completed = set()
        durations = {}
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            while len(completed) < len(self.tasks):
                # Find tasks that are ready to run
                ready_tasks = []
                for task_name, task in self.tasks.items():
                    if task_name not in completed and all(dep in completed for dep in task.dependencies):
                        ready_tasks.append(task_name)
                
                if not ready_tasks:
                    if len(completed) < len(self.tasks):
                        raise RuntimeError("No tasks ready but not all completed. Possible deadlock.")
                    break
                
                # Run ready tasks in parallel
                pending_tasks = [self.execute_task(name, executor) for name in ready_tasks]
                results = await asyncio.gather(*pending_tasks)
                
                # Update completed tasks
                for name, duration in results:
                    completed.add(name)
                    durations[name] = duration
        
        end_time = time.time()
        total_time = end_time - start_time
        
        return total_time, durations