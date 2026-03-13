"""
Abercrombie & Fitch scraper — uses their internal catalog JSON API.
No browser needed — much more reliable on cloud hosting.
"""

import httpx
from scraper.base import BaseScraper, RawProduct

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.abercrombie.com/",
}

API_URL = (
    "https://www.abercrombie.com/api/2.0/page/catalog/category/women/skirts"
    "?store=ANF&country=US&lang=en-US&start={start}&rows=48"
    "&sort=&format=json"
)


class AbercrombieScraper(BaseScraper):
    retailer_name = "Abercrombie"

    async def scrape(self) -> list[RawProduct]:
        products = []
        try:
            async with httpx.AsyncClient(headers=HEADERS, timeout=30, follow_redirects=True) as client:
                for start in [0, 48]:
                    r = await client.get(API_URL.format(start=start))
                    if r.status_code != 200:
                        print(f"[Abercrombie] API returned {r.status_code}")
                        break
                    data = r.json()
                    items = data.get("products", data.get("items", []))
                    if not items:
                        break
                    for item in items:
                        try:
                            name = item.get("name") or item.get("productName", "")
                            pid = item.get("productId") or item.get("id", "")
                            url = f"https://www.abercrombie.com/shop/us/p/{pid}"
                            images = item.get("images", [])
                            img_url = images[0].get("url", "") if images else ""
                            if img_url and not img_url.startswith("http"):
                                img_url = "https://img.abercrombie.com" + img_url

                            price_info = item.get("priceInfo", item.get("price", {}))
                            current_price = price_info.get("salePrice") or price_info.get("current") or price_info.get("price")
                            original_price = price_info.get("listPrice") or price_info.get("original")

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
            print(f"[Abercrombie] Scrape error: {e}")

        print(f"[Abercrombie] Found {len(products)} raw products")
        for p in products:
            p.retailer = self.retailer_name
        return products

    async def _scrape_products(self, page):
        return []
