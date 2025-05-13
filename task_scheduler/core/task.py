"""Task class and related functionality."""
from dataclasses import dataclass, field
from typing import List, Set


@dataclass
class Task:
    """Represents a task with name, duration, and dependencies."""
    name: str
    duration: float
    dependencies: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate task attributes after initialization."""
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Task name must be a non-empty string")
        
        if not isinstance(self.duration, (int, float)) or self.duration < 0:
            raise ValueError("Task duration must be a non-negative number")
        
        if not isinstance(self.dependencies, list):
            raise ValueError("Dependencies must be a list")
        
        for dep in self.dependencies:
            if not isinstance(dep, str) or not dep:
                raise ValueError("Each dependency must be a non-empty string")
    
    def __str__(self) -> str:
        """String representation of the task."""
        deps = ", ".join(self.dependencies) if self.dependencies else "none"
        return f"Task '{self.name}' (duration: {self.duration}s, dependencies: {deps})"