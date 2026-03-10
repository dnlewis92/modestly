"""
ModCloth scraper — Skirts section.
ModCloth is an independent retailer with lighter bot protection.
Great source for vintage-inspired modest styles.
"""

from playwright.async_api import Page, BrowserContext
from scraper.base import BaseScraper, RawProduct

JS_STEALTH = "Object.defineProperty(navigator,'webdriver',{get:()=>undefined}); window.chrome={runtime:{}};"
ARGS = ["--disable-blink-features=AutomationControlled", "--no-sandbox"]


class ModClothScraper(BaseScraper):
    retailer_name = "ModCloth"
    SKIRTS_URL = "https://www.modcloth.com/shop/skirts"

    async def _get_browser_context(self, browser) -> BrowserContext:
        ctx = await browser.new_context(
            user_agent=self.USER_AGENTS[0],
            viewport={"width": 1440, "height": 900},
        )
        await ctx.add_init_script(JS_STEALTH)
        return ctx

    async def scrape(self) -> list[RawProduct]:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=ARGS)
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
            await page.goto(self.SKIRTS_URL, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(4000)

            cards = await page.query_selector_all("[class*='product'], li[data-product], [data-testid*='product']")
            print(f"[ModCloth] Found {len(cards)} cards")

            for card in cards[:60]:
                try:
                    name_el = await card.query_selector("[class*='name'], [class*='title'], h2, h3, p[class]")
                    name = await name_el.inner_text() if name_el else None

                    link_el = await card.query_selector("a")
                    href = await link_el.get_attribute("href") if link_el else None
                    if href and not href.startswith("http"):
                        href = "https://www.modcloth.com" + href

                    img_el = await card.query_selector("img")
                    img_url = await img_el.get_attribute("src") if img_el else None
                    if not img_url:
                        img_url = await img_el.get_attribute("data-src") if img_el else None

                    price_els = await card.query_selector_all("[class*='price'], [class*='Price']")
                    prices = []
                    for el in price_els:
                        p = self._parse_price((await el.inner_text()).split("\n")[0])
                        if p:
                            prices.append(p)

                    current_price = min(prices) if prices else None
                    original_price = max(prices) if len(prices) > 1 else None

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
            print(f"[ModCloth] Scrape error: {e}")
        return products
