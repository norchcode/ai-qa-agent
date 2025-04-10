"""
Test Session module for AI QA Agent.
This module provides functionality for tracking individual test execution sessions.
"""
import os
import logging
import json
import datetime
import uuid
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

class TestSession:
    """Class representing a single test execution session."""
    
    def __init__(self, session_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a new test session.
        
        Args:
            session_id: Optional session ID. If not provided, a new UUID will be generated.
            metadata: Optional metadata for the session.
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.start_time = datetime.datetime.now()
        self.end_time = None
        self.metadata = metadata or {}
        self.test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'test_files': []
        }
        self.screenshots = []
        self.logs = []
        self.status = 'running'
        
        logger.info(f"Created new test session: {self.session_id}")
    
    def add_test_result(self, test_file: str, result: Dict[str, Any]) -> None:
        """
        Add a test result to the session.
        
        Args:
            test_file: Path to the test file.
            result: Dictionary containing test result information.
        """
        logger.info(f"Adding test result for {test_file} to session {self.session_id}")
        
        # Update test counts
        self.test_results['total_tests'] += 1
        if result.get('status') == 'passed':
            self.test_results['passed_tests'] += 1
        elif result.get('status') == 'failed':
            self.test_results['failed_tests'] += 1
        elif result.get('status') == 'skipped':
            self.test_results['skipped_tests'] += 1
        
        # Add test file result
        self.test_results['test_files'].append({
            'file_path': test_file,
            'result': result
        })
    
    def add_screenshot(self, screenshot_path: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a screenshot to the session.
        
        Args:
            screenshot_path: Path to the screenshot file.
            metadata: Optional metadata for the screenshot.
        """
        logger.info(f"Adding screenshot {screenshot_path} to session {self.session_id}")
        
        self.screenshots.append({
            'path': screenshot_path,
            'timestamp': datetime.datetime.now().isoformat(),
            'metadata': metadata or {}
        })
    
    def add_log(self, log_message: str, log_level: str = 'INFO', metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a log message to the session.
        
        Args:
            log_message: The log message.
            log_level: Log level (INFO, WARNING, ERROR, etc.).
            metadata: Optional metadata for the log.
        """
        self.logs.append({
            'message': log_message,
            'level': log_level,
            'timestamp': datetime.datetime.now().isoformat(),
            'metadata': metadata or {}
        })
    
    def end_session(self, status: str = 'completed') -> None:
        """
        End the test session.
        
        Args:
            status: Final status of the session (completed, aborted, failed, etc.).
        """
        logger.info(f"Ending test session {self.session_id} with status {status}")
        
        self.end_time = datetime.datetime.now()
        self.status = status
    
    def get_duration(self) -> float:
        """
        Get the duration of the session in seconds.
        
        Returns:
            Duration in seconds.
        """
        end = self.end_time or datetime.datetime.now()
        return (end - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the session to a dictionary.
        
        Returns:
            Dictionary representation of the session.
        """
        return {
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.get_duration(),
            'status': self.status,
            'metadata': self.metadata,
            'test_results': self.test_results,
            'screenshots': self.screenshots,
            'logs': self.logs
        }
    
    def to_json(self) -> str:
        """
        Convert the session to a JSON string.
        
        Returns:
            JSON string representation of the session.
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestSession':
        """
        Create a TestSession from a dictionary.
        
        Args:
            data: Dictionary containing session data.
            
        Returns:
            TestSession instance.
        """
        session = cls(session_id=data.get('session_id'), metadata=data.get('metadata', {}))
        
        # Set timestamps
        if 'start_time' in data:
            session.start_time = datetime.datetime.fromisoformat(data['start_time'])
        if 'end_time' in data and data['end_time']:
            session.end_time = datetime.datetime.fromisoformat(data['end_time'])
        
        # Set other attributes
        session.status = data.get('status', 'unknown')
        session.test_results = data.get('test_results', {})
        session.screenshots = data.get('screenshots', [])
        session.logs = data.get('logs', [])
        
        return session
    
    @classmethod
    def from_json(cls, json_str: str) -> 'TestSession':
        """
        Create a TestSession from a JSON string.
        
        Args:
            json_str: JSON string containing session data.
            
        Returns:
            TestSession instance.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
