"""
Main scraper orchestrator.
Runs all scrapers, classifies products with Claude, stores results in DB.
"""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from scraper.database import SessionLocal, create_tables, Product, PriceHistory
from scraper.classifier import classify_product
from scraper.scrapers import ALL_SCRAPERS
from scraper.base import RawProduct

MAX_PRICE = float(os.getenv("MAX_PRICE", "200"))
MIN_DISCOUNT_PCT = float(os.getenv("MIN_DISCOUNT_PCT", "0"))


def calc_discount(current: float, original: float | None) -> float | None:
    if original and original > current:
        return round((1 - current / original) * 100, 1)
    return None


async def process_product(raw: RawProduct, db) -> None:
    """Classify a product and upsert into the database."""
    if raw.current_price > MAX_PRICE:
        return

    # AI modesty classification
    classification = await classify_product(raw.image_url, raw.name)

    if not classification.get("is_modest"):
        return  # Skip immodest items

    discount_pct = calc_discount(raw.current_price, raw.original_price)

    existing = db.query(Product).filter(Product.url == raw.url).first()

    if existing:
        # Check for price drop
        price_dropped = raw.current_price < existing.current_price
        if price_dropped:
            # Save old price to history
            history = PriceHistory(
                product_id=existing.id,
                price=existing.current_price,
            )
            db.add(history)

        existing.current_price = raw.current_price
        existing.original_price = raw.original_price
        existing.discount_pct = discount_pct
        existing.image_url = raw.image_url
        existing.price_dropped = price_dropped
        existing.is_available = True
        existing.updated_at = datetime.utcnow()
        if price_dropped:
            existing.price_changed_at = datetime.utcnow()
    else:
        product = Product(
            retailer=raw.retailer,
            name=raw.name,
            url=raw.url,
            image_url=raw.image_url,
            current_price=raw.current_price,
            original_price=raw.original_price,
            discount_pct=discount_pct,
            currency=raw.currency,
            is_modest=classification["is_modest"],
            modest_confidence=classification.get("confidence", 0.0),
            modest_reason=classification.get("reason", ""),
            modest_length=classification.get("length", "unknown"),
            is_available=True,
            price_dropped=False,
        )
        db.add(product)

    db.commit()


async def run_scraper(scraper_class, db):
    scraper = scraper_class()
    print(f"[{scraper.retailer_name}] Starting scrape...")
    try:
        products = await scraper.scrape()
        print(f"[{scraper.retailer_name}] Found {len(products)} raw products")

        # Classify and store concurrently (but limit concurrency to avoid rate limits)
        sem = asyncio.Semaphore(3)

        async def process_with_sem(p):
            async with sem:
                await process_product(p, db)

        await asyncio.gather(*[process_with_sem(p) for p in products])
        print(f"[{scraper.retailer_name}] Done")
    except Exception as e:
        print(f"[{scraper.retailer_name}] Error: {e}")


async def run_all():
    create_tables()
    db = SessionLocal()
    try:
        for scraper_class in ALL_SCRAPERS:
            await run_scraper(scraper_class, db)
            await asyncio.sleep(2)  # Brief pause between retailers
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(run_all())
