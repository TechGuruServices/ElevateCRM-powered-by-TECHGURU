"""
Minimal FastAPI app for testing
"""
import os
from fastapi import FastAPI

# Create minimal app
app = FastAPI(
    title="TECHGURU ElevateCRM - Minimal Test",
    version="0.1.0-dev"
)

# Health check endpoint
@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "techguru-elevatecrm-api",
        "version": "0.1.0-dev",
        "environment": "development"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "TECHGURU ElevateCRM API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "test_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
