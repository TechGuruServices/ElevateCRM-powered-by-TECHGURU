#!/usr/bin/env python3
"""
TECHGURU ElevateCRM - Development Server Entry Point
"""
import os
import sys
import uvicorn
from pathlib import Path

# Add current directory to Python path for proper imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check if we're in development mode
    debug_mode = os.getenv("DEBUG", "false").lower() == "true"
    
    # Run the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=debug_mode,
        log_level="info" if not debug_mode else "debug",
        access_log=True
    )
