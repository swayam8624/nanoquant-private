#!/usr/bin/env python3
"""
Development script to start both the NanoQuant backend API and the frontend
"""

import subprocess
import sys
import os
import signal

# Global variables to track processes
processes = []

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nShutting down development servers...")
    for process in processes:
        try:
            process.terminate()
        except:
            pass
    sys.exit(0)

def start_backend():
    """Start the NanoQuant backend API"""
    print("Starting NanoQuant backend API...")
    try:
        # Change to the project directory
        os.chdir("/Users/swayamsingal/Desktop/Programming/NanoQuant")
        
        # Start the API server
        process = subprocess.Popen([
            "uvicorn", 
            "nanoquant.api.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8001"
        ])
        
        processes.append(process)
        print("✅ NanoQuant backend API started on http://localhost:8001")
        return True
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def start_frontend():
    """Start the Vibe Quant Studio frontend"""
    print("Starting Vibe Quant Studio frontend...")
    try:
        # Change to the frontend directory
        os.chdir("/Users/swayamsingal/Desktop/Programming/NanoQuant/vibe-quant-studio-main")
        
        # Start the frontend development server
        process = subprocess.Popen(["npm", "run", "dev"])
        
        processes.append(process)
        print("✅ Vibe Quant Studio frontend started on http://localhost:8080")
        return True
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return False

def main():
    """Main function to start both backend and frontend"""
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🚀 Starting NanoQuant Development Environment")
    print("=" * 50)
    
    # Start backend
    if not start_backend():
        print("Failed to start backend. Exiting.")
        sys.exit(1)
    
    # Start frontend
    if not start_frontend():
        print("Failed to start frontend. Exiting.")
        sys.exit(1)
    
    print("\n🎉 Development environment is running!")
    print("   Backend API: http://localhost:8001")
    print("   Frontend: http://localhost:8080")
    print("   Press Ctrl+C to stop both servers")
    
    # Wait for processes to complete
    try:
        for process in processes:
            process.wait()
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()