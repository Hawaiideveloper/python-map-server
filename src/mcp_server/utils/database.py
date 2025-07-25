"""
Database models and operations for the Python MCP Server.

This module provides persistent storage for user data, API keys, execution history,
and other stateful information needed for multi-user support.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
from contextlib import contextmanager

DATABASE_PATH = Path("mcp_server.db")

class DatabaseManager:
    """Manage database operations for the MCP server."""
    
    def __init__(self, db_path: str = str(DATABASE_PATH)):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    subscription_tier TEXT DEFAULT 'free'
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key_hash TEXT UNIQUE NOT NULL,
                    user_id INTEGER,
                    name TEXT NOT NULL,
                    permissions TEXT NOT NULL,  -- JSON array
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP,
                    request_count INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS execution_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    api_key_id INTEGER,
                    tool_name TEXT NOT NULL,
                    code_hash TEXT,
                    execution_time REAL NOT NULL,
                    success BOOLEAN NOT NULL,
                    error_message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    input_size INTEGER,
                    output_size INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (api_key_id) REFERENCES api_keys (id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS code_snippets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    title TEXT NOT NULL,
                    description TEXT,
                    code TEXT NOT NULL,
                    language TEXT DEFAULT 'python',
                    tags TEXT,  -- JSON array
                    is_public BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS rate_limits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    identifier TEXT NOT NULL,  -- IP or API key
                    requests_count INTEGER DEFAULT 0,
                    window_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_request TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS security_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    api_key_id INTEGER,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,  -- low, medium, high, critical
                    details TEXT NOT NULL,  -- JSON
                    ip_address TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (api_key_id) REFERENCES api_keys (id)
                )
            ''')
            
            # Create indexes for better performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_execution_history_user_id ON execution_history(user_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_execution_history_timestamp ON execution_history(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_security_events_timestamp ON security_events(timestamp)')
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper cleanup."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
        finally:
            conn.close()
    
    def create_user(self, username: str, email: str, password_hash: str) -> int:
        """Create a new user and return user ID."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, password_hash)
            )
            conn.commit()
            return cursor.lastrowid or 0
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username."""
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def create_api_key(self, user_id: int, key_hash: str, name: str, permissions: List[str]) -> int:
        """Create a new API key and return key ID."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                'INSERT INTO api_keys (user_id, key_hash, name, permissions) VALUES (?, ?, ?, ?)',
                (user_id, key_hash, name, json.dumps(permissions))
            )
            conn.commit()
            return cursor.lastrowid or 0
    
    def get_api_key(self, key_hash: str) -> Optional[Dict[str, Any]]:
        """Get API key information by hash."""
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM api_keys WHERE key_hash = ? AND is_active = 1', (key_hash,))
            row = cursor.fetchone()
            if row:
                result = dict(row)
                result['permissions'] = json.loads(result['permissions'])
                return result
            return None
    
    def update_api_key_usage(self, key_hash: str):
        """Update API key last used timestamp and request count."""
        with self.get_connection() as conn:
            conn.execute(
                'UPDATE api_keys SET last_used = CURRENT_TIMESTAMP, request_count = request_count + 1 WHERE key_hash = ?',
                (key_hash,)
            )
            conn.commit()
    
    def record_execution(self, user_id: int, api_key_id: int, tool_name: str, 
                        code_hash: str, execution_time: float, success: bool,
                        error_message: Optional[str] = None, input_size: int = 0, output_size: int = 0):
        """Record code execution in history."""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO execution_history 
                (user_id, api_key_id, tool_name, code_hash, execution_time, success, error_message, input_size, output_size)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, api_key_id, tool_name, code_hash, execution_time, success, error_message, input_size, output_size))
            conn.commit()
    
    def get_execution_history(self, user_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Get execution history for a user."""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM execution_history 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (user_id, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_usage_stats(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get usage statistics for a user."""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        with self.get_connection() as conn:
            # Total executions
            cursor = conn.execute('''
                SELECT COUNT(*) as total_executions,
                       SUM(execution_time) as total_execution_time,
                       SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_executions,
                       SUM(input_size) as total_input_size,
                       SUM(output_size) as total_output_size
                FROM execution_history 
                WHERE user_id = ? AND timestamp >= ?
            ''', (user_id, since_date.isoformat()))
            stats = dict(cursor.fetchone())
            
            # Tool usage breakdown
            cursor = conn.execute('''
                SELECT tool_name, COUNT(*) as count, AVG(execution_time) as avg_time
                FROM execution_history 
                WHERE user_id = ? AND timestamp >= ?
                GROUP BY tool_name
            ''', (user_id, since_date.isoformat()))
            
            stats['tool_usage'] = [dict(row) for row in cursor.fetchall()]
            
            return stats
    
    def save_code_snippet(self, user_id: int, title: str, description: str, 
                         code: str, language: str = 'python', tags: Optional[List[str]] = None,
                         is_public: bool = False) -> int:
        """Save a code snippet."""
        tags_json = json.dumps(tags or [])
        
        with self.get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO code_snippets 
                (user_id, title, description, code, language, tags, is_public)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, title, description, code, language, tags_json, is_public))
            conn.commit()
            return cursor.lastrowid or 0
    
    def get_code_snippets(self, user_id: int, include_public: bool = True) -> List[Dict[str, Any]]:
        """Get code snippets for a user."""
        with self.get_connection() as conn:
            if include_public:
                cursor = conn.execute('''
                    SELECT * FROM code_snippets 
                    WHERE user_id = ? OR is_public = 1
                    ORDER BY updated_at DESC
                ''', (user_id,))
            else:
                cursor = conn.execute('''
                    SELECT * FROM code_snippets 
                    WHERE user_id = ?
                    ORDER BY updated_at DESC
                ''', (user_id,))
            
            snippets = []
            for row in cursor.fetchall():
                snippet = dict(row)
                snippet['tags'] = json.loads(snippet['tags'])
                snippets.append(snippet)
            
            return snippets
    
    def record_security_event(self, user_id: int, api_key_id: int, event_type: str,
                             severity: str, details: Dict[str, Any], ip_address: Optional[str] = None):
        """Record a security event."""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO security_events 
                (user_id, api_key_id, event_type, severity, details, ip_address)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, api_key_id, event_type, severity, json.dumps(details), ip_address))
            conn.commit()
    
    def get_security_events(self, user_id: Optional[int] = None, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent security events."""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        with self.get_connection() as conn:
            if user_id:
                cursor = conn.execute('''
                    SELECT * FROM security_events 
                    WHERE user_id = ? AND timestamp >= ?
                    ORDER BY timestamp DESC
                ''', (user_id, since_date.isoformat()))
            else:
                cursor = conn.execute('''
                    SELECT * FROM security_events 
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                ''', (since_date.isoformat(),))
            
            events = []
            for row in cursor.fetchall():
                event = dict(row)
                event['details'] = json.loads(event['details'])
                events.append(event)
            
            return events
    
    def cleanup_old_data(self, days: int = 90):
        """Clean up old execution history and rate limit data."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        with self.get_connection() as conn:
            # Clean old execution history
            conn.execute('DELETE FROM execution_history WHERE timestamp < ?', (cutoff_date.isoformat(),))
            
            # Clean old rate limit data
            conn.execute('DELETE FROM rate_limits WHERE window_start < ?', (cutoff_date.isoformat(),))
            
            conn.commit()

# Global database instance
db_manager = DatabaseManager()
