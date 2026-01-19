"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   ██╗  ██╗    ██╗  ██╗          ██╗  ██╗ ██████╗ ██╗     ██████╗ ██╗███╗   ██╗ ██████╗ ███████╗  ║
║   ██║  ██║    ██║  ██║          ██║  ██║██╔═══██╗██║     ██╔══██╗██║████╗  ██║██╔════╝ ██╔════╝  ║
║   ███████║    ███████║          ███████║██║   ██║██║     ██║  ██║██║██╔██╗ ██║██║  ███╗███████╗  ║
║   ██╔══██║    ██╔══██║          ██╔══██║██║   ██║██║     ██║  ██║██║██║╚██╗██║██║   ██║╚════██║  ║
║   ██║  ██║    ██║  ██║          ██║  ██║╚██████╔╝███████╗██████╔╝██║██║ ╚████║╚██████╔╝███████║  ║
║   ╚═╝  ╚═╝    ╚═╝  ╚═╝          ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═════╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝  ║
║                                                                           ║
║                 BOSQUE COUNTY MINERAL & COMMODITIES EXCHANGE             ║
║                        Main FastAPI Application                          ║
║                                                                           ║
║   Operator:    HH Holdings LLC / Bevans Real Estate                      ║
║   Location:    397 Highway 22, Clifton, TX 76634                         ║
║   Broker:      Biri Bevans, Designated Broker                            ║
║   Module:      Backend API Server                                        ║
║                                                                           ║
║   Stack:       FastAPI • PostgreSQL • Redis • WebSocket                  ║
║   Version:     1.0.0 - Production Ready                                  ║
║   Copyright:   © 2026 HH Holdings LLC. All rights reserved.              ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

BCMCE Platform - Main FastAPI Application
Bosque County Mineral & Commodities Exchange
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging
from dotenv import load_dotenv
import os

from api import pricing, options, suppliers, county

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting BCMCE Platform API")
    # Startup: Initialize database connections, cache, etc.
    yield
    # Shutdown: Clean up resources
    logger.info("Shutting down BCMCE Platform API")


# Initialize FastAPI application
app = FastAPI(
    title="BCMCE Platform API",
    description="Bosque County Mineral & Commodities Exchange - Real-time marketplace API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include API routers
app.include_router(pricing.router, prefix="/api/v1/pricing", tags=["Pricing"])
app.include_router(options.router, prefix="/api/v1/options", tags=["Options"])
app.include_router(suppliers.router, prefix="/api/v1/suppliers", tags=["Suppliers"])
app.include_router(county.router, prefix="/api/v1/county", tags=["County"])


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "service": "BCMCE Platform API",
        "version": "1.0.0",
        "status": "operational",
        "market": "Bosque County, TX"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    from database import check_database_health
    from config import get_settings
    import redis
    from datetime import datetime

    settings = get_settings()

    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0",
        "services": {}
    }

    # Check database
    try:
        db_healthy = check_database_health()
        health_status["services"]["database"] = {
            "status": "connected" if db_healthy else "disconnected",
            "type": "PostgreSQL"
        }
    except Exception as e:
        health_status["services"]["database"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["status"] = "degraded"

    # Check Redis cache
    try:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        redis_client.ping()
        health_status["services"]["cache"] = {
            "status": "connected",
            "type": "Redis"
        }
        redis_client.close()
    except Exception as e:
        health_status["services"]["cache"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["status"] = "degraded"

    return health_status


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("API_DEBUG", "False") == "True"
    )
