"""
UIDAI Insights API - Main Application
======================================

Production-grade REST API for Aadhaar analytics.

🚀 FEATURES:
- FastAPI with automatic OpenAPI/Swagger docs
- CORS middleware for frontend integration
- Organized routers for clean code structure
- Health checks for monitoring
- Pydantic validation for all requests/responses

💼 WHY THIS MATTERS FOR YOUR RESUME:
- Shows you can build deployable APIs
- Industry-standard patterns (FastAPI is used by Microsoft, Netflix, Uber)
- Clean architecture with separation of concerns
- Auto-generated documentation (Swagger UI)

Usage:
    uvicorn api.main:app --reload --port 8000
    
Swagger Docs:
    http://localhost:8000/docs
    
ReDoc:
    http://localhost:8000/redoc
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import routers
from api.routers import health, analytics, predictions, chat


# =============================================================================
# APP CONFIGURATION
# =============================================================================

# API Metadata for Swagger docs
API_TITLE = "UIDAI Aadhaar Insights API"
API_DESCRIPTION = """
## 🔍 UIDAI Aadhaar Analytics REST API

A production-grade API for accessing Aadhaar enrolment and update analytics.

### 📊 Features

* **Analytics** - State summaries, monthly trends, overall statistics
* **Risk Scores** - ML-based risk scoring for 65+ states (0-100 scale)
* **Business Impact** - Fraud savings, ROI analysis, actionable recommendations
* **AI Chat** - Natural language queries about your data
* **Health Checks** - API monitoring and status

### 🔗 Quick Links

* [Interactive Docs (Swagger UI)](/docs)
* [Alternative Docs (ReDoc)](/redoc)
* [OpenAPI JSON](/openapi.json)

### 👨‍💻 Author

Built by **Bhojraj** - [GitHub](https://github.com/BhojrajCSE21)
"""

API_VERSION = "1.0.0"

# Create FastAPI app instance
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Bhojraj",
        "url": "https://github.com/BhojrajCSE21",
    },
    license_info={
        "name": "MIT License",
    }
)


# =============================================================================
# MIDDLEWARE
# =============================================================================

# CORS middleware - allows frontend apps to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# REGISTER ROUTERS
# =============================================================================

# API v1 prefix for versioning
API_V1_PREFIX = "/api/v1"

# Health check (no prefix needed)
app.include_router(health.router, prefix=API_V1_PREFIX)

# Analytics endpoints
app.include_router(analytics.router, prefix=API_V1_PREFIX)

# Risk & predictions endpoints
app.include_router(predictions.router, prefix=API_V1_PREFIX)

# Business impact endpoints
app.include_router(predictions.business_router, prefix=API_V1_PREFIX)

# AI Chat endpoints
app.include_router(chat.router, prefix=API_V1_PREFIX)


# =============================================================================
# ROOT ENDPOINT
# =============================================================================

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API welcome message.
    
    Provides links to documentation and basic API info.
    """
    return {
        "message": "Welcome to UIDAI Aadhaar Insights API",
        "version": API_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": f"{API_V1_PREFIX}/health",
        "endpoints": {
            "analytics": f"{API_V1_PREFIX}/analytics",
            "risk": f"{API_V1_PREFIX}/risk",
            "business": f"{API_V1_PREFIX}/business"
        },
        "timestamp": datetime.now().isoformat()
    }


# =============================================================================
# STARTUP/SHUTDOWN EVENTS
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    print("=" * 60)
    print("🚀 UIDAI Insights API Starting...")
    print("=" * 60)
    print(f"📊 Swagger Docs: http://localhost:8000/docs")
    print(f"📖 ReDoc: http://localhost:8000/redoc")
    print(f"🏥 Health Check: http://localhost:8000{API_V1_PREFIX}/health")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    print("\n🛑 UIDAI Insights API Shutting down...")


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
