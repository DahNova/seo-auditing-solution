from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.database import init_db, close_db
from app.routers import clients, websites, scans

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logging.info("Starting SEO Auditing Solution...")
    await init_db()
    logging.info("Database initialized successfully")
    yield
    # Shutdown
    logging.info("Shutting down...")
    await close_db()
    logging.info("Database connections closed")

app = FastAPI(
    title="SEO Auditing Solution - Dexa Agency",
    description="Systematic SEO monitoring and auditing tool for 200+ clients",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(clients.router, prefix="/api/v1")
app.include_router(websites.router, prefix="/api/v1")
app.include_router(scans.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "SEO Auditing Solution API - Dexa Agency"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.debug,
        workers=1 if settings.debug else settings.workers
    )