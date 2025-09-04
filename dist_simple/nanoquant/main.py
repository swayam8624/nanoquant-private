#!/usr/bin/env python3
"""
Main entry point for NanoQuant desktop application
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main entry point"""
    # Check if we're running as a desktop app
    if len(sys.argv) > 1 and sys.argv[1] == "desktop":
        # Launch the desktop application
        launch_desktop_app()
    else:
        # Launch the CLI
        from nanoquant.cli.main import app
        app()

def launch_desktop_app():
    """Launch the desktop application"""
    try:
        import streamlit.web.bootstrap as bootstrap
        
        # Get the path to the web app
        web_app_path = Path(__file__).parent / "web" / "app.py"
        
        # Launch Streamlit app
        bootstrap.load_config_options(flag_options={})
        bootstrap.run(str(web_app_path), command_line=None, args=[], flag_options={})
    except ImportError:
        print("Streamlit not found. Please install it with: pip install streamlit")
        sys.exit(1)
    except Exception as e:
        print(f"Error launching desktop app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()