"""
Database Schema and Operations
Using SQLite for simplicity and portability
"""

import sqlite3
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

DB_NAME = 'cp_master.db'


def get_connection():
    """Get database connection."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database with all required tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users table - stores user profiles and handles
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            cf_handle TEXT,
            atcoder_handle TEXT,
            leetcode_handle TEXT,
            current_rating INTEGER DEFAULT 0,
            max_rating INTEGER DEFAULT 0,
            rank TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Chats table - stores group/chat information
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            chat_id INTEGER PRIMARY KEY,
            chat_type TEXT,
            title TEXT,
            contest_reminders BOOLEAN DEFAULT 1,
            reminder_time INTEGER DEFAULT 30,
            platform_filter TEXT DEFAULT 'all',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Contests table - cache upcoming contests
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contests (
            contest_id TEXT PRIMARY KEY,
            platform TEXT NOT NULL,
            name TEXT NOT NULL,
            start_time TIMESTAMP NOT NULL,
            duration INTEGER NOT NULL,
            url TEXT,
            notified BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Duels table - tracks competitive duels
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS duels (
            duel_id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            challenger_id INTEGER NOT NULL,
            challenged_id INTEGER NOT NULL,
            problem_rating INTEGER NOT NULL,
            problem_name TEXT,
            problem_url TEXT,
            status TEXT DEFAULT 'pending',
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            winner_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (challenger_id) REFERENCES users(user_id),
            FOREIGN KEY (challenged_id) REFERENCES users(user_id)
        )
    ''')
    
    # Problems table - cache solved problems
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS problems (
            problem_id TEXT PRIMARY KEY,
            platform TEXT NOT NULL,
            name TEXT NOT NULL,
            rating INTEGER,
            tags TEXT,
            url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Submissions table - track user submissions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            problem_id TEXT NOT NULL,
            platform TEXT NOT NULL,
            verdict TEXT,
            submission_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (problem_id) REFERENCES problems(problem_id)
        )
    ''')
    
    # Streaks table - track daily solving streaks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS streaks (
            user_id INTEGER PRIMARY KEY,
            current_streak INTEGER DEFAULT 0,
            max_streak INTEGER DEFAULT 0,
            last_solve_date DATE,
            total_solves INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # Daily problems table - track daily problem assignments
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            problem_id TEXT NOT NULL,
            assigned_date DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY (problem_id) REFERENCES problems(problem_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully!")


# User operations
def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def create_or_update_user(user_id: int, username: str = None, 
                          first_name: str = None, **kwargs) -> bool:
    """Create or update user information."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = COALESCE(?, username),
                first_name = COALESCE(?, first_name),
                updated_at = CURRENT_TIMESTAMP
        ''', (user_id, username, first_name, username, first_name))
        
        # Update additional fields if provided
        for key, value in kwargs.items():
            if value is not None:
                cursor.execute(f'''
                    UPDATE users SET {key} = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (value, user_id))
        
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error creating/updating user: {e}")
        return False
    finally:
        conn.close()


def set_user_handle(user_id: int, platform: str, handle: str) -> bool:
    """Set user handle for a specific platform."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        field_name = f"{platform.lower()}_handle"
        cursor.execute(f'''
            UPDATE users SET {field_name} = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (handle, user_id))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error setting handle: {e}")
        return False
    finally:
        conn.close()


# Chat operations
def get_chat(chat_id: int) -> Optional[Dict[str, Any]]:
    """Get chat information."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM chats WHERE chat_id = ?', (chat_id,))
    chat = cursor.fetchone()
    conn.close()
    return dict(chat) if chat else None


def create_or_update_chat(chat_id: int, chat_type: str, title: str = None) -> bool:
    """Create or update chat information."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO chats (chat_id, chat_type, title)
            VALUES (?, ?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET
                chat_type = ?,
                title = COALESCE(?, title)
        ''', (chat_id, chat_type, title, chat_type, title))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error creating/updating chat: {e}")
        return False
    finally:
        conn.close()


def update_chat_reminders(chat_id: int, enabled: bool) -> bool:
    """Update contest reminder settings for a chat."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE chats SET contest_reminders = ?
            WHERE chat_id = ?
        ''', (1 if enabled else 0, chat_id))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error updating reminders: {e}")
        return False
    finally:
        conn.close()


# Contest operations
def cache_contest(contest_id: str, platform: str, name: str, 
                 start_time: datetime, duration: int, url: str) -> bool:
    """Cache contest information."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO contests 
            (contest_id, platform, name, start_time, duration, url)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (contest_id, platform, name, start_time, duration, url))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error caching contest: {e}")
        return False
    finally:
        conn.close()


def get_upcoming_contests() -> List[Dict[str, Any]]:
    """Get all upcoming contests."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM contests 
        WHERE start_time > CURRENT_TIMESTAMP
        ORDER BY start_time ASC
    ''')
    contests = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return contests


# Duel operations
def create_duel(chat_id: int, challenger_id: int, challenged_id: int, 
                problem_rating: int) -> Optional[int]:
    """Create a new duel."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO duels (chat_id, challenger_id, challenged_id, problem_rating)
            VALUES (?, ?, ?, ?)
        ''', (chat_id, challenger_id, challenged_id, problem_rating))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        logger.error(f"Error creating duel: {e}")
        return None
    finally:
        conn.close()


def get_pending_duel(user_id: int) -> Optional[Dict[str, Any]]:
    """Get pending duel for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM duels 
        WHERE challenged_id = ? AND status = 'pending'
        ORDER BY created_at DESC LIMIT 1
    ''', (user_id,))
    duel = cursor.fetchone()
    conn.close()
    return dict(duel) if duel else None


def update_duel_status(duel_id: int, status: str, **kwargs) -> bool:
    """Update duel status."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE duels SET status = ? WHERE duel_id = ?
        ''', (status, duel_id))
        
        for key, value in kwargs.items():
            cursor.execute(f'''
                UPDATE duels SET {key} = ? WHERE duel_id = ?
            ''', (value, duel_id))
        
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error updating duel: {e}")
        return False
    finally:
        conn.close()


# Streak operations
def update_streak(user_id: int) -> bool:
    """Update user's solving streak."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Get current streak data
        cursor.execute('''
            SELECT current_streak, max_streak, last_solve_date, total_solves
            FROM streaks WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        today = datetime.now().date()
        
        if result:
            current, max_s, last_date, total = result
            last_date = datetime.strptime(last_date, '%Y-%m-%d').date() if last_date else None
            
            if last_date == today:
                # Already solved today
                return True
            elif last_date and (today - last_date).days == 1:
                # Continuing streak
                current += 1
                max_s = max(max_s, current)
            else:
                # Streak broken
                current = 1
            
            cursor.execute('''
                UPDATE streaks 
                SET current_streak = ?, max_streak = ?, 
                    last_solve_date = ?, total_solves = total_solves + 1
                WHERE user_id = ?
            ''', (current, max_s, today, user_id))
        else:
            # First solve
            cursor.execute('''
                INSERT INTO streaks (user_id, current_streak, max_streak, 
                                   last_solve_date, total_solves)
                VALUES (?, 1, 1, ?, 1)
            ''', (user_id, today))
        
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error updating streak: {e}")
        return False
    finally:
        conn.close()


def get_streak(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user's streak information."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM streaks WHERE user_id = ?', (user_id,))
    streak = cursor.fetchone()
    conn.close()
    return dict(streak) if streak else None
