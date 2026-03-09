"""
Abercrombie & Fitch scraper — Women's Skirts section.
Uses data-testid attributes which are stable.
"""

from playwright.async_api import Page, BrowserContext
from scraper.base import BaseScraper, RawProduct

JS_STEALTH = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
window.chrome = {runtime: {}};
"""

CHROME_ARGS = ["--disable-blink-features=AutomationControlled", "--no-sandbox"]


class AbercrombieScraper(BaseScraper):
    retailer_name = "Abercrombie"

    SKIRTS_URL = "https://www.abercrombie.com/shop/us/womens-skirts"

    async def _get_browser_context(self, browser) -> BrowserContext:
        ctx = await browser.new_context(
            user_agent=self.USER_AGENTS[0],
            viewport={"width": 1440, "height": 900},
        )
        await ctx.add_init_script(JS_STEALTH)
        return ctx

    async def _get_browser(self, p):
        return await p.chromium.launch(headless=True, args=CHROME_ARGS)

    async def scrape(self) -> list[RawProduct]:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await self._get_browser(p)
            try:
                context = await self._get_browser_context(browser)
                page = await context.new_page()
                products = await self._scrape_products(page)
                for prod in products:
                    prod.retailer = self.retailer_name
                return products
            finally:
                await browser.close()

    async def _scrape_products(self, page: Page) -> list[RawProduct]:
        products = []
        try:
            await page.goto(self.SKIRTS_URL, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(6000)

            cards = await page.query_selector_all("li[class*=productCard]")
            print(f"[Abercrombie] Found {len(cards)} raw cards")

            for card in cards[:60]:
                try:
                    name_el = await card.query_selector("[data-testid='catalog-product-card-name']")
                    name = await name_el.inner_text() if name_el else None

                    link_el = await card.query_selector("[data-testid='catalog-product-card-image-link']")
                    href = await link_el.get_attribute("href") if link_el else None
                    if href and not href.startswith("http"):
                        href = "https://www.abercrombie.com" + href

                    img_el = await card.query_selector("[data-testid='catalog-product-card-image']")
                    img_url = await img_el.get_attribute("src") if img_el else None

                    # Current price — data-variant="" is the active price
                    price_el = await card.query_selector(
                        "[data-testid='product-price'] .product-price-text[data-variant='']"
                    )
                    current_price_str = await price_el.inner_text() if price_el else None

                    # Original (was) price — data-variant="was"
                    orig_el = await card.query_selector(
                        "[data-testid='product-price'] .product-price-text[data-variant='was']"
                    )
                    original_price_str = await orig_el.inner_text() if orig_el else None

                    # Fallback: grab the first price shown
                    if not current_price_str:
                        fallback = await card.query_selector("[data-testid='product-price']")
                        if fallback:
                            text = await fallback.inner_text()
                            current_price_str = text.split("\n")[0].strip()

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
            print(f"[Abercrombie] Scrape error: {e}")

        return products
