"""
ModCloth scraper — uses their search JSON API.
"""

import httpx
from scraper.base import BaseScraper, RawProduct

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.modcloth.com/",
}

API_URL = "https://www.modcloth.com/shop/skirts?format=json&page={page}"


class ModClothScraper(BaseScraper):
    retailer_name = "ModCloth"

    async def scrape(self) -> list[RawProduct]:
        products = []
        try:
            async with httpx.AsyncClient(headers=HEADERS, timeout=30, follow_redirects=True) as client:
                for page in [1, 2]:
                    r = await client.get(API_URL.format(page=page))
                    if r.status_code != 200:
                        print(f"[ModCloth] API returned {r.status_code}")
                        break
                    data = r.json()
                    items = (data.get("products") or data.get("hits")
                             or data.get("results", {}).get("products", []))
                    if not items:
                        break
                    for item in items:
                        try:
                            name = item.get("name") or item.get("title", "")
                            url = item.get("url") or item.get("link", "")
                            if url and not url.startswith("http"):
                                url = "https://www.modcloth.com" + url
                            images = item.get("images", [{}])
                            img_url = images[0].get("url", "") if isinstance(images, list) and images else item.get("image", "")

                            price = item.get("price", {})
                            if isinstance(price, dict):
                                current_price = price.get("sale") or price.get("current") or price.get("amount")
                                original_price = price.get("original") or price.get("list")
                            else:
                                current_price = price
                                original_price = item.get("compare_at_price")

                            if name and url and current_price:
                                products.append(RawProduct(
                                    name=name.strip(),
                                    url=url,
                                    image_url=img_url,
                                    current_price=float(str(current_price).replace("$", "")),
                                    original_price=float(str(original_price).replace("$", "")) if original_price else None,
                                ))
                        except Exception:
                            continue
        except Exception as e:
            print(f"[ModCloth] Scrape error: {e}")

        print(f"[ModCloth] Found {len(products)} raw products")
        for p in products:
            p.retailer = self.retailer_name
        return products

    async def _scrape_products(self, page):
        return []
