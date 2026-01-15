"""UCP Custom Server - Main FastAPI Application."""

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models import init_db
from .capabilities import discovery_router, checkout_router
from .capabilities.chat import router as chat_router
from .capabilities.products import router as products_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(
    title="UCP Custom Shop",
    version="0.1.0",
    description="Custom UCP-compliant merchant server with AI agent",
    lifespan=lifespan,
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(discovery_router)
app.include_router(checkout_router)
app.include_router(chat_router)
app.include_router(products_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ucp-custom-shop"}


def main():
    """Run the server."""
    uvicorn.run(
        "src.server.app:app",
        host="0.0.0.0",
        port=8183,
        reload=True,
    )


if __name__ == "__main__":
    main()
