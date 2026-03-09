"""
Bloomingdale's scraper — Women's Skirts section.
"""

from playwright.async_api import Page
from scraper.base import BaseScraper, RawProduct


class BloomingdalesScraper(BaseScraper):
    retailer_name = "Bloomingdale's"

    SKIRTS_URL = "https://www.bloomingdales.com/shop/womens-apparel/skirts?Nrpp=48&Ns=SORT_BY_DISCOUNT_RATE%7C1"

    async def _scrape_products(self, page: Page) -> list[RawProduct]:
        products = []
        try:
            await page.goto(self.SKIRTS_URL, wait_until="networkidle", timeout=35000)
            await page.wait_for_timeout(4000)

            items = await page.query_selector_all(".product-thumbnail, [data-testid='productThumbnail']")

            for item in items[:50]:
                try:
                    name_el = await item.query_selector(".product-title, .product-description a")
                    name = await name_el.inner_text() if name_el else None

                    link_el = await item.query_selector("a")
                    href = await link_el.get_attribute("href") if link_el else None
                    if href and not href.startswith("http"):
                        href = "https://www.bloomingdales.com" + href

                    img_el = await item.query_selector("img")
                    img_url = await img_el.get_attribute("src") if img_el else None
                    if not img_url:
                        img_url = await img_el.get_attribute("data-src") if img_el else None

                    price_el = await item.query_selector(".price-sale, .sale-price, .product-price")
                    current_price_str = await price_el.inner_text() if price_el else None

                    orig_el = await item.query_selector(".price-regular, .original-price")
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
            print(f"[Bloomingdale's] Scrape error: {e}")

        return products
