"""
Nordstrom Rack scraper — Women's Skirts section.
Nordstrom Rack uses heavy JS. Products are rendered client-side.
"""

from playwright.async_api import Page
from scraper.base import BaseScraper, RawProduct


class NordstromRackScraper(BaseScraper):
    retailer_name = "Nordstrom Rack"

    SKIRTS_URL = "https://www.nordstromrack.com/c/women/clothing/skirts?sort=PriceAscending"

    async def _scrape_products(self, page: Page) -> list[RawProduct]:
        products = []
        try:
            await page.goto(self.SKIRTS_URL, wait_until="networkidle", timeout=35000)
            await page.wait_for_timeout(4000)

            items = await page.query_selector_all("[data-testid='product-card'], .product-card")

            for item in items[:50]:
                try:
                    name_el = await item.query_selector("[data-testid='product-title'], .product-title")
                    name = await name_el.inner_text() if name_el else None

                    link_el = await item.query_selector("a")
                    href = await link_el.get_attribute("href") if link_el else None
                    if href and not href.startswith("http"):
                        href = "https://www.nordstromrack.com" + href

                    img_el = await item.query_selector("img")
                    img_url = await img_el.get_attribute("src") if img_el else None

                    price_el = await item.query_selector("[data-testid='price'], .sale-price, .product-price")
                    current_price_str = await price_el.inner_text() if price_el else None

                    orig_el = await item.query_selector("[data-testid='original-price'], .original-price")
                    original_price_str = await orig_el.inner_text() if orig_el else None

                    if name and href and img_url and current_price_str:
                        current_price = self._parse_price(current_price_str.split("\n")[0])
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
            print(f"[Nordstrom Rack] Scrape error: {e}")

        return products
