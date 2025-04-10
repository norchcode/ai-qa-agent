"""
Unit tests for the History module.
"""
import unittest
import os
import sys
import json
import tempfile
import shutil
import sqlite3
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from history.test_session import TestSession
from history.history_manager import HistoryManager

class TestHistoryModule(unittest.TestCase):
    """Test cases for the History module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.db_file = os.path.join(self.test_dir, 'test_history.db')
        
        # Initialize the History Manager with the test directory
        self.history_manager = HistoryManager(storage_dir=self.test_dir, db_file=self.db_file)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_test_session_creation(self):
        """Test creating a TestSession."""
        # Create a test session
        session = TestSession(metadata={'test_type': 'unit_test'})
        
        # Verify session attributes
        self.assertIsNotNone(session.session_id)
        self.assertIsNotNone(session.start_time)
        self.assertIsNone(session.end_time)
        self.assertEqual(session.status, 'running')
        self.assertEqual(session.metadata, {'test_type': 'unit_test'})
        self.assertEqual(session.test_results['total_tests'], 0)
    
    def test_test_session_add_result(self):
        """Test adding a test result to a TestSession."""
        # Create a test session
        session = TestSession()
        
        # Add a test result
        test_file = '/path/to/test.py'
        result = {'status': 'passed', 'execution_time': 1.5}
        session.add_test_result(test_file, result)
        
        # Verify test result was added
        self.assertEqual(session.test_results['total_tests'], 1)
        self.assertEqual(session.test_results['passed_tests'], 1)
        self.assertEqual(len(session.test_results['test_files']), 1)
        self.assertEqual(session.test_results['test_files'][0]['file_path'], test_file)
        self.assertEqual(session.test_results['test_files'][0]['result'], result)
    
    def test_test_session_serialization(self):
        """Test serializing and deserializing a TestSession."""
        # Create a test session with data
        session = TestSession(metadata={'test_type': 'unit_test'})
        session.add_test_result('/path/to/test1.py', {'status': 'passed'})
        session.add_test_result('/path/to/test2.py', {'status': 'failed', 'error_message': 'Test error'})
        session.add_screenshot('/path/to/screenshot.png', {'step': 'login'})
        session.add_log('Test log message', 'INFO')
        session.end_session('completed')
        
        # Serialize to JSON
        json_str = session.to_json()
        
        # Deserialize from JSON
        new_session = TestSession.from_json(json_str)
        
        # Verify deserialized session
        self.assertEqual(new_session.session_id, session.session_id)
        self.assertEqual(new_session.status, 'completed')
        self.assertEqual(new_session.test_results['total_tests'], 2)
        self.assertEqual(new_session.test_results['passed_tests'], 1)
        self.assertEqual(new_session.test_results['failed_tests'], 1)
        self.assertEqual(len(new_session.screenshots), 1)
        self.assertEqual(len(new_session.logs), 1)
    
    def test_history_manager_session_lifecycle(self):
        """Test the session lifecycle in HistoryManager."""
        # Start a new session
        session = self.history_manager.start_session(metadata={'test_type': 'integration_test'})
        
        # Verify session was created
        self.assertIsNotNone(session)
        self.assertEqual(session.metadata, {'test_type': 'integration_test'})
        self.assertEqual(self.history_manager.current_session, session)
        
        # Add some test data
        session.add_test_result('/path/to/test.py', {'status': 'passed'})
        
        # End the session
        self.history_manager.end_session('completed')
        
        # Verify session was ended and saved
        self.assertIsNone(self.history_manager.current_session)
        
        # Retrieve the session
        retrieved_session = self.history_manager.get_session(session.session_id)
        
        # Verify retrieved session
        self.assertIsNotNone(retrieved_session)
        self.assertEqual(retrieved_session.session_id, session.session_id)
        self.assertEqual(retrieved_session.status, 'completed')
        self.assertEqual(retrieved_session.test_results['total_tests'], 1)
    
    def test_history_manager_get_sessions(self):
        """Test retrieving sessions from HistoryManager."""
        # Create multiple sessions
        for i in range(5):
            session = self.history_manager.start_session(metadata={'index': i})
            session.add_test_result(f'/path/to/test{i}.py', {'status': 'passed'})
            self.history_manager.end_session('completed')
        
        # Get sessions with pagination
        sessions = self.history_manager.get_sessions(limit=3, offset=0)
        
        # Verify sessions
        self.assertEqual(len(sessions), 3)
        
        # Get sessions with offset
        sessions = self.history_manager.get_sessions(limit=3, offset=3)
        
        # Verify sessions
        self.assertEqual(len(sessions), 2)
    
    def test_history_manager_delete_session(self):
        """Test deleting a session from HistoryManager."""
        # Create a session
        session = self.history_manager.start_session()
        session_id = session.session_id
        self.history_manager.end_session('completed')
        
        # Verify session exists
        self.assertIsNotNone(self.history_manager.get_session(session_id))
        
        # Delete the session
        result = self.history_manager.delete_session(session_id)
        
        # Verify deletion was successful
        self.assertTrue(result)
        
        # Verify session no longer exists
        self.assertIsNone(self.history_manager.get_session(session_id))
    
    def test_history_manager_statistics(self):
        """Test getting statistics from HistoryManager."""
        # Create sessions with different statuses
        for i in range(3):
            session = self.history_manager.start_session()
            session.add_test_result(f'/path/to/test{i}.py', {'status': 'passed'})
            self.history_manager.end_session('completed')
        
        for i in range(2):
            session = self.history_manager.start_session()
            session.add_test_result(f'/path/to/failed{i}.py', {'status': 'failed'})
            self.history_manager.end_session('failed')
        
        # Get statistics
        stats = self.history_manager.get_session_statistics()
        
        # Verify statistics
        self.assertEqual(stats['total_sessions'], 5)
        self.assertEqual(stats['total_tests'], 5)
        self.assertEqual(stats['passed_tests'], 3)
        self.assertEqual(stats['failed_tests'], 2)
        self.assertEqual(stats['completed_sessions'], 3)
        self.assertEqual(stats['failed_sessions'], 2)
    
    def test_history_manager_compare_sessions(self):
        """Test comparing sessions in HistoryManager."""
        # Create two sessions with some overlapping tests
        session1 = self.history_manager.start_session(metadata={'version': '1.0'})
        session1.add_test_result('/path/to/test1.py', {'status': 'passed'})
        session1.add_test_result('/path/to/test2.py', {'status': 'passed'})
        self.history_manager.end_session('completed')
        
        session2 = self.history_manager.start_session(metadata={'version': '1.1'})
        session2.add_test_result('/path/to/test1.py', {'status': 'passed'})
        session2.add_test_result('/path/to/test2.py', {'status': 'failed'})
        session2.add_test_result('/path/to/test3.py', {'status': 'passed'})
        self.history_manager.end_session('completed')
        
        # Compare the sessions
        comparison = self.history_manager.compare_sessions([session1.session_id, session2.session_id])
        
        # Verify comparison results
        self.assertEqual(len(comparison['sessions']), 2)
        self.assertEqual(len(comparison['test_results']), 3)  # 3 unique test files
        self.assertEqual(comparison['summary']['consistent_results'], 1)  # test1.py has consistent results
        self.assertEqual(comparison['summary']['inconsistent_results'], 1)  # test2.py has inconsistent results
    
    def test_history_manager_cleanup(self):
        """Test cleaning up old sessions in HistoryManager."""
        # Create some old sessions by manipulating the start_time
        for i in range(3):
            session = self.history_manager.start_session()
            session.start_time = datetime.now() - timedelta(days=40)  # 40 days old
            session.add_test_result(f'/path/to/old{i}.py', {'status': 'passed'})
            self.history_manager.end_session('completed')
        
        # Create some recent sessions
        for i in range(2):
            session = self.history_manager.start_session()
            session.add_test_result(f'/path/to/recent{i}.py', {'status': 'passed'})
            self.history_manager.end_session('completed')
        
        # Clean up sessions older than 30 days
        deleted_count = self.history_manager.cleanup_old_sessions(days=30)
        
        # Verify cleanup results
        self.assertEqual(deleted_count, 3)
        
        # Verify only recent sessions remain
        sessions = self.history_manager.get_sessions()
        self.assertEqual(len(sessions), 2)

if __name__ == '__main__':
    unittest.main()
