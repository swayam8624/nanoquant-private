#!/usr/bin/env python3
"""
Build script for NanoQuant frontend applications
Creates desktop packages for macOS, Windows, and Linux using Next.js and Tauri
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import platform

def create_build_directory():
    """Create build directory for packaging"""
    build_dir = Path("build")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir()
    return build_dir

def install_dependencies():
    """Install frontend dependencies"""
    try:
        print("📦 Installing frontend dependencies...")
        subprocess.run(["npm", "install"], check=True, cwd="frontend")
        print("✅ Frontend dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install frontend dependencies: {e}")
        sys.exit(1)

def build_nextjs_app():
    """Build Next.js application"""
    try:
        print("🚀 Building Next.js application...")
        subprocess.run(["npm", "run", "build"], check=True, cwd="frontend")
        print("✅ Next.js application built successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build Next.js application: {e}")
        sys.exit(1)

def create_desktop_build():
    """Create desktop build using Tauri"""
    try:
        print("🔧 Installing Tauri CLI...")
        subprocess.run(["npm", "install", "@tauri-apps/cli"], check=True, cwd="frontend")
        
        print("🔨 Building desktop application...")
        subprocess.run(["npm", "run", "tauri", "build"], check=True, cwd="frontend")
        print("✅ Desktop application built successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build desktop application: {e}")
        sys.exit(1)

def create_simple_desktop_package():
    """Create a simple desktop package for distribution"""
    try:
        print("📦 Creating simple desktop package...")
        
        # Create build directory
        dist_dir = Path("dist_frontend")
        if dist_dir.exists():
            shutil.rmtree(dist_dir)
        dist_dir.mkdir()
        
        # Copy built Next.js app
        out_dir = Path("frontend/out")
        if out_dir.exists():
            shutil.copytree(out_dir, dist_dir / "web")
        
        # Create a simple launcher script
        if platform.system() == "Windows":
            launcher_content = """@echo off
cd web
start http://localhost:3000
python -m http.server 3000
"""
            with open(dist_dir / "NanoQuant.bat", "w") as f:
                f.write(launcher_content)
        else:
            launcher_content = """#!/bin/bash
cd "$(dirname "$0")/web"
python3 -m http.server 3000 &
echo "NanoQuant frontend is running at http://localhost:3000"
echo "Press Ctrl+C to stop"
wait
"""
            with open(dist_dir / "NanoQuant.sh", "w") as f:
                f.write(launcher_content)
            # Make it executable
            os.chmod(dist_dir / "NanoQuant.sh", 0o755)
        
        print("✅ Simple desktop package created successfully")
        print(f"📦 Package location: {dist_dir}")
        return True
    except Exception as e:
        print(f"❌ Failed to create simple desktop package: {e}")
        return False

def main():
    """Main build function"""
    print("🚀 Starting NanoQuant frontend build process...")
    
    # Change to project directory
    os.chdir("/Users/swayamsingal/Desktop/Programming/NanoQuant")
    
    # Install dependencies
    install_dependencies()
    
    # Build Next.js app
    build_nextjs_app()
    
    # Export static files
    try:
        print("📤 Exporting static files...")
        subprocess.run(["npm", "run", "export"], check=True, cwd="frontend")
        print("✅ Static files exported successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to export static files: {e}")
        sys.exit(1)
    
    # Create simple desktop package
    success = create_simple_desktop_package()
    
    if success:
        print("\n🎉 Frontend build completed successfully!")
        print("📦 Distribution files are in the 'dist_frontend' directory")
    else:
        print("\n⚠️  Frontend build completed with issues.")
        sys.exit(1)

if __name__ == "__main__":
    main()