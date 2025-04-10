"""
History manager module for AI QA Agent.
"""
import logging
import sqlite3
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import csv

logger = logging.getLogger(__name__)

class HistoryManager:
    """
    Manages test history and session data.
    """
    
    def __init__(self, database_path: str):
        """
        Initialize the history manager.
        
        Args:
            database_path: Path to the SQLite database file.
        """
        self.database_path = database_path
        self._ensure_database()
        logger.info(f"History manager initialized with database at {database_path}")
    
    def _ensure_database(self):
        """Ensure the database exists and has the required tables."""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.database_path), exist_ok=True)
        
        # Connect to the database
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Create sessions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            name TEXT,
            date TEXT,
            test_path TEXT,
            status TEXT,
            pass_rate REAL,
            results TEXT
        )
        ''')
        
        # Create actions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_type TEXT,
            prompt TEXT,
            result TEXT,
            timestamp TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def is_connected(self) -> bool:
        """
        Check if the database connection is working.
        
        Returns:
            True if connected, False otherwise.
        """
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return False
    
    def create_session(self, name: str, test_path: str, results: Dict[str, Any]) -> str:
        """
        Create a new test session.
        
        Args:
            name: Name of the session.
            test_path: Path to the test file or directory.
            results: Test results dictionary.
            
        Returns:
            Session ID.
        """
        # Generate a unique session ID
        session_id = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Calculate pass rate
        total = results.get("total", 0)
        passed = results.get("passed", 0)
        pass_rate = (passed / total) * 100 if total > 0 else 0
        
        # Determine status
        if passed == total:
            status = "Passed"
        elif passed == 0:
            status = "Failed"
        else:
            status = "Partial"
        
        # Connect to the database
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Insert the session
        cursor.execute(
            "INSERT INTO sessions (id, name, date, test_path, status, pass_rate, results) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                session_id,
                name,
                datetime.now().isoformat(),
                test_path,
                status,
                pass_rate,
                json.dumps(results)
            )
        )
        
        conn.commit()
        conn.close()
        
        logger.info(f"Created session {session_id} with name '{name}'")
        return session_id
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Get details for a specific test session.
        
        Args:
            session_id: ID of the test session.
            
        Returns:
            Dictionary containing session details.
        """
        # Connect to the database
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Get the session
        cursor.execute(
            "SELECT id, name, date, test_path, status, pass_rate, results FROM sessions WHERE id = ?",
            (session_id,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            logger.warning(f"Session {session_id} not found")
            return {}
        
        # Convert to dictionary
        session = {
            "id": row[0],
            "name": row[1],
            "date": row[2],
            "test_path": row[3],
            "status": row[4],
            "pass_rate": row[5],
            "results": json.loads(row[6])
        }
        
        logger.info(f"Retrieved session {session_id}")
        return session
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get test history from the database.
        
        Args:
            limit: Maximum number of history entries to return.
            
        Returns:
            List of history entries.
        """
        # Connect to the database
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Get the sessions
        cursor.execute(
            "SELECT id, name, date, test_path, status, pass_rate FROM sessions ORDER BY date DESC LIMIT ?",
            (limit,)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        history = []
        for row in rows:
            history.append({
                "id": row[0],
                "name": row[1],
                "date": row[2],
                "test_path": row[3],
                "status": row[4],
                "pass_rate": row[5]
            })
        
        logger.info(f"Retrieved {len(history)} history entries")
        return history
    
    def compare_sessions(self, session_id1: str, session_id2: str) -> Dict[str, Any]:
        """
        Compare two test sessions.
        
        Args:
            session_id1: ID of the first test session.
            session_id2: ID of the second test session.
            
        Returns:
            Dictionary containing comparison results.
        """
        # Get the sessions
        session1 = self.get_session(session_id1)
        session2 = self.get_session(session_id2)
        
        if not session1 or not session2:
            logger.warning(f"One or both sessions not found: {session_id1}, {session_id2}")
            return {"error": "One or both sessions not found"}
        
        # Compare the sessions
        comparison = {
            "session1": {
                "id": session1["id"],
                "name": session1["name"],
                "date": session1["date"],
                "status": session1["status"],
                "pass_rate": session1["pass_rate"]
            },
            "session2": {
                "id": session2["id"],
                "name": session2["name"],
                "date": session2["date"],
                "status": session2["status"],
                "pass_rate": session2["pass_rate"]
            },
            "differences": {
                "pass_rate": session2["pass_rate"] - session1["pass_rate"],
                "status_changed": session1["status"] != session2["status"]
            }
        }
        
        # Compare test results
        results1 = session1["results"]
        results2 = session2["results"]
        
        test_diffs = []
        tests1 = {test["name"]: test for test in results1.get("tests", [])}
        tests2 = {test["name"]: test for test in results2.get("tests", [])}
        
        # Find tests in both sessions
        for name, test1 in tests1.items():
            if name in tests2:
                test2 = tests2[name]
                if test1["status"] != test2["status"]:
                    test_diffs.append({
                        "name": name,
                        "status1": test1["status"],
                        "status2": test2["status"]
                    })
        
        # Find tests only in session 1
        only_in_1 = [name for name in tests1 if name not in tests2]
        
        # Find tests only in session 2
        only_in_2 = [name for name in tests2 if name not in tests1]
        
        comparison["differences"]["tests"] = {
            "changed": test_diffs,
            "only_in_session1": only_in_1,
            "only_in_session2": only_in_2
        }
        
        logger.info(f"Compared sessions {session_id1} and {session_id2}")
        return comparison
    
    def log_action(self, action_type: str, prompt: str, result: Dict[str, Any]) -> None:
        """
        Log an action to the database.
        
        Args:
            action_type: Type of action.
            prompt: User prompt or request.
            result: Result of the action.
        """
        # Connect to the database
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Insert the action
        cursor.execute(
            "INSERT INTO actions (action_type, prompt, result, timestamp) VALUES (?, ?, ?, ?)",
            (
                action_type,
                prompt,
                json.dumps(result),
                datetime.now().isoformat()
            )
        )
        
        conn.commit()
        conn.close()
        
        logger.info(f"Logged action of type '{action_type}'")
    
    def export(self, format: str = "json") -> str:
        """
        Export test history to a file.
        
        Args:
            format: Export format (json, csv).
            
        Returns:
            Path to the export file.
        """
        # Get the history
        history = self.get_history(limit=100)  # Export up to 100 entries
        
        # Create export directory if it doesn't exist
        export_dir = os.path.join(os.path.dirname(self.database_path), "exports")
        os.makedirs(export_dir, exist_ok=True)
        
        # Generate export filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        export_path = os.path.join(export_dir, f"history_export_{timestamp}.{format}")
        
        if format == "json":
            # Export to JSON
            with open(export_path, "w") as f:
                json.dump(history, f, indent=2)
        elif format == "csv":
            # Export to CSV
            with open(export_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Name", "Date", "Test Path", "Status", "Pass Rate"])
                for entry in history:
                    writer.writerow([
                        entry["id"],
                        entry["name"],
                        entry["date"],
                        entry["test_path"],
                        entry["status"],
                        entry["pass_rate"]
                    ])
        else:
            logger.error(f"Unsupported export format: {format}")
            return ""
        
        logger.info(f"Exported history to {export_path}")
        return export_path
