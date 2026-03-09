"""
APScheduler integration — runs scraper every N hours.
Called from the FastAPI app startup.
"""

import asyncio
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

INTERVAL_HOURS = int(os.getenv("SCRAPE_INTERVAL_HOURS", "6"))


def start_scheduler():
    from scraper.run import run_all

    scheduler.add_job(
        lambda: asyncio.create_task(run_all()),
        "interval",
        hours=INTERVAL_HOURS,
        id="scrape_job",
        replace_existing=True,
    )
    scheduler.start()
    print(f"Scheduler started — scraping every {INTERVAL_HOURS} hours")
