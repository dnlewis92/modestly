"""
ASOS scraper — Women's Skirts section.
ASOS returns product data in embedded JSON (__NEXT_DATA__ or via their search API).
"""

import json
from playwright.async_api import Page
from scraper.base import BaseScraper, RawProduct


class AsosScraper(BaseScraper):
    retailer_name = "ASOS"

    SKIRTS_URL = "https://www.asos.com/women/skirts/cat/?cid=2638&currentpricerange=0-200&floor=0&ceiling=200"

    async def _scrape_products(self, page: Page) -> list[RawProduct]:
        products = []
        try:
            await page.goto(self.SKIRTS_URL, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)

            # Try to intercept the product list from embedded data
            content = await page.content()
            items = await page.query_selector_all("article[data-auto-id='productTile']")

            for item in items[:50]:  # Limit to first 50 per scrape
                try:
                    name_el = await item.query_selector("[data-auto-id='productTileDescription']")
                    name = await name_el.inner_text() if name_el else None

                    link_el = await item.query_selector("a")
                    href = await link_el.get_attribute("href") if link_el else None
                    if href and not href.startswith("http"):
                        href = "https://www.asos.com" + href

                    img_el = await item.query_selector("img")
                    img_url = await img_el.get_attribute("src") if img_el else None
                    if img_url and img_url.startswith("//"):
                        img_url = "https:" + img_url

                    # Current price
                    price_el = await item.query_selector("[data-auto-id='productTilePrice'] span:first-child")
                    current_price_str = await price_el.inner_text() if price_el else None

                    # Original price (if on sale)
                    orig_el = await item.query_selector("[data-auto-id='productTilePrice'] span[aria-label*='Was']")
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
            print(f"[ASOS] Scrape error: {e}")

        return products
