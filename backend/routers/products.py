from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from pydantic import BaseModel

from scraper.database import get_db, Product

router = APIRouter(prefix="/api")


class ProductOut(BaseModel):
    id: int
    retailer: str
    name: str
    url: str
    image_url: Optional[str]
    current_price: Optional[float]
    original_price: Optional[float]
    discount_pct: Optional[float]
    currency: str
    modest_length: Optional[str]
    price_dropped: bool
    scraped_at: str
    price_changed_at: Optional[str]

    class Config:
        from_attributes = True

    def model_post_init(self, __context):
        # Convert datetimes to ISO strings
        pass


class ProductsResponse(BaseModel):
    items: list[dict]
    total: int
    page: int
    pages: int


@router.get("/products", response_model=ProductsResponse)
def list_products(
    retailer: Optional[str] = Query(None),
    min_price: float = Query(0),
    max_price: float = Query(200),
    min_discount: float = Query(0, description="Minimum discount % (0-100)"),
    price_dropped: Optional[bool] = Query(None),
    sort_by: str = Query("discount", enum=["discount", "price_low", "price_high", "newest", "price_drop"]),
    page: int = Query(1, ge=1),
    limit: int = Query(48, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Product).filter(
        Product.is_modest == True,
        Product.is_available == True,
        Product.current_price >= min_price,
        Product.current_price <= max_price,
    )

    if retailer:
        retailers = [r.strip() for r in retailer.split(",")]
        q = q.filter(Product.retailer.in_(retailers))

    if min_discount > 0:
        q = q.filter(Product.discount_pct >= min_discount)

    if price_dropped is True:
        q = q.filter(Product.price_dropped == True)

    # Sorting
    if sort_by == "discount":
        q = q.order_by(desc(Product.discount_pct).nullslast())
    elif sort_by == "price_low":
        q = q.order_by(asc(Product.current_price))
    elif sort_by == "price_high":
        q = q.order_by(desc(Product.current_price))
    elif sort_by == "newest":
        q = q.order_by(desc(Product.scraped_at))
    elif sort_by == "price_drop":
        q = q.order_by(desc(Product.price_dropped), desc(Product.price_changed_at))

    total = q.count()
    offset = (page - 1) * limit
    items = q.offset(offset).limit(limit).all()

    def serialize(p: Product) -> dict:
        return {
            "id": p.id,
            "retailer": p.retailer,
            "name": p.name,
            "url": p.url,
            "image_url": p.image_url,
            "current_price": p.current_price,
            "original_price": p.original_price,
            "discount_pct": p.discount_pct,
            "currency": p.currency,
            "modest_length": p.modest_length,
            "price_dropped": p.price_dropped,
            "scraped_at": p.scraped_at.isoformat() if p.scraped_at else None,
            "price_changed_at": p.price_changed_at.isoformat() if p.price_changed_at else None,
        }

    return {
        "items": [serialize(p) for p in items],
        "total": total,
        "page": page,
        "pages": max(1, -(-total // limit)),  # ceiling division
    }


@router.get("/retailers")
def list_retailers(db: Session = Depends(get_db)):
    from sqlalchemy import func
    results = (
        db.query(Product.retailer, func.count(Product.id).label("count"))
        .filter(Product.is_modest == True, Product.is_available == True)
        .group_by(Product.retailer)
        .all()
    )
    return [{"name": r.retailer, "count": r.count} for r in results]


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(Product).filter(Product.is_modest == True).count()
    on_sale = db.query(Product).filter(
        Product.is_modest == True,
        Product.discount_pct >= 20,
    ).count()
    price_drops = db.query(Product).filter(
        Product.is_modest == True,
        Product.price_dropped == True,
    ).count()
    return {"total_items": total, "on_sale": on_sale, "price_drops": price_drops}
