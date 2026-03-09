import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from scraper.database import create_tables
from backend.routers.products import router as products_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()
    from scraper.scheduler import start_scheduler
    start_scheduler()
    yield
    # Shutdown (nothing needed)


app = FastAPI(
    title="Modest Fashion Aggregator API",
    description="Aggregates modest clothing deals from top retailers",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/scrape")
async def trigger_scrape():
    """Manually trigger a scrape (dev/admin use)."""
    import asyncio
    from scraper.run import run_all
    asyncio.create_task(run_all())
    return {"message": "Scrape started in background"}
