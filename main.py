from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import logging
import os

from app.core.config import settings
from app.database import init_db, close_db
from app.routers import clients, websites, scans, scheduler, schedules, templates, htmx

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
    title="SEO Auditing Solution - Nova Tools",
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
app.include_router(schedules.router)
app.include_router(scheduler.router)
app.include_router(templates.router)
app.include_router(htmx.router)

# Mount static files (after routes to avoid conflicts)
static_dir = os.path.join(os.path.dirname(__file__), "app", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def root():
    """Redirect to modern templated interface"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/templated/")


@app.get("/app")
async def web_app():
    """Alternative route for web interface - redirect to templated"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/templated/")

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