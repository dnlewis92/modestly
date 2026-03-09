"""
Zara scraper — Women's Skirts section.
Zara is heavily JS-rendered and has Cloudflare protection.
We use a slower, more human-like approach.
"""

import asyncio
from playwright.async_api import Page
from scraper.base import BaseScraper, RawProduct


class ZaraScraper(BaseScraper):
    retailer_name = "Zara"

    # Zara skirts category for US
    SKIRTS_URL = "https://www.zara.com/us/en/woman-skirts-l1299.html"

    # Zara's Cloudflare protection is aggressive; increase delays
    MIN_DELAY = 4.0
    MAX_DELAY = 8.0

    async def _scrape_products(self, page: Page) -> list[RawProduct]:
        products = []
        try:
            # Mimic human behavior more closely
            await page.goto(self.SKIRTS_URL, wait_until="domcontentloaded", timeout=40000)
            await asyncio.sleep(3)
            await page.mouse.move(400, 300)
            await asyncio.sleep(1)
            await page.evaluate("window.scrollTo(0, 500)")
            await asyncio.sleep(2)

            items = await page.query_selector_all("li.product-grid-product")

            for item in items[:50]:
                try:
                    name_el = await item.query_selector(".product-grid-product-info__name")
                    name = await name_el.inner_text() if name_el else None

                    link_el = await item.query_selector("a.product-grid-product__figure-link")
                    href = await link_el.get_attribute("href") if link_el else None

                    img_el = await item.query_selector("img.media-image__image")
                    img_url = await img_el.get_attribute("src") if img_el else None
                    if not img_url:
                        img_url = await img_el.get_attribute("data-src") if img_el else None

                    # Current price
                    price_el = await item.query_selector(".price__amount-current .money-amount__main")
                    current_price_str = await price_el.inner_text() if price_el else None

                    # Original price (if discounted)
                    orig_el = await item.query_selector(".price__amount-original .money-amount__main")
                    original_price_str = await orig_el.inner_text() if orig_el else None

                    if name and href and img_url and current_price_str:
                        current_price = self._parse_price(current_price_str)
                        original_price = self._parse_price(original_price_str) if original_price_str else None
                        if current_price:
                            products.append(RawProduct(
                                name=name.strip(),
                                url=href,
                                image_url=img_url,
                                current_price=current_price,
                                original_price=original_price,
                            ))
                except Exception:
                    continue

            await self._polite_delay()
        except Exception as e:
            print(f"[Zara] Scrape error: {e}")

        return products
