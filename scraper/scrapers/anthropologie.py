"""
Anthropologie scraper — Women's Skirts section.
Anthropologie uses React. We use Playwright to render and parse.
"""

from playwright.async_api import Page
from scraper.base import BaseScraper, RawProduct


class AnthropologieScraper(BaseScraper):
    retailer_name = "Anthropologie"

    SKIRTS_URL = "https://www.anthropologie.com/skirts?priceFilter=0-200"

    async def _scrape_products(self, page: Page) -> list[RawProduct]:
        products = []
        try:
            await page.goto(self.SKIRTS_URL, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(4000)

            items = await page.query_selector_all("[data-testid='product-tile']")

            # fallback selector
            if not items:
                items = await page.query_selector_all(".product-tile, .c-product-tile")

            for item in items[:50]:
                try:
                    name_el = await item.query_selector("[data-testid='product-tile-name'], .product-tile__name")
                    name = await name_el.inner_text() if name_el else None

                    link_el = await item.query_selector("a")
                    href = await link_el.get_attribute("href") if link_el else None
                    if href and not href.startswith("http"):
                        href = "https://www.anthropologie.com" + href

                    img_el = await item.query_selector("img")
                    img_url = await img_el.get_attribute("src") if img_el else None
                    if not img_url:
                        img_url = await img_el.get_attribute("data-src") if img_el else None

                    price_el = await item.query_selector("[data-testid='product-price'], .product-tile__price")
                    price_text = await price_el.inner_text() if price_el else ""

                    # Anthropologie often shows "Was $X Now $Y" or just "$X"
                    current_price = None
                    original_price = None

                    if "Now" in price_text or "Sale" in price_text.title():
                        parts = price_text.replace("Was", "").replace("Now", "").strip().split()
                        prices = [self._parse_price(p) for p in parts if self._parse_price(p)]
                        if len(prices) >= 2:
                            original_price, current_price = sorted(prices, reverse=True)[:2]
                        elif len(prices) == 1:
                            current_price = prices[0]
                    else:
                        current_price = self._parse_price(price_text.split("\n")[0])

                    if name and href and img_url and current_price:
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
            print(f"[Anthropologie] Scrape error: {e}")

        return products
