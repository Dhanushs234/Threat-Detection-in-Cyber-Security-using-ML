"""
CONTINUOUS MONITORING SERVICE - BACKGROUND LOOP

Runs row-by-row detection in background thread.

RULES:
- 7-second delay between detections
- Continues until stop signal
- Updates state after each detection
- Auto-blocks attacks only
- Thread-safe operations
- Stores to database (async, non-blocking)
"""

import threading
import time
import sys
import os
from datetime import datetime

# Add Database directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Database'))

from state_manager import (
    monitoring_state,
    DetectionResult,
    BlockedThreat,
    ThreatMapEvent
)
from detection_wrapper import (
    DatasetIterator,
    detect_single_row_with_metadata,
    generate_detection_id,
    get_threat_color,
    DATASET_PATH
)
from db_manager import db_manager
from socket_manager import emit_event


class MonitoringService:
    """
    Background monitoring service that runs continuous detection.
    
    LOOP BEHAVIOR:
    - while is_monitoring:
        - detect one row
        - generate detection_id
        - update KPI counters
        - append detection log
        - if label == attack: block src_ip
        - append threat map event
        - sleep(7 seconds)
    """
    
    def __init__(self):
        self.thread = None
        self.dataset_iterator = None
    
    def start(self):
        """Start monitoring in background thread"""
        if self.thread and self.thread.is_alive():
            return {'status': 'error', 'message': 'Monitoring already running'}
        
        # Reset and initialize
        monitoring_state.start_monitoring()
        self.dataset_iterator = DatasetIterator(DATASET_PATH)

        # Start background thread
        self.thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.thread.start()

        # Push initial detections-per-minute snapshot
        self._broadcast_detections_per_minute()

        return {'status': 'success', 'message': 'Monitoring started'}
    
    def stop(self):
        """Stop monitoring gracefully"""
        if not monitoring_state.is_active():
            return {'status': 'error', 'message': 'Monitoring not running'}
        
        monitoring_state.stop_monitoring()
        
        # Wait for thread to finish (with timeout)
        if self.thread:
            self.thread.join(timeout=10)
        
        return {'status': 'success', 'message': 'Monitoring stopped'}
    
    def _broadcast_stats(self):
        stats = monitoring_state.get_kpi_stats()
        print("Emitting stats_update", stats)
        emit_event('stats_update', stats)

    def _broadcast_detection(self, result):
        print("Emitting detection_event", result.get('detection_id'))
        emit_event('detection_event', result)

    def _broadcast_blocked(self, payload):
        print("Emitting blocked_event", payload.get('detection_id'))
        emit_event('blocked_event', payload)

    def _broadcast_detections_per_minute(self):
        series = monitoring_state.get_detections_per_minute()
        emit_event('detections_per_minute_update', {
            'detections_per_minute': series
        })

    def _monitoring_loop(self):
        """
        Main monitoring loop (runs in background thread).
        
        STRICT RULES:
        - Process one row at a time
        - 7-second delay between detections
        - Continue until is_monitoring = False
        - Auto-block only if label == "Attack"
        """
        detection_counter = 0
        
        while monitoring_state.is_active():
            try:
                # Check if more rows available
                if not self.dataset_iterator.has_next():
                    print("All rows processed. Stopping monitoring.")
                    monitoring_state.stop_monitoring()
                    break
                
                # Get next row
                features, metadata = self.dataset_iterator.get_next()
                
                # Generate detection ID
                detection_counter += 1
                detection_id = generate_detection_id(detection_counter)
                
                # Run detection
                result = detect_single_row_with_metadata(
                    row_data=features,
                    metadata=metadata,
                    detection_id=detection_id
                )
                
                # Create detection result object
                detection = DetectionResult(
                    timestamp=result['timestamp'],
                    detection_id=result['detection_id'],
                    src_ip=result['src_ip'],
                    src_country=result['src_country'],
                    dst_ip=result['dst_ip'],
                    dst_country=result['dst_country'],
                    label=result['label'],
                    severity=result['severity'],
                    hybrid_confidence=result['hybrid_confidence'],
                    risk_score=result['risk_score']
                )
                
                # Update state
                monitoring_state.add_detection(detection)

                # Broadcast detection and stats
                self._broadcast_detection(result)
                self._broadcast_stats()
                self._broadcast_detections_per_minute()
                
                # Store to database (ONLY attack or suspicious)
                label_lower = result['label'].lower()
                if label_lower in ['attack', 'suspicious']:
                    db_manager.queue_threat_event({
                        'timestamp': result['timestamp'],
                        'detection_id': result['detection_id'],
                        'src_ip': result['src_ip'],
                        'src_country': result['src_country'],
                        'dst_ip': result['dst_ip'],
                        'dst_country': result['dst_country'],
                        'label': result['label'],
                        'severity': result['severity'],
                        'hybrid_confidence': result['hybrid_confidence'],
                        'risk_score': result['risk_score']
                    })
                
                # Auto-block logic (ONLY for attacks)
                if label_lower == 'attack':
                    blocked = BlockedThreat(
                        timestamp=result['timestamp'],
                        detection_id=result['detection_id'],
                        src_ip=result['src_ip'],
                        reason='Attack detected',
                        severity=result['severity']
                    )
                    monitoring_state.add_blocked_threat(blocked)
                    
                    # Store blocked threat to database
                    blocked_payload = {
                        'timestamp': result['timestamp'],
                        'detection_id': result['detection_id'],
                        'src_ip': result['src_ip'],
                        'reason': 'Attack detected',
                        'severity': result['severity']
                    }
                    db_manager.queue_blocked_threat(blocked_payload)
                    self._broadcast_blocked(blocked_payload)
                    
                    print(f"BLOCKED: {result['src_ip']} (Detection: {detection_id})")
                
                # Add threat map event
                threat_event = ThreatMapEvent(
                    from_country=result['src_country'],
                    to_country=result['dst_country'],
                    label=result['label'],
                    severity=result['severity'],
                    color=get_threat_color(result['label']),
                    timestamp=result['timestamp']
                )
                monitoring_state.add_threat_map_event(threat_event)
                
                # Display detection
                print(f"\n{'='*70}")
                print(f"Detection {detection_id} | {result['timestamp']}")
                print(f"{'='*70}")
                print(f"Source:      {result['src_ip']} ({result['src_country']})")
                print(f"Destination: {result['dst_ip']} ({result['dst_country']})")
                print(f"Label:       {result['label']}")
                print(f"Severity:    {result['severity']}")
                print(f"Confidence:  {result['hybrid_confidence']}%")
                print(f"Risk:        {result['risk_score']}%")
                print(f"{'='*70}\n")
                
                # STRICT 7-SECOND DELAY
                time.sleep(7)
                
            except StopIteration:
                print("Dataset exhausted. Stopping monitoring.")
                monitoring_state.stop_monitoring()
                break
            
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                monitoring_state.stop_monitoring()
                break
        
        print("Monitoring loop exited.")


# Global service instance
monitoring_service = MonitoringService()
