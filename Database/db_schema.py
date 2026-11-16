"""
DATABASE SCHEMA - SQLITE

Defines database tables for history and audit storage.

RULES:
- Store ONLY manual detections, attacks, suspicious, and blocked threats
- NO normal CSV detections
- NO raw features or vectors
- NO modifications to ML logic

TABLES:
1. manual_detection_history - All manual detections
2. threat_events - Attack & suspicious detections only
3. blocked_threats - All blocked IPs
"""

import sqlite3
from pathlib import Path

# Database file path
DB_PATH = Path(__file__).parent / "ids_history.db"


def get_connection():
    """Get database connection"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(
        str(DB_PATH),
        check_same_thread=False,
        timeout=10,
    )


def initialize_database():
    """
    Initialize database and create tables if they don't exist.
    
    Called once at backend startup.
    Does NOT drop existing tables.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table 1: Manual Detection History
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manual_detection_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            detection_id TEXT,
            label TEXT NOT NULL,
            hybrid_confidence INTEGER NOT NULL,
            risk_score INTEGER NOT NULL
        )
    """)
    
    # Table 2: Threat Events (Attack & Suspicious only)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS threat_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            detection_id TEXT NOT NULL,
            src_ip TEXT NOT NULL,
            src_country TEXT NOT NULL,
            dst_ip TEXT NOT NULL,
            dst_country TEXT NOT NULL,
            label TEXT NOT NULL,
            severity TEXT NOT NULL,
            hybrid_confidence INTEGER NOT NULL,
            risk_score INTEGER NOT NULL
        )
    """)
    
    # Table 3: Blocked Threats
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blocked_threats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            detection_id TEXT NOT NULL,
            src_ip TEXT NOT NULL,
            reason TEXT NOT NULL,
            severity TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()
    
    print(f"Database initialized: {DB_PATH}")


def reset_all_tables():
    """
    Reset all tables by deleting all rows.
    
    Used for demo reset.
    Does NOT drop tables.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM manual_detection_history")
    cursor.execute("DELETE FROM threat_events")
    cursor.execute("DELETE FROM blocked_threats")
    
    conn.commit()
    conn.close()
    
    print("All database tables reset (rows deleted)")


def apply_retention_policy(max_rows=50000):
    """
    Apply retention policy to keep only the last N rows in each table.
    
    Args:
        max_rows: Maximum rows to keep per table (default: 50,000)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    tables = ['manual_detection_history', 'threat_events', 'blocked_threats']
    
    for table in tables:
        # Count rows
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        
        if count > max_rows:
            # Delete oldest rows
            rows_to_delete = count - max_rows
            cursor.execute(f"""
                DELETE FROM {table}
                WHERE id IN (
                    SELECT id FROM {table}
                    ORDER BY id ASC
                    LIMIT {rows_to_delete}
                )
            """)
            print(f"Retention applied to {table}: deleted {rows_to_delete} old rows")
    
    conn.commit()
    conn.close()


def get_table_counts():
    """
    Get row counts for all tables.
    
    Returns:
        dict: Table names and row counts
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    counts = {}
    tables = ['manual_detection_history', 'threat_events', 'blocked_threats']
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        counts[table] = cursor.fetchone()[0]
    
    conn.close()
    return counts


if __name__ == "__main__":
    # Test database initialization
    initialize_database()
    counts = get_table_counts()
    print(f"\nTable counts: {counts}")
