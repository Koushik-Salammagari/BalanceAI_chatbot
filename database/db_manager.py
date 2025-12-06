import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import uuid


class ConversationDB:
    """Manages persistent storage of conversations using SQLite"""
    
    def __init__(self, db_path: str = "conversations.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                user_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                title TEXT,
                message_count INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,
                role TEXT,
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
            )
        ''')
        
        # Create index for faster searches
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_conversation_id 
            ON messages(conversation_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_updated_at 
            ON conversations(updated_at)
        ''')
        
        conn.commit()
        conn.close()
    
    def create_conversation(self, user_id: Optional[str] = None, title: Optional[str] = None) -> str:
        """
        Create a new conversation.
        
        Args:
            user_id: Optional user identifier
            title: Optional conversation title
            
        Returns:
            conversation_id
        """
        conversation_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations (conversation_id, user_id, title)
            VALUES (?, ?, ?)
        ''', (conversation_id, user_id, title or "New Conversation"))
        
        conn.commit()
        conn.close()
        
        return conversation_id
    
    def add_message(self, conversation_id: str, role: str, content: str):
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: ID of the conversation
            role: 'user' or 'assistant'
            content: Message content
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Add message
        cursor.execute('''
            INSERT INTO messages (conversation_id, role, content)
            VALUES (?, ?, ?)
        ''', (conversation_id, role, content))
        
        # Update conversation metadata
        cursor.execute('''
            UPDATE conversations 
            SET updated_at = CURRENT_TIMESTAMP,
                message_count = message_count + 1
            WHERE conversation_id = ?
        ''', (conversation_id,))
        
        conn.commit()
        conn.close()
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """
        Get a conversation with all its messages.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Dictionary with conversation data or None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get conversation metadata
        cursor.execute('''
            SELECT * FROM conversations WHERE conversation_id = ?
        ''', (conversation_id,))
        
        conv_row = cursor.fetchone()
        if not conv_row:
            conn.close()
            return None
        
        # Get messages
        cursor.execute('''
            SELECT role, content, timestamp 
            FROM messages 
            WHERE conversation_id = ?
            ORDER BY timestamp ASC
        ''', (conversation_id,))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                "role": row["role"],
                "content": row["content"],
                "timestamp": row["timestamp"]
            })
        
        conn.close()
        
        return {
            "conversation_id": conv_row["conversation_id"],
            "user_id": conv_row["user_id"],
            "created_at": conv_row["created_at"],
            "updated_at": conv_row["updated_at"],
            "title": conv_row["title"],
            "message_count": conv_row["message_count"],
            "messages": messages
        }
    
    def list_conversations(self, limit: int = 20) -> List[Dict]:
        """
        List recent conversations.
        
        Args:
            limit: Maximum number of conversations to return
            
        Returns:
            List of conversation summaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT conversation_id, title, created_at, updated_at, message_count
            FROM conversations
            ORDER BY updated_at DESC
            LIMIT ?
        ''', (limit,))
        
        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                "conversation_id": row["conversation_id"],
                "title": row["title"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "message_count": row["message_count"]
            })
        
        conn.close()
        return conversations
    
    def delete_conversation(self, conversation_id: str):
        """
        Delete a conversation and all its messages.
        
        Args:
            conversation_id: ID of the conversation to delete
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete messages first
        cursor.execute('DELETE FROM messages WHERE conversation_id = ?', (conversation_id,))
        
        # Delete conversation
        cursor.execute('DELETE FROM conversations WHERE conversation_id = ?', (conversation_id,))
        
        conn.commit()
        conn.close()
    
    def search_conversations(self, keyword: str, limit: int = 10) -> List[Dict]:
        """
        Search conversations by keyword in messages.
        
        Args:
            keyword: Search term
            limit: Maximum results
            
        Returns:
            List of matching conversations
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT c.conversation_id, c.title, c.updated_at, c.message_count
            FROM conversations c
            JOIN messages m ON c.conversation_id = m.conversation_id
            WHERE m.content LIKE ?
            ORDER BY c.updated_at DESC
            LIMIT ?
        ''', (f'%{keyword}%', limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "conversation_id": row["conversation_id"],
                "title": row["title"],
                "updated_at": row["updated_at"],
                "message_count": row["message_count"]
            })
        
        conn.close()
        return results
    
    def update_conversation_title(self, conversation_id: str, title: str):
        """
        Update conversation title.
        
        Args:
            conversation_id: ID of the conversation
            title: New title
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE conversations 
            SET title = ?, updated_at = CURRENT_TIMESTAMP
            WHERE conversation_id = ?
        ''', (title, conversation_id))
        
        conn.commit()
        conn.close()