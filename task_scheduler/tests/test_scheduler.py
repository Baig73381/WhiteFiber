"""Tests for the task scheduler."""
import unittest
from unittest.mock import patch

from task_scheduler.core.parser import TaskParser
from task_scheduler.core.scheduler import TaskScheduler
from task_scheduler.core.task import Task


class TestTaskScheduler(unittest.TestCase):
    """Test cases for the TaskScheduler class."""
    
    def test_task_validation(self):
        """Test task validation."""
        # Valid tasks
        tasks = [
            Task("A", 5, []),
            Task("B", 3, ["A"]),
            Task("C", 2, ["A"]),
            Task("D", 1, ["B", "C"]),
        ]
        scheduler = TaskScheduler(tasks)
        self.assertEqual(len(scheduler.tasks), 4)
        
        # Duplicate task names
        with self.assertRaises(ValueError):
            TaskScheduler([
                Task("A", 5, []),
                Task("A", 3, []),
            ])
        
        # Missing dependency
        with self.assertRaises(ValueError):
            TaskScheduler([
                Task("A", 5, []),
                Task("B", 3, ["C"]),
            ])
        
        # Circular dependency
        with self.assertRaises(ValueError):
            TaskScheduler([
                Task("A", 5, ["B"]),
                Task("B", 3, ["A"]),
            ])
    
    def test_expected_runtime(self):
        """Test expected runtime calculation."""
        # Linear tasks
        tasks = [
            Task("A", 5, []),
            Task("B", 3, ["A"]),
            Task("C", 2, ["B"]),
        ]
        scheduler = TaskScheduler(tasks)
        self.assertEqual(scheduler.get_expected_runtime(), 10)
        
        # Parallel tasks
        tasks = [
            Task("A", 5, []),
            Task("B", 3, ["A"]),
            Task("C", 2, ["A"]),
            Task("D", 1, ["B", "C"]),
        ]
        scheduler = TaskScheduler(tasks)
        self.assertEqual(scheduler.get_expected_runtime(), 9)
    
    def test_parser(self):
        """Test task parser."""
        text = """
        A, 5, []
        B, 3, [A]
        C, 2, [A]
        D, 1, [B, C]
        """
        tasks = TaskParser.parse_text(text)
        self.assertEqual(len(tasks), 4)
        self.assertEqual(tasks[0].name, "A")
        self.assertEqual(tasks[0].duration, 5)
        self.assertEqual(tasks[0].dependencies, [])
        self.assertEqual(tasks[3].name, "D")
        self.assertEqual(tasks[3].dependencies, ["B", "C"])


if __name__ == "__main__":
    unittest.main()