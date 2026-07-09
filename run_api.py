"""
Launch script for the Project Health Reporting Agent API server.

Usage:
    .venv\\Scripts\\python run_api.py

The server will start at http://localhost:8000
API docs at http://localhost:8000/docs
"""
import uvicorn

if __name__ == "__main__":
    import os
    port = int(os.getenv("PROJECT_HEALTH_API_PORT", "8001"))
    uvicorn.run(
        "src.project_health.api:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        reload_dirs=["src"],
    )
