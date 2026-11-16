"""
BACKEND TEST SCRIPT

Tests all backend endpoints to verify functionality.

Usage:
    python test_backend.py
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def test_health_check():
    """Test health check endpoint"""
    print_section("TEST 1: Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print("✅ Health check passed")


def test_root_endpoint():
    """Test root endpoint"""
    print_section("TEST 2: Root Endpoint")
    
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print("✅ Root endpoint passed")


def test_manual_detection():
    """Test manual detection endpoint"""
    print_section("TEST 3: Manual Detection")
    
    # Sample input (16 raw features)
    payload = {
        "dur": 0.001055,
        "spkts": 2,
        "dpkts": 2,
        "sbytes": 132,
        "dbytes": 164,
        "sload": 500473.9375,
        "dload": 621800.9375,
        "sinpkt": 0.017,
        "dinpkt": 0.013,
        "sjit": 0.0,
        "djit": 0.0,
        "smean": 66,
        "dmean": 82,
        "synack": 0.0,
        "ackdat": 0.0,
        "proto": "udp"
    }
    
    print("Request payload:")
    print(json.dumps(payload, indent=2))
    
    response = requests.post(f"{BASE_URL}/detect/manual", json=payload)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    result = response.json()
    assert 'timestamp' in result
    assert 'label' in result
    assert 'severity' in result
    assert 'hybrid_confidence' in result
    assert 'risk_score' in result
    print("✅ Manual detection passed")


def test_monitoring_workflow():
    """Test complete monitoring workflow"""
    print_section("TEST 4: Monitoring Workflow")
    
    # Start monitoring
    print("Starting monitoring...")
    response = requests.post(f"{BASE_URL}/monitor/start")
    print(f"Start response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✅ Monitoring started")
    
    # Wait for a few detections
    print("\nWaiting 15 seconds for detections...")
    time.sleep(15)
    
    # Get stats
    print("\nFetching KPI stats...")
    response = requests.get(f"{BASE_URL}/monitor/stats")
    stats = response.json()
    print(f"Stats: {json.dumps(stats, indent=2)}")
    assert stats['monitoring'] == True
    assert stats['total_detections'] > 0
    print("✅ Stats retrieved")
    
    # Get detection logs
    print("\nFetching detection logs...")
    response = requests.get(f"{BASE_URL}/monitor/logs")
    logs = response.json()
    print(f"Total logs: {len(logs['logs'])}")
    if logs['logs']:
        print(f"Sample log: {json.dumps(logs['logs'][0], indent=2)}")
    print("✅ Logs retrieved")
    
    # Get blocked threats
    print("\nFetching blocked threats...")
    response = requests.get(f"{BASE_URL}/monitor/blocked")
    blocked = response.json()
    print(f"Total blocked: {len(blocked['blocked_threats'])}")
    if blocked['blocked_threats']:
        print(f"Sample blocked: {json.dumps(blocked['blocked_threats'][0], indent=2)}")
    print("✅ Blocked threats retrieved")
    
    # Get threat map
    print("\nFetching threat map...")
    response = requests.get(f"{BASE_URL}/monitor/threat-map")
    threat_map = response.json()
    print(f"Total threat events: {len(threat_map['threat_map'])}")
    if threat_map['threat_map']:
        print(f"Sample event: {json.dumps(threat_map['threat_map'][0], indent=2)}")
    print("✅ Threat map retrieved")
    
    # Get latest detection
    print("\nFetching latest detection...")
    response = requests.get(f"{BASE_URL}/monitor/latest")
    latest = response.json()
    if latest['latest_detection']:
        print(f"Latest: {json.dumps(latest['latest_detection'], indent=2)}")
    print("✅ Latest detection retrieved")
    
    # Stop monitoring
    print("\nStopping monitoring...")
    response = requests.post(f"{BASE_URL}/monitor/stop")
    print(f"Stop response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✅ Monitoring stopped")
    
    # Verify monitoring stopped
    print("\nVerifying monitoring stopped...")
    response = requests.get(f"{BASE_URL}/monitor/stats")
    stats = response.json()
    assert stats['monitoring'] == False
    print("✅ Monitoring confirmed stopped")


def test_invalid_manual_detection():
    """Test manual detection with invalid input"""
    print_section("TEST 5: Invalid Manual Detection")
    
    # Missing required field
    payload = {
        "dur": 0.001055,
        "spkts": 2,
        # Missing other fields
    }
    
    print("Request payload (incomplete):")
    print(json.dumps(payload, indent=2))
    
    response = requests.post(f"{BASE_URL}/detect/manual", json=payload)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 422  # Validation error
    print("✅ Invalid input correctly rejected")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("  BACKEND API TEST SUITE")
    print("="*70)
    
    try:
        test_health_check()
        test_root_endpoint()
        test_manual_detection()
        test_monitoring_workflow()
        test_invalid_manual_detection()
        
        print_section("ALL TESTS PASSED ✅")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend server")
        print("Please ensure the server is running:")
        print("  cd backend")
        print("  python main.py")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")


if __name__ == "__main__":
    run_all_tests()
