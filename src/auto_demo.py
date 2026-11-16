"""
Automated demo of manual detection with predefined test cases
No interactive input required - runs automatically
"""

import pandas as pd
from datetime import datetime
from manual_detect import preprocess_input, run_manual_detection

def demo_case(name, flow_data):
    """Run detection on a single test case"""
    print("\n" + "="*60)
    print(f"TEST CASE: {name}")
    print("="*60)
    
    print("\nInput:")
    for key, val in flow_data.items():
        print(f"  {key:15s}: {val}")
    
    df = pd.DataFrame([flow_data])
    X_scaled = preprocess_input(df)
    label, confidence, risk, severity = run_manual_detection(X_scaled)
    
    print("\n" + "="*60)
    print("HYBRID IDS DETECTION RESULT")
    print("="*60)
    print(f"Timestamp  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Label      : {label}")
    print(f"Confidence : {confidence}%")
    print(f"Risk       : {risk}%")
    print(f"Severity   : {severity}")
    print("="*60)
    
    if label == "Attack":
        print("⚠️  HIGH PRIORITY: Attack detected by Random Forest")
    elif label == "Suspicious":
        print("⚠️  MEDIUM PRIORITY: Anomaly flagged by Isolation Forest")
    else:
        print("✓ Normal traffic - no threats detected")

def main():
    print("\n" + "="*60)
    print("AUTOMATED MANUAL DETECTION DEMO")
    print("="*60)
    print("Running predefined test cases...")
    
    # Test Case 1: Normal-looking web traffic
    demo_case("Normal Web Traffic", {
        'dur': 0.5,
        'proto': 'tcp',
        'spkts': 10,
        'dpkts': 8,
        'sbytes': 500,
        'dbytes': 400,
        'sload': 8000,
        'dload': 6400,
        'sinpkt': 0.05,
        'dinpkt': 0.05,
        'sjit': 0.01,
        'djit': 0.01,
        'smean': 50,
        'dmean': 50,
        'synack': 1,
        'ackdat': 8,
    })
    
    # Test Case 2: High-volume suspicious traffic
    demo_case("High-Volume Traffic", {
        'dur': 10.0,
        'proto': 'tcp',
        'spkts': 1000,
        'dpkts': 50,
        'sbytes': 100000,
        'dbytes': 5000,
        'sload': 80000,
        'dload': 4000,
        'sinpkt': 0.01,
        'dinpkt': 0.2,
        'sjit': 0.005,
        'djit': 0.05,
        'smean': 100,
        'dmean': 100,
        'synack': 5,
        'ackdat': 50,
    })
    
    # Test Case 3: UDP traffic
    demo_case("UDP Traffic", {
        'dur': 1.0,
        'proto': 'udp',
        'spkts': 5,
        'dpkts': 5,
        'sbytes': 250,
        'dbytes': 250,
        'sload': 2000,
        'dload': 2000,
        'sinpkt': 0.2,
        'dinpkt': 0.2,
        'sjit': 0.02,
        'djit': 0.02,
        'smean': 50,
        'dmean': 50,
        'synack': 0,
        'ackdat': 0,
    })
    
    # Test Case 4: Short-duration burst
    demo_case("Short Burst", {
        'dur': 0.1,
        'proto': 'tcp',
        'spkts': 100,
        'dpkts': 10,
        'sbytes': 5000,
        'dbytes': 500,
        'sload': 400000,
        'dload': 40000,
        'sinpkt': 0.001,
        'dinpkt': 0.01,
        'sjit': 0.0005,
        'djit': 0.005,
        'smean': 50,
        'dmean': 50,
        'synack': 10,
        'ackdat': 5,
    })
    
    # Test Case 5: ICMP traffic
    demo_case("ICMP Ping", {
        'dur': 2.0,
        'proto': 'icmp',
        'spkts': 4,
        'dpkts': 4,
        'sbytes': 256,
        'dbytes': 256,
        'sload': 1024,
        'dload': 1024,
        'sinpkt': 0.5,
        'dinpkt': 0.5,
        'sjit': 0.01,
        'djit': 0.01,
        'smean': 64,
        'dmean': 64,
        'synack': 0,
        'ackdat': 0,
    })
    
    print("\n" + "="*60)
    print("✓ AUTOMATED DEMO COMPLETE")
    print("="*60)
    print("\nAll test cases processed using:")
    print("  - Frozen hybrid detector (RF → IF)")
    print("  - Frozen preprocessing pipeline")
    print("  - Output layer (confidence/risk/severity)")
    print("\nThresholds: RF=0.40, IF=0.05")

if __name__ == "__main__":
    main()
