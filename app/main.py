"""
ActivityGuide Backend - FastAPI Application
City-first event discovery platform for parents
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import engine, Base
from app.core.cache import redis_client
from app.services.sync import start_sync_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting ActivityGuide Backend...")
    
    # Create database tables
    try:
        print("📊 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created")
    except Exception as e:
        print(f"❌ Database creation error: {e}")
        # Continue anyway - tables might already exist
    
    # Test Redis connection
    try:
        if redis_client:
            await redis_client.ping()
            print("✅ Redis connected")
        else:
            print("⚠️ Redis not available - running without cache")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
    
    # Start background sync scheduler (no default zip codes)
    # start_sync_scheduler()  # Disabled - requires explicit zip codes
    print("⚠️ Background sync disabled - no default zip codes configured")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down ActivityGuide Backend...")


# Create FastAPI app
app = FastAPI(
    title="ActivityGuide API",
    description="City-first event discovery platform for parents",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "activityguide-api"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
