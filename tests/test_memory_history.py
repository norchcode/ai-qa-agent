"""
Test script for the enhanced Memory and History Saving feature.
"""
import os
import sys
import time
import datetime
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from history_manager import HistoryManager
from test_session import TestSession

def test_memory_history_saving():
    """Test the enhanced Memory and History Saving feature."""
    print("Testing Memory and History Saving feature...")
    
    # Create a test directory
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_history')
    os.makedirs(test_dir, exist_ok=True)
    
    # Initialize the History Manager
    history_manager = HistoryManager(storage_dir=test_dir)
    
    # Test session creation and tracking
    print("Testing session creation and tracking...")
    session1 = history_manager.start_session(metadata={'test_type': 'unit_test', 'version': '1.0'})
    session1.add_test_result('/path/to/test1.py', {'status': 'passed', 'execution_time': 1.5})
    session1.add_test_result('/path/to/test2.py', {'status': 'failed', 'execution_time': 2.0, 'error_message': 'Test error'})
    session1.add_screenshot('/path/to/screenshot1.png', {'step': 'login'})
    history_manager.end_session('completed')
    
    # Create another session
    session2 = history_manager.start_session(metadata={'test_type': 'integration_test', 'version': '1.0'})
    session2.add_test_result('/path/to/test1.py', {'status': 'passed', 'execution_time': 1.2})
    session2.add_test_result('/path/to/test3.py', {'status': 'passed', 'execution_time': 3.0})
    session2.add_screenshot('/path/to/screenshot2.png', {'step': 'dashboard'})
    history_manager.end_session('completed')
    
    # Test session retrieval
    print("Testing session retrieval...")
    retrieved_session = history_manager.get_session(session1.session_id)
    if retrieved_session:
        print(f"Successfully retrieved session: {retrieved_session.session_id}")
        print(f"Session status: {retrieved_session.status}")
        print(f"Total tests: {retrieved_session.test_results['total_tests']}")
    else:
        print("Failed to retrieve session")
    
    # Test session listing with filters
    print("Testing session listing with filters...")
    sessions = history_manager.get_sessions(limit=10, filters={'status': 'completed'})
    print(f"Found {len(sessions)} completed sessions")
    
    # Test session comparison
    print("Testing session comparison...")
    comparison = history_manager.compare_sessions([session1.session_id, session2.session_id])
    print(f"Comparison summary: {comparison['summary']}")
    
    # Test new data export functionality
    print("Testing data export functionality...")
    csv_file = os.path.join(test_dir, 'sessions_export.csv')
    json_file = os.path.join(test_dir, 'sessions_export.json')
    
    # Export to CSV
    if history_manager.export_sessions_to_csv(csv_file):
        print(f"Successfully exported sessions to CSV: {csv_file}")
    else:
        print("Failed to export sessions to CSV")
    
    # Export to JSON
    if history_manager.export_sessions_to_json(json_file):
        print(f"Successfully exported sessions to JSON: {json_file}")
    else:
        print("Failed to export sessions to JSON")
    
    # Test visualization generation
    print("Testing visualization generation...")
    visualization_file = os.path.join(test_dir, 'history_visualization.png')
    if history_manager.generate_history_visualization(visualization_file):
        print(f"Successfully generated visualization: {visualization_file}")
    else:
        print("Failed to generate visualization")
    
    # Test data retention policy
    print("Testing data retention policy...")
    # Create an old session by manipulating the start_time
    session3 = history_manager.start_session(metadata={'test_type': 'old_test', 'version': '0.9'})
    session3.start_time = datetime.datetime.now() - datetime.timedelta(days=40)  # 40 days old
    session3.add_test_result('/path/to/old_test.py', {'status': 'passed', 'execution_time': 1.0})
    history_manager.end_session('completed')
    
    # Clean up old sessions
    deleted_count = history_manager.cleanup_old_sessions(days=30)
    print(f"Deleted {deleted_count} old sessions")
    
    print("Memory and History Saving feature test completed.")
    return True

if __name__ == "__main__":
    test_memory_history_saving()
