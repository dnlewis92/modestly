"""
Banana Republic scraper — uses Gap group's search JSON API.
"""

import httpx
from scraper.base import BaseScraper, RawProduct

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://bananarepublic.gap.com/",
}

API_URL = (
    "https://bananarepublic.gap.com/browse/searchproducts.do"
    "?searchQuery=skirt&searchCategory=womenBottoms&format=json&count=48&offset={offset}"
)


class BananaRepublicScraper(BaseScraper):
    retailer_name = "Banana Republic"

    async def scrape(self) -> list[RawProduct]:
        products = []
        try:
            async with httpx.AsyncClient(headers=HEADERS, timeout=30, follow_redirects=True) as client:
                for offset in [0, 48]:
                    r = await client.get(API_URL.format(offset=offset))
                    if r.status_code != 200:
                        print(f"[Banana Republic] API returned {r.status_code}")
                        break
                    data = r.json()
                    items = (data.get("products") or data.get("searchResults", {}).get("products", []))
                    if not items:
                        break
                    for item in items:
                        try:
                            name = item.get("productName") or item.get("name", "")
                            pid = item.get("productId") or item.get("id", "")
                            url = f"https://bananarepublic.gap.com/browse/product.do?pid={pid}"
                            images = item.get("images", [])
                            img_url = images[0] if isinstance(images, list) and images else ""
                            if isinstance(img_url, dict):
                                img_url = img_url.get("src", "")

                            current_price = item.get("salePrice") or item.get("currentPrice") or item.get("price")
                            original_price = item.get("listPrice") or item.get("originalPrice")

                            if name and url and current_price:
                                products.append(RawProduct(
                                    name=name.strip(),
                                    url=url,
                                    image_url=img_url,
                                    current_price=float(str(current_price).replace("$", "").replace(",", "")),
                                    original_price=float(str(original_price).replace("$", "").replace(",", "")) if original_price else None,
                                ))
                        except Exception:
                            continue
        except Exception as e:
            print(f"[Banana Republic] Scrape error: {e}")

        print(f"[Banana Republic] Found {len(products)} raw products")
        for p in products:
            p.retailer = self.retailer_name
        return products

    async def _scrape_products(self, page):
        return []
