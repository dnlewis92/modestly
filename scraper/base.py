"""
Base scraper using Playwright. All retailer scrapers inherit from this.
"""

import asyncio
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from playwright.async_api import async_playwright, Browser, BrowserContext, Page


@dataclass
class RawProduct:
    name: str
    url: str
    image_url: str
    current_price: float
    original_price: Optional[float]
    currency: str = "USD"
    retailer: str = ""


class BaseScraper(ABC):
    retailer_name: str = ""

    # Polite delay range between requests (seconds)
    MIN_DELAY = 2.0
    MAX_DELAY = 5.0

    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    ]

    async def _get_browser_context(self, browser: Browser) -> BrowserContext:
        return await browser.new_context(
            user_agent=random.choice(self.USER_AGENTS),
            viewport={"width": 1440, "height": 900},
            locale="en-US",
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            },
        )

    async def _polite_delay(self):
        delay = random.uniform(self.MIN_DELAY, self.MAX_DELAY)
        await asyncio.sleep(delay)

    async def scrape(self) -> list[RawProduct]:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                context = await self._get_browser_context(browser)
                page = await context.new_page()
                products = await self._scrape_products(page)
                for p in products:
                    p.retailer = self.retailer_name
                return products
            finally:
                await browser.close()

    @abstractmethod
    async def _scrape_products(self, page: Page) -> list[RawProduct]:
        """Implement per-retailer scraping logic."""
        pass

    def _parse_price(self, price_str: str) -> Optional[float]:
        """Parse a price string like '$49.99' or '49.99' into a float."""
        if not price_str:
            return None
        cleaned = price_str.strip().replace("$", "").replace(",", "").replace("USD", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            return None
