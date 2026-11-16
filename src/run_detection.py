"""
HYBRID IDS ENTRY POINT
-------------------------------------------------
This is the ONLY approved entry point for running
hybrid detection in production.

All detection MUST go through this script.
-------------------------------------------------
"""

from system_summary import print_system_summary
from hybrid_detector_final import hybrid_detect

def main():
    print_system_summary()
    
    print("="*60)
    print("HYBRID IDS - FROZEN SYSTEM")
    print("Version: v1.0-final")
    print("Status: FROZEN")
    print("="*60)
    
    # Run frozen hybrid detection
    hybrid_detect()
    
    print("\n" + "="*60)
    print("Detection complete. Results saved to outputs/")
    print("="*60)

if __name__ == "__main__":
    main()
