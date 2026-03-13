"""
LOFT scraper — uses their search JSON API.
"""

import httpx
from scraper.base import BaseScraper, RawProduct

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.loft.com/",
}

API_URL = (
    "https://www.loft.com/api/search"
    "?q=skirt&start={start}&sz=48&format=json"
)


class LoftScraper(BaseScraper):
    retailer_name = "LOFT"

    async def scrape(self) -> list[RawProduct]:
        products = []
        try:
            async with httpx.AsyncClient(headers=HEADERS, timeout=30, follow_redirects=True) as client:
                for start in [0, 48]:
                    r = await client.get(API_URL.format(start=start))
                    if r.status_code != 200:
                        print(f"[LOFT] API returned {r.status_code}")
                        break
                    data = r.json()
                    hits = (data.get("hits") or data.get("products")
                            or data.get("results", {}).get("hits", []))
                    if not hits:
                        break
                    for item in hits:
                        try:
                            name = item.get("product_name") or item.get("name", "")
                            url = item.get("url") or item.get("product_url", "")
                            if url and not url.startswith("http"):
                                url = "https://www.loft.com" + url
                            images = item.get("images", [{}])
                            img_url = images[0].get("url", "") if isinstance(images, list) and images else ""

                            price = item.get("price", {})
                            if isinstance(price, dict):
                                current_price = price.get("sales", {}).get("value") or price.get("current")
                                original_price = price.get("list", {}).get("value") or price.get("original")
                            else:
                                current_price = price
                                original_price = None

                            if name and url and current_price:
                                products.append(RawProduct(
                                    name=name.strip(),
                                    url=url,
                                    image_url=img_url,
                                    current_price=float(current_price),
                                    original_price=float(original_price) if original_price else None,
                                ))
                        except Exception:
                            continue
        except Exception as e:
            print(f"[LOFT] Scrape error: {e}")

        print(f"[LOFT] Found {len(products)} raw products")
        for p in products:
            p.retailer = self.retailer_name
        return products

    async def _scrape_products(self, page):
        return []
