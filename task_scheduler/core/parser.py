"""Parser for task list specifications."""
import csv
import io
from typing import List, Optional

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
        
        # Use CSV reader to handle the parsing
        reader = csv.reader(io.StringIO(text))
        
        for i, row in enumerate(reader, start=1):
            # Skip empty rows
            if not row or all(not cell.strip() for cell in row):
                continue
            
            # Validate row format
            if len(row) < 2:
                raise ValueError(f"Line {i}: Each task must have at least a name and duration")
            
            # Parse task name and duration
            name = row[0].strip()
            
            try:
                duration = float(row[1].strip())
            except ValueError:
                raise ValueError(f"Line {i}: Duration must be a number, got '{row[1].strip()}'")
            
            # Parse dependencies if present
            dependencies = []
            if len(row) >= 3 and row[2].strip():
                # Handle different formats of dependencies
                deps_str = row[2].strip()
                
                # Handle list-like format: [TaskA, TaskB]
                if deps_str.startswith('[') and deps_str.endswith(']'):
                    deps_str = deps_str[1:-1]
                    if deps_str:
                        dependencies = [dep.strip() for dep in deps_str.split(',')]
                # Handle comma-separated format without brackets
                else:
                    dependencies = [dep.strip() for dep in deps_str.split(',')]
            
            # Create and add the task
            tasks.append(Task(name=name, duration=duration, dependencies=dependencies))
        
        return tasks
    
    @staticmethod
    def parse_file(file_path: str) -> List[Task]:
        """Parse a task list from a file."""
        with open(file_path, 'r') as f:
            return TaskParser.parse_text(f.read())