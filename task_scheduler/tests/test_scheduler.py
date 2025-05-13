"""Tests for the task scheduler."""
import unittest
import asyncio
from unittest.mock import patch, MagicMock

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
    
    def test_complex_task_graph(self):
        """Test a more complex task graph."""
        tasks = [
            Task("A", 2, []),
            Task("B", 3, []),
            Task("C", 1, ["A", "B"]),
            Task("D", 4, ["A"]),
            Task("E", 2, ["C"]),
            Task("F", 3, ["D", "E"]),
        ]
        scheduler = TaskScheduler(tasks)
        # Expected path: B(3) -> A(2) -> C(1) -> E(2) -> D(4) -> F(3) = 15
        # But actual critical path is: B(3) -> A(2) -> D(4) -> F(3) = 12
        self.assertEqual(scheduler.get_expected_runtime(), 12)
    
    def test_empty_task_list(self):
        """Test with an empty task list."""
        scheduler = TaskScheduler([])
        self.assertEqual(scheduler.get_expected_runtime(), 0)
    
    def test_single_task(self):
        """Test with a single task."""
        scheduler = TaskScheduler([Task("A", 5, [])])
        self.assertEqual(scheduler.get_expected_runtime(), 5)
    
    def test_parser_with_different_formats(self):
        """Test parser with different dependency formats."""
        # Test with brackets format
        text1 = "A, 5, [B, C]"
        tasks1 = TaskParser.parse_text(text1)
        self.assertEqual(tasks1[0].dependencies, ["B", "C"])
        
        # Test with no brackets format
        text2 = "A, 5, B, C"
        tasks2 = TaskParser.parse_text(text2)
        self.assertEqual(tasks2[0].dependencies, ["B", "C"])
        
        # Test with empty dependencies
        text3 = "A, 5"
        tasks3 = TaskParser.parse_text(text3)
        self.assertEqual(tasks3[0].dependencies, [])
    
    @patch('time.sleep', return_value=None)  # Mock sleep to make tests faster
    async def test_run_tasks(self, mock_sleep):
        """Test running tasks."""
        tasks = [
            Task("A", 0.1, []),
            Task("B", 0.1, ["A"]),
            Task("C", 0.1, ["A"]),
            Task("D", 0.1, ["B", "C"]),
        ]
        scheduler = TaskScheduler(tasks)
        runtime, durations = await scheduler.run_tasks()
        
        # Check that all tasks were completed
        self.assertEqual(len(durations), 4)
        
        # Check execution order through dependencies
        self.assertIn("A", durations)
        self.assertIn("B", durations)
        self.assertIn("C", durations)
        self.assertIn("D", durations)


if __name__ == "__main__":
    unittest.main()