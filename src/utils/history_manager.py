"""
History manager module for AI QA Agent.
This module provides functionality for managing test history.
"""
import os
import logging
import json
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class HistoryManager:
    """
    Manages test history for the AI QA Agent.
    """
    
    def __init__(self, database_path: str):
        """
        Initialize the history manager.
        
        Args:
            database_path: Path to the database file.
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
        
        # Create the history table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            prompt TEXT,
            result TEXT,
            timestamp TEXT
        )
        ''')
        
        # Commit and close
        conn.commit()
        conn.close()
    
    def log_action(self, action: str, prompt: str, result: Dict[str, Any]):
        """
        Log an action to the history.
        
        Args:
            action: The action that was taken.
            prompt: The prompt that triggered the action.
            result: The result of the action.
        """
        try:
            # Connect to the database
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Insert the action
            cursor.execute(
                "INSERT INTO history (action, prompt, result, timestamp) VALUES (?, ?, ?, ?)",
                (action, prompt, json.dumps(result), datetime.now().isoformat())
            )
            
            # Commit and close
            conn.commit()
            conn.close()
            
            logger.info(f"Logged action {action} to history")
        except Exception as e:
            logger.error(f"Error logging action to history: {e}")
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the history of actions.
        
        Args:
            limit: Maximum number of history entries to return.
            
        Returns:
            List of history entries.
        """
        try:
            # Connect to the database
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Get the history
            cursor.execute(
                "SELECT id, action, prompt, result, timestamp FROM history ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            
            # Process the results
            history = []
            for row in cursor.fetchall():
                id, action, prompt, result_json, timestamp = row
                try:
                    result = json.loads(result_json)
                except:
                    result = {}
                
                history.append({
                    "id": id,
                    "action": action,
                    "prompt": prompt,
                    "result": result,
                    "timestamp": timestamp,
                    "date": timestamp.split("T")[0] if "T" in timestamp else timestamp,
                    "status": result.get("status", "unknown"),
                    "name": f"{action} - {prompt[:30]}...",
                    "pass_rate": 100 if result.get("status") == "success" else 0
                })
            
            # Close the connection
            conn.close()
            
            return history
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            return []
    
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
        except:
            return False
