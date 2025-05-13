"""Parser for task list specifications."""
import csv
import io
from typing import List

from .task import Task


class TaskParser:
    """Parser for task list specifications in text format."""
    
    @staticmethod
    def parse_text(text: str) -> List[Task]:
        """Parse a task list from text in CSV format.
        
        Format:
        name, duration in seconds, dependencies (as a list of names)
        
        Example:
        TaskA, 5, []
        TaskB, 3, [TaskA]
        TaskC, 2, [TaskA]
        TaskD, 1, [TaskB, TaskC]
        """
        tasks = []
        reader = csv.reader(io.StringIO(text))
        
        for row in reader:
            # Skip empty rows
            if not row or not row[0].strip():
                continue
            
            # Check if we have at least name and duration
            if len(row) < 2:
                raise ValueError(f"Each task must have at least a name and duration")
            
            name = row[0].strip()
            duration = float(row[1].strip())
            
            # Parse dependencies if present
            dependencies = []
            if len(row) > 2 and row[2].strip():
                deps_str = row[2].strip()
                
                # Handle list-like format: [TaskA, TaskB]
                if deps_str.startswith('[') and deps_str.endswith(']'):
                    deps_str = deps_str[1:-1]
                    if deps_str:
                        dependencies = [dep.strip() for dep in deps_str.split(',')]
                # Handle comma-separated format without brackets
                else:
                    dependencies = [dep.strip() for dep in deps_str.split(',')]
            
            tasks.append(Task(name, duration, dependencies))
        
        return tasks
    
    @staticmethod
    def parse_file(file_path: str) -> List[Task]:
        """Parse a task list from a file."""
        with open(file_path, 'r') as f:
            return TaskParser.parse_text(f.read())