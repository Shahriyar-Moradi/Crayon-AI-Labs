#!/usr/bin/env python3
"""
Simple test runner for Memory Chatbot API
"""

import subprocess
import sys

def run_tests():
    """Run the test suite"""
    print("🧪 Running API Tests")
    print("-" * 30)
    
    try:
        # Run pytest from tests directory
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            ".", 
            "-v"
        ], capture_output=True, text=True)
        
        # Show output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
            
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 