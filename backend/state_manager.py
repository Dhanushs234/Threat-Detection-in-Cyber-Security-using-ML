"""
BACKEND STATE MANAGER - IN-MEMORY ONLY

Manages monitoring state, KPIs, logs, blocked threats, and threat map events.

RULES:
- No database
- No persistence
- Reset on restart is OK
- Thread-safe operations
"""

import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class DetectionResult:
    """Single detection result with all required fields"""
    timestamp: str
    detection_id: str
    src_ip: str
    src_country: str
    dst_ip: str
    dst_country: str
    label: str
    severity: str
    hybrid_confidence: int
    risk_score: int
    
    def to_dict(self):
        return asdict(self)


@dataclass
class BlockedThreat:
    """Blocked threat entry"""
    timestamp: str
    detection_id: str
    src_ip: str
    reason: str
    severity: str
    
    def to_dict(self):
        return asdict(self)


@dataclass
class ThreatMapEvent:
    """Threat map event for visualization"""
    from_country: str
    to_country: str
    label: str
    severity: str
    color: str
    timestamp: str
    
    def to_dict(self):
        return asdict(self)


class MonitoringState:
    """
    Thread-safe in-memory state for monitoring system.
    
    State includes:
    - Monitoring status
    - KPI counters
    - Detection logs
    - Blocked threats
    - Threat map events
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        self.reset()
    
    def reset(self):
        """Reset all state to initial values"""
        with self._lock:
            self.is_monitoring = False
            self.start_time: Optional[datetime] = None
            self.detection_counter = 0
            
            self.kpi_stats = {
                'total_detections': 0,
                'normal_count': 0,
                'suspicious_count': 0,
                'attack_count': 0,
                'blocked_count': 0
            }
            
            self.latest_detection: Optional[DetectionResult] = None
            self.detection_logs: List[DetectionResult] = []
            self.blocked_threats: List[BlockedThreat] = []
            self.threat_map_events: List[ThreatMapEvent] = []
    
    def start_monitoring(self):
        """Start monitoring session"""
        with self._lock:
            self.is_monitoring = True
            self.start_time = datetime.now()
    
    def stop_monitoring(self):
        """Stop monitoring session"""
        with self._lock:
            self.is_monitoring = False
            self.start_time = None
    
    def is_active(self) -> bool:
        """Check if monitoring is active"""
        with self._lock:
            return self.is_monitoring
    
    def add_detection(self, detection: DetectionResult):
        """
        Add a new detection result and update KPIs.
        
        Args:
            detection: DetectionResult object
        """
        with self._lock:
            self.detection_counter += 1
            self.kpi_stats['total_detections'] += 1
            
            label_lower = detection.label.lower()
            if label_lower == 'normal':
                self.kpi_stats['normal_count'] += 1
            elif label_lower == 'suspicious':
                self.kpi_stats['suspicious_count'] += 1
            elif label_lower == 'attack':
                self.kpi_stats['attack_count'] += 1
            
            self.latest_detection = detection
            self.detection_logs.append(detection)
    
    def add_blocked_threat(self, blocked: BlockedThreat):
        """
        Add a blocked threat entry.
        
        Args:
            blocked: BlockedThreat object
        """
        with self._lock:
            self.kpi_stats['blocked_count'] += 1
            self.blocked_threats.append(blocked)
    
    def add_threat_map_event(self, event: ThreatMapEvent):
        """
        Add a threat map event.
        
        Args:
            event: ThreatMapEvent object
        """
        with self._lock:
            self.threat_map_events.append(event)
    
    def get_kpi_stats(self) -> Dict:
        """
        Get current KPI statistics.
        
        Returns:
            dict: KPI stats including monitoring status and timing
        """
        with self._lock:
            stats = {
                'monitoring': self.is_monitoring,
                **self.kpi_stats
            }
            
            if self.start_time:
                elapsed = (datetime.now() - self.start_time).total_seconds()
                stats['total_time'] = round(elapsed, 2)
                
                if self.kpi_stats['total_detections'] > 0:
                    stats['avg_time_per_detection'] = round(
                        elapsed / self.kpi_stats['total_detections'], 2
                    )
                else:
                    stats['avg_time_per_detection'] = 0.0
            else:
                stats['total_time'] = 0.0
                stats['avg_time_per_detection'] = 0.0
            
            return stats
    
    def get_detection_logs(self) -> List[Dict]:
        """
        Get all detection logs.
        
        Returns:
            list: List of detection dictionaries
        """
        with self._lock:
            return [det.to_dict() for det in self.detection_logs]

    def get_detections_per_minute(self, max_minutes: int = 12) -> List[Dict[str, int]]:
        """Aggregate detections into per-minute buckets for the recent window."""
        with self._lock:
            if max_minutes <= 0:
                return []

            now_minute = datetime.now().replace(second=0, microsecond=0)
            start_minute = now_minute - timedelta(minutes=max_minutes - 1)

            bucket_counts: Dict[datetime, int] = {}

            for detection in self.detection_logs:
                try:
                    detected_at = datetime.strptime(detection.timestamp, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue

                minute_bucket = detected_at.replace(second=0, microsecond=0)
                if minute_bucket < start_minute:
                    continue

                bucket_counts[minute_bucket] = bucket_counts.get(minute_bucket, 0) + 1

            timeline = []
            for offset in range(max_minutes):
                minute = start_minute + timedelta(minutes=offset)
                timeline.append({
                    'time': minute.strftime('%H:%M'),
                    'count': bucket_counts.get(minute, 0)
                })

            return timeline
    
    def get_blocked_threats(self) -> List[Dict]:
        """
        Get all blocked threats.
        
        Returns:
            list: List of blocked threat dictionaries
        """
        with self._lock:
            return [blocked.to_dict() for blocked in self.blocked_threats]
    
    def get_threat_map_events(self) -> List[Dict]:
        """
        Get all threat map events.
        
        Returns:
            list: List of threat map event dictionaries
        """
        with self._lock:
            return [event.to_dict() for event in self.threat_map_events]
    
    def get_latest_detection(self) -> Optional[Dict]:
        """
        Get the latest detection result.
        
        Returns:
            dict or None: Latest detection dictionary
        """
        with self._lock:
            if self.latest_detection:
                return self.latest_detection.to_dict()
            return None


# Global state instance
monitoring_state = MonitoringState()
