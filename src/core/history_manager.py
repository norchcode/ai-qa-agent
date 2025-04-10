"""
History Manager module for AI QA Agent.
This module provides functionality for managing test execution history.
"""
import os
import logging
import json
import datetime
import sqlite3
import csv
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from .test_session import TestSession

logger = logging.getLogger(__name__)

class HistoryManager:
    """Class for managing test execution history."""
    
    def __init__(self, storage_dir: Optional[str] = None, db_file: Optional[str] = None):
        """
        Initialize the History Manager.
        
        Args:
            storage_dir: Optional directory for storing session data. If not provided, will use default.
            db_file: Optional SQLite database file. If not provided, will use default.
        """
        self.storage_dir = storage_dir or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'history')
        os.makedirs(self.storage_dir, exist_ok=True)
        
        self.db_file = db_file or os.path.join(self.storage_dir, 'history.db')
        self._init_database()
        
        self.current_session = None
        
        logger.info(f"Initialized History Manager with storage directory: {self.storage_dir}")
    
    def _init_database(self) -> None:
        """Initialize the SQLite database."""
        logger.info(f"Initializing history database: {self.db_file}")
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Create sessions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            start_time TEXT NOT NULL,
            end_time TEXT,
            status TEXT NOT NULL,
            total_tests INTEGER DEFAULT 0,
            passed_tests INTEGER DEFAULT 0,
            failed_tests INTEGER DEFAULT 0,
            skipped_tests INTEGER DEFAULT 0,
            metadata TEXT,
            data_file TEXT
        )
        ''')
        
        # Create test_results table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            test_file TEXT NOT NULL,
            status TEXT NOT NULL,
            execution_time REAL,
            error_message TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )
        ''')
        
        # Create screenshots table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS screenshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            path TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            metadata TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def start_session(self, metadata: Optional[Dict[str, Any]] = None) -> TestSession:
        """
        Start a new test session.
        
        Args:
            metadata: Optional metadata for the session.
            
        Returns:
            New TestSession instance.
        """
        logger.info("Starting new test session")
        
        self.current_session = TestSession(metadata=metadata)
        return self.current_session
    
    def end_session(self, status: str = 'completed') -> None:
        """
        End the current test session.
        
        Args:
            status: Final status of the session (completed, aborted, failed, etc.).
        """
        if not self.current_session:
            logger.warning("No active session to end")
            return
        
        logger.info(f"Ending session {self.current_session.session_id} with status {status}")
        
        self.current_session.end_session(status)
        self._save_session(self.current_session)
        self.current_session = None
    
    def _save_session(self, session: TestSession) -> None:
        """
        Save a session to the database and file system.
        
        Args:
            session: TestSession to save.
        """
        logger.info(f"Saving session {session.session_id}")
        
        # Save session data to file
        data_file = os.path.join(self.storage_dir, f"session_{session.session_id}.json")
        with open(data_file, 'w') as f:
            f.write(session.to_json())
        
        # Save session metadata to database
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Insert session record
        cursor.execute('''
        INSERT OR REPLACE INTO sessions (
            session_id, start_time, end_time, status, 
            total_tests, passed_tests, failed_tests, skipped_tests,
            metadata, data_file
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session.session_id,
            session.start_time.isoformat(),
            session.end_time.isoformat() if session.end_time else None,
            session.status,
            session.test_results.get('total_tests', 0),
            session.test_results.get('passed_tests', 0),
            session.test_results.get('failed_tests', 0),
            session.test_results.get('skipped_tests', 0),
            json.dumps(session.metadata),
            data_file
        ))
        
        # Insert test results
        for test_file_result in session.test_results.get('test_files', []):
            test_file = test_file_result.get('file_path', '')
            result = test_file_result.get('result', {})
            
            cursor.execute('''
            INSERT INTO test_results (
                session_id, test_file, status, execution_time, error_message, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session.session_id,
                test_file,
                result.get('status', 'unknown'),
                result.get('execution_time', 0.0),
                result.get('error_message', ''),
                datetime.datetime.now().isoformat()
            ))
        
        # Insert screenshots
        for screenshot in session.screenshots:
            cursor.execute('''
            INSERT INTO screenshots (
                session_id, path, timestamp, metadata
            ) VALUES (?, ?, ?, ?)
            ''', (
                session.session_id,
                screenshot.get('path', ''),
                screenshot.get('timestamp', datetime.datetime.now().isoformat()),
                json.dumps(screenshot.get('metadata', {}))
            ))
        
        conn.commit()
        conn.close()
    
    def get_session(self, session_id: str) -> Optional[TestSession]:
        """
        Get a session by ID.
        
        Args:
            session_id: ID of the session to get.
            
        Returns:
            TestSession if found, None otherwise.
        """
        logger.info(f"Getting session {session_id}")
        
        # Check if it's the current session
        if self.current_session and self.current_session.session_id == session_id:
            return self.current_session
        
        # Check database
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT data_file FROM sessions WHERE session_id = ?
        ''', (session_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            logger.warning(f"Session {session_id} not found")
            return None
        
        data_file = result[0]
        
        # Load session from file
        try:
            with open(data_file, 'r') as f:
                session_data = f.read()
            
            return TestSession.from_json(session_data)
        except Exception as e:
            logger.error(f"Error loading session {session_id}: {e}")
            return None
    
    def get_sessions(self, limit: int = 100, offset: int = 0, 
                    filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get a list of sessions with pagination and filtering.
        
        Args:
            limit: Maximum number of sessions to return.
            offset: Offset for pagination.
            filters: Optional filters to apply.
            
        Returns:
            List of session metadata dictionaries.
        """
        logger.info(f"Getting sessions with limit={limit}, offset={offset}, filters={filters}")
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        query = "SELECT * FROM sessions"
        params = []
        
        # Apply filters
        if filters:
            where_clauses = []
            
            if 'status' in filters:
                where_clauses.append("status = ?")
                params.append(filters['status'])
            
            if 'start_date' in filters:
                where_clauses.append("start_time >= ?")
                params.append(filters['start_date'])
            
            if 'end_date' in filters:
                where_clauses.append("start_time <= ?")
                params.append(filters['end_date'])
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
        
        # Apply ordering and pagination
        query += " ORDER BY start_time DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                'session_id': row[0],
                'start_time': row[1],
                'end_time': row[2],
                'status': row[3],
                'total_tests': row[4],
                'passed_tests': row[5],
                'failed_tests': row[6],
                'skipped_tests': row[7],
                'metadata': json.loads(row[8]) if row[8] else {},
                'data_file': row[9]
            })
        
        conn.close()
        
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: ID of the session to delete.
            
        Returns:
            True if the session was deleted, False otherwise.
        """
        logger.info(f"Deleting session {session_id}")
        
        # Cannot delete current session
        if self.current_session and self.current_session.session_id == session_id:
            logger.warning(f"Cannot delete current session {session_id}")
            return False
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Get data file path
        cursor.execute('''
        SELECT data_file FROM sessions WHERE session_id = ?
        ''', (session_id,))
        
        result = cursor.fetchone()
        
        if not result:
            logger.warning(f"Session {session_id} not found")
            conn.close()
            return False
        
        data_file = result[0]
        
        # Delete from database
        cursor.execute('''
        DELETE FROM screenshots WHERE session_id = ?
        ''', (session_id,))
        
        cursor.execute('''
        DELETE FROM test_results WHERE session_id = ?
        ''', (session_id,))
        
        cursor.execute('''
        DELETE FROM sessions WHERE session_id = ?
        ''', (session_id,))
        
        conn.commit()
        conn.close()
        
        # Delete data file
        try:
            if os.path.exists(data_file):
                os.remove(data_file)
        except Exception as e:
            logger.error(f"Error deleting data file {data_file}: {e}")
        
        return True
    
    def get_session_statistics(self, time_range: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Get statistics about test sessions.
        
        Args:
            time_range: Optional time range filter with 'start' and 'end' keys.
            
        Returns:
            Dictionary containing statistics.
        """
        logger.info(f"Getting session statistics with time_range={time_range}")
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        query = """
        SELECT 
            COUNT(*) as total_sessions,
            SUM(total_tests) as total_tests,
            SUM(passed_tests) as passed_tests,
            SUM(failed_tests) as failed_tests,
            SUM(skipped_tests) as skipped_tests,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_sessions,
            COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_sessions,
            COUNT(CASE WHEN status = 'aborted' THEN 1 END) as aborted_sessions
        FROM sessions
        """
        
        params = []
        
        # Apply time range filter
        if time_range:
            where_clauses = []
            
            if 'start' in time_range:
                where_clauses.append("start_time >= ?")
                params.append(time_range['start'])
            
            if 'end' in time_range:
                where_clauses.append("start_time <= ?")
                params.append(time_range['end'])
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
        
        cursor.execute(query, params)
        
        row = cursor.fetchone()
        
        statistics = {
            'total_sessions': row[0],
            'total_tests': row[1] or 0,
            'passed_tests': row[2] or 0,
            'failed_tests': row[3] or 0,
            'skipped_tests': row[4] or 0,
            'completed_sessions': row[5],
            'failed_sessions': row[6],
            'aborted_sessions': row[7],
            'success_rate': (row[2] or 0) / (row[1] or 1) * 100 if row[1] else 0
        }
        
        conn.close()
        
        return statistics
    
    def compare_sessions(self, session_ids: List[str]) -> Dict[str, Any]:
        """
        Compare multiple test sessions.
        
        Args:
            session_ids: List of session IDs to compare.
            
        Returns:
            Dictionary containing comparison results.
        """
        logger.info(f"Comparing sessions: {session_ids}")
        
        sessions = []
        for session_id in session_ids:
            session = self.get_session(session_id)
            if session:
                sessions.append(session)
        
        if not sessions:
            logger.warning("No valid sessions to compare")
            return {'error': 'No valid sessions to compare'}
        
        # Prepare comparison data
        comparison = {
            'sessions': [],
            'test_results': {},
            'performance': {},
            'summary': {}
        }
        
        # Add session metadata
        for session in sessions:
            comparison['sessions'].append({
                'session_id': session.session_id,
                'start_time': session.start_time.isoformat(),
                'end_time': session.end_time.isoformat() if session.end_time else None,
                'duration': session.get_duration(),
                'status': session.status,
                'total_tests': session.test_results.get('total_tests', 0),
                'passed_tests': session.test_results.get('passed_tests', 0),
                'failed_tests': session.test_results.get('failed_tests', 0),
                'skipped_tests': session.test_results.get('skipped_tests', 0)
            })
        
        # Compare test results
        all_test_files = set()
        for session in sessions:
            for test_file_result in session.test_results.get('test_files', []):
                test_file = test_file_result.get('file_path', '')
                all_test_files.add(test_file)
        
        for test_file in all_test_files:
            comparison['test_results'][test_file] = {}
            
            for session in sessions:
                session_id = session.session_id
                comparison['test_results'][test_file][session_id] = None
                
                for test_file_result in session.test_results.get('test_files', []):
                    if test_file_result.get('file_path', '') == test_file:
                        comparison['test_results'][test_file][session_id] = test_file_result.get('result', {})
        
        # Compare performance
        for test_file in all_test_files:
            comparison['performance'][test_file] = {}
            
            for session in sessions:
                session_id = session.session_id
                
                for test_file_result in session.test_results.get('test_files', []):
                    if test_file_result.get('file_path', '') == test_file:
                        result = test_file_result.get('result', {})
                        comparison['performance'][test_file][session_id] = result.get('execution_time', 0.0)
        
        # Generate summary
        consistent_results = 0
        inconsistent_results = 0
        
        for test_file, results in comparison['test_results'].items():
            statuses = set()
            for session_id, result in results.items():
                if result:
                    statuses.add(result.get('status', 'unknown'))
            
            if len(statuses) == 1:
                consistent_results += 1
            elif len(statuses) > 1:
                inconsistent_results += 1
        
        comparison['summary'] = {
            'total_test_files': len(all_test_files),
            'consistent_results': consistent_results,
            'inconsistent_results': inconsistent_results
        }
        
        return comparison
    
    def cleanup_old_sessions(self, days: int = 30) -> int:
        """
        Delete sessions older than the specified number of days.
        
        Args:
            days: Number of days to keep sessions for.
            
        Returns:
            Number of sessions deleted.
        """
        logger.info(f"Cleaning up sessions older than {days} days")
        
        # Calculate cutoff date
        cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Get sessions to delete
        cursor.execute('''
        SELECT session_id, data_file FROM sessions WHERE start_time < ?
        ''', (cutoff_date,))
        
        sessions_to_delete = cursor.fetchall()
        
        # Delete each session
        deleted_count = 0
        for session_id, data_file in sessions_to_delete:
            # Skip current session
            if self.current_session and self.current_session.session_id == session_id:
                continue
            
            # Delete from database
            cursor.execute('''
            DELETE FROM screenshots WHERE session_id = ?
            ''', (session_id,))
            
            cursor.execute('''
            DELETE FROM test_results WHERE session_id = ?
            ''', (session_id,))
            
            cursor.execute('''
            DELETE FROM sessions WHERE session_id = ?
            ''', (session_id,))
            
            # Delete data file
            try:
                if os.path.exists(data_file):
                    os.remove(data_file)
            except Exception as e:
                logger.error(f"Error deleting data file {data_file}: {e}")
            
            deleted_count += 1
        
        conn.commit()
        conn.close()
        
        logger.info(f"Deleted {deleted_count} old sessions")
        
        return deleted_count
    
    def export_sessions_to_csv(self, output_file: str, 
                              filters: Optional[Dict[str, Any]] = None) -> bool:
        """
        Export sessions to a CSV file.
        
        Args:
            output_file: Path to the output CSV file.
            filters: Optional filters to apply.
            
        Returns:
            True if the export was successful, False otherwise.
        """
        logger.info(f"Exporting sessions to CSV: {output_file}")
        
        try:
            # Get sessions
            sessions = self.get_sessions(limit=1000, filters=filters)
            
            if not sessions:
                logger.warning("No sessions to export")
                return False
            
            # Write to CSV
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'session_id', 'start_time', 'end_time', 'status',
                    'total_tests', 'passed_tests', 'failed_tests', 'skipped_tests'
                ])
                
                writer.writeheader()
                
                for session in sessions:
                    # Remove metadata and data_file fields
                    session_data = {k: v for k, v in session.items() 
                                   if k not in ['metadata', 'data_file']}
                    writer.writerow(session_data)
            
            logger.info(f"Exported {len(sessions)} sessions to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting sessions to CSV: {e}")
            return False
    
    def export_sessions_to_json(self, output_file: str, 
                               filters: Optional[Dict[str, Any]] = None) -> bool:
        """
        Export sessions to a JSON file.
        
        Args:
            output_file: Path to the output JSON file.
            filters: Optional filters to apply.
            
        Returns:
            True if the export was successful, False otherwise.
        """
        logger.info(f"Exporting sessions to JSON: {output_file}")
        
        try:
            # Get sessions
            sessions = self.get_sessions(limit=1000, filters=filters)
            
            if not sessions:
                logger.warning("No sessions to export")
                return False
            
            # Write to JSON
            with open(output_file, 'w') as f:
                json.dump(sessions, f, indent=2)
            
            logger.info(f"Exported {len(sessions)} sessions to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting sessions to JSON: {e}")
            return False
    
    def generate_history_visualization(self, output_file: str, 
                                      days: int = 30) -> bool:
        """
        Generate a visualization of test history.
        
        Args:
            output_file: Path to the output image file.
            days: Number of days to include in the visualization.
            
        Returns:
            True if the visualization was generated successfully, False otherwise.
        """
        logger.info(f"Generating test history visualization for the last {days} days")
        
        try:
            # Calculate start date
            start_date = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
            
            # Get sessions
            conn = sqlite3.connect(self.db_file)
            
            # Query to get daily test counts
            query = """
            SELECT 
                date(start_time) as date,
                COUNT(*) as total_sessions,
                SUM(total_tests) as total_tests,
                SUM(passed_tests) as passed_tests,
                SUM(failed_tests) as failed_tests
            FROM sessions
            WHERE start_time >= ?
            GROUP BY date(start_time)
            ORDER BY date
            """
            
            # Load data into pandas DataFrame
            df = pd.read_sql_query(query, conn, params=(start_date,))
            
            if df.empty:
                logger.warning("No data available for visualization")
                return False
            
            # Create visualization
            plt.figure(figsize=(12, 8))
            
            # Plot test counts
            ax1 = plt.subplot(2, 1, 1)
            ax1.plot(df['date'], df['total_tests'], 'b-', label='Total Tests')
            ax1.plot(df['date'], df['passed_tests'], 'g-', label='Passed Tests')
            ax1.plot(df['date'], df['failed_tests'], 'r-', label='Failed Tests')
            ax1.set_title('Test Execution History')
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Number of Tests')
            ax1.legend()
            ax1.grid(True)
            
            # Plot success rate
            ax2 = plt.subplot(2, 1, 2)
            success_rate = (df['passed_tests'] / df['total_tests'] * 100).fillna(0)
            ax2.bar(df['date'], success_rate, color='green', alpha=0.7)
            ax2.set_title('Test Success Rate')
            ax2.set_xlabel('Date')
            ax2.set_ylabel('Success Rate (%)')
            ax2.set_ylim(0, 100)
            ax2.grid(True)
            
            plt.tight_layout()
            plt.savefig(output_file)
            plt.close()
            
            logger.info(f"Visualization saved to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating visualization: {e}")
            return False
