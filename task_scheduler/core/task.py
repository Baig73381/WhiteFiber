"""Task class and related functionality."""
from typing import List


class Task:
    """Represents a task with name, duration, and dependencies."""
    
    def __init__(self, name: str, duration: float, dependencies: List[str] = None):
        """Initialize a task with name, duration, and optional dependencies."""
        self.name = name
        self.duration = float(duration)
        self.dependencies = dependencies or []
        
        # Basic validation
        if not name:
            raise ValueError("Task name cannot be empty")
        if duration < 0:
            raise ValueError("Task duration cannot be negative")
    
    def __str__(self) -> str:
        """String representation of the task."""
        deps = ", ".join(self.dependencies) if self.dependencies else "none"
        return f"Task '{self.name}' (duration: {self.duration}s, dependencies: {deps})"