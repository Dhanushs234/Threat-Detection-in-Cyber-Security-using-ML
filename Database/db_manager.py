"""
DATABASE MANAGER - ASYNC WRITES

Handles all database operations with non-blocking writes.

RULES:
- DB writes NEVER block detection loop
- Store ONLY: manual detections, attacks, suspicious, blocked threats
- NO normal CSV detections
- NO raw features

WRITE POLICY:
- Manual detection → ALWAYS insert
- CSV detection → ONLY if attack or suspicious
- Auto-block → ALWAYS insert
"""

import sqlite3
import threading
from queue import Queue, Empty
from datetime import datetime
from typing import Dict, List, Optional

from db_schema import get_connection, apply_retention_policy


class DatabaseManager:
    """
    Thread-safe database manager with async writes.
    
    Uses background thread and queue to ensure DB writes
    never block the detection loop.
    """
    
    def __init__(self, retention_max_rows=50000):
        self.write_queue = Queue()
        self.retention_max_rows = retention_max_rows
        self.running = False
        self.worker_thread = None
        self._lock = threading.Lock()
    
    def start(self):
        """Start background worker thread for DB writes"""
        with self._lock:
            if self.running:
                return
            
            self.running = True
            self.worker_thread = threading.Thread(target=self._worker, daemon=True)
            self.worker_thread.start()
            print("Database manager started (async writes enabled)")
    
    def stop(self):
        """Stop background worker thread"""
        with self._lock:
            self.running = False
        
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
            print("Database manager stopped")
    
    def _worker(self):
        """Background worker that processes write queue"""
        while self.running:
            try:
                task = self.write_queue.get(timeout=1)
            except Empty:
                continue
            except Exception as e:
                print(f"DB write error: {e}")
                continue

            if task is None:
                self.write_queue.task_done()
                break

            try:
                operation = task.get('operation')
                data = task.get('data', {})

                if operation == 'manual_detection':
                    self._write_manual_detection(data)
                elif operation == 'threat_event':
                    self._write_threat_event(data)
                elif operation == 'blocked_threat':
                    self._write_blocked_threat(data)
                elif operation == 'retention':
                    apply_retention_policy(self.retention_max_rows)
            except Exception as e:
                print(f"⚠️ DB write error: {e}")
            finally:
                self.write_queue.task_done()
    
    def _write_manual_detection(self, data: Dict):
        """Write manual detection to database"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO manual_detection_history 
            (timestamp, detection_id, label, hybrid_confidence, risk_score)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data['timestamp'],
            data.get('detection_id', 'MANUAL'),
            data['label'],
            data['hybrid_confidence'],
            data['risk_score']
        ))
        
        conn.commit()
        conn.close()
    
    def _write_threat_event(self, data: Dict):
        """Write threat event (attack or suspicious) to database"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO threat_events 
            (timestamp, detection_id, src_ip, src_country, dst_ip, dst_country, 
             label, severity, hybrid_confidence, risk_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['timestamp'],
            data['detection_id'],
            data['src_ip'],
            data['src_country'],
            data['dst_ip'],
            data['dst_country'],
            data['label'],
            data['severity'],
            data['hybrid_confidence'],
            data['risk_score']
        ))
        
        conn.commit()
        conn.close()
    
    def _write_blocked_threat(self, data: Dict):
        """Write blocked threat to database"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO blocked_threats 
            (timestamp, detection_id, src_ip, reason, severity)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data['timestamp'],
            data['detection_id'],
            data['src_ip'],
            data['reason'],
            data['severity']
        ))
        
        conn.commit()
        conn.close()
    
    def queue_manual_detection(self, data: Dict):
        """
        Queue manual detection for async write.
        
        Args:
            data: Dict with timestamp, label, hybrid_confidence, risk_score
        """
        self.write_queue.put({
            'operation': 'manual_detection',
            'data': data
        })
    
    def queue_threat_event(self, data: Dict):
        """
        Queue threat event for async write.
        
        ONLY called for attack or suspicious detections.
        
        Args:
            data: Dict with all detection fields
        """
        label_lower = data['label'].lower()
        
        # STRICT RULE: Only store attack or suspicious
        if label_lower in ['attack', 'suspicious']:
            self.write_queue.put({
                'operation': 'threat_event',
                'data': data
            })
    
    def queue_blocked_threat(self, data: Dict):
        """
        Queue blocked threat for async write.
        
        Args:
            data: Dict with timestamp, detection_id, src_ip, reason, severity
        """
        self.write_queue.put({
            'operation': 'blocked_threat',
            'data': data
        })
    
    def apply_retention(self):
        """Apply retention policy (non-blocking)"""
        self.write_queue.put({
            'operation': 'retention',
            'data': {}
        })
    
    def get_manual_detection_history(self, limit: int = 100) -> List[Dict]:
        """
        Get manual detection history.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of manual detection records
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, timestamp, detection_id, label, hybrid_confidence, risk_score
            FROM manual_detection_history
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'timestamp': row[1],
                'detection_id': row[2],
                'label': row[3],
                'hybrid_confidence': row[4],
                'risk_score': row[5]
            }
            for row in rows
        ]
    
    def get_threat_events(self, limit: int = 100) -> List[Dict]:
        """
        Get threat events (attacks and suspicious).
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of threat event records
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, timestamp, detection_id, src_ip, src_country, dst_ip, dst_country,
                   label, severity, hybrid_confidence, risk_score
            FROM threat_events
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'timestamp': row[1],
                'detection_id': row[2],
                'src_ip': row[3],
                'src_country': row[4],
                'dst_ip': row[5],
                'dst_country': row[6],
                'label': row[7],
                'severity': row[8],
                'hybrid_confidence': row[9],
                'risk_score': row[10]
            }
            for row in rows
        ]
    
    def get_blocked_threats_history(self, limit: int = 100) -> List[Dict]:
        """
        Get blocked threats history.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of blocked threat records
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, timestamp, detection_id, src_ip, reason, severity
            FROM blocked_threats
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'timestamp': row[1],
                'detection_id': row[2],
                'src_ip': row[3],
                'reason': row[4],
                'severity': row[5]
            }
            for row in rows
        ]


# Global database manager instance
db_manager = DatabaseManager(retention_max_rows=50000)
