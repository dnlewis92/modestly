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


@router.post("/seed")
def seed_products(db: Session = Depends(get_db)):
    """Seed the database with sample modest clothing products."""
    from datetime import datetime
    sample = [
        # Abercrombie
        dict(retailer="Abercrombie", name="A&F Linen-Blend Midi Skirt", url="https://www.abercrombie.com/shop/us/p/linen-blend-midi-skirt-57264319", image_url="https://img.abercrombie.com/is/image/anf/KIC_157-3204-0580-278_prod1", current_price=59.95, original_price=89.95, discount_pct=33.4, modest_length="midi"),
        dict(retailer="Abercrombie", name="A&F Smocked-Waist Maxi Skirt", url="https://www.abercrombie.com/shop/us/p/smocked-waist-maxi-skirt-57264320", image_url="https://img.abercrombie.com/is/image/anf/KIC_157-3204-0580-279_prod1", current_price=69.95, original_price=99.95, discount_pct=30.0, modest_length="maxi"),
        dict(retailer="Abercrombie", name="A&F High-Rise Pleated Midi Skirt", url="https://www.abercrombie.com/shop/us/p/high-rise-pleated-midi-skirt-57264321", image_url="https://img.abercrombie.com/is/image/anf/KIC_157-3204-0580-280_prod1", current_price=79.95, original_price=None, discount_pct=None, modest_length="midi"),
        # LOFT
        dict(retailer="LOFT", name="Linen-Blend Midi Skirt", url="https://www.loft.com/linen-blend-midi-skirt/product/p/123401", image_url="https://asset.loft.com/is/image/AnnTaylor/AN_467745_6001_AY", current_price=59.50, original_price=89.50, discount_pct=33.5, modest_length="midi"),
        dict(retailer="LOFT", name="Button-Front Maxi Skirt", url="https://www.loft.com/button-front-maxi-skirt/product/p/123402", image_url="https://asset.loft.com/is/image/AnnTaylor/AN_467745_6002_AY", current_price=74.50, original_price=99.50, discount_pct=25.1, modest_length="maxi"),
        dict(retailer="LOFT", name="Floral Midi Wrap Skirt", url="https://www.loft.com/floral-midi-wrap-skirt/product/p/123403", image_url="https://asset.loft.com/is/image/AnnTaylor/AN_467745_6003_AY", current_price=89.50, original_price=None, discount_pct=None, modest_length="midi"),
        # Madewell
        dict(retailer="Madewell", name="The Tiered Maxi Skirt", url="https://www.madewell.com/the-tiered-maxi-skirt-MA963.html", image_url="https://i8.amplience.net/i/bcmadewell/MA963_GF3293_d", current_price=78.00, original_price=128.00, discount_pct=39.1, modest_length="maxi"),
        dict(retailer="Madewell", name="Smocked-Waist Midi Skirt", url="https://www.madewell.com/smocked-waist-midi-skirt-NM489.html", image_url="https://i8.amplience.net/i/bcmadewell/NM489_GF3294_d", current_price=68.00, original_price=98.00, discount_pct=30.6, modest_length="midi"),
        dict(retailer="Madewell", name="A-Line Midi Skirt in Linen", url="https://www.madewell.com/a-line-midi-skirt-in-linen-LK239.html", image_url="https://i8.amplience.net/i/bcmadewell/LK239_GF3295_d", current_price=88.00, original_price=None, discount_pct=None, modest_length="midi"),
        # Banana Republic
        dict(retailer="Banana Republic", name="Pleated Linen Midi Skirt", url="https://bananarepublic.gap.com/browse/product.do?pid=775221002", image_url="https://bananarepublic.gap.com/webcontent/0016/849/568/cn16849568.jpg", current_price=89.99, original_price=149.99, discount_pct=40.0, modest_length="midi"),
        dict(retailer="Banana Republic", name="A-Line Maxi Skirt", url="https://bananarepublic.gap.com/browse/product.do?pid=775221003", image_url="https://bananarepublic.gap.com/webcontent/0016/849/569/cn16849569.jpg", current_price=99.99, original_price=169.99, discount_pct=41.2, modest_length="maxi"),
        dict(retailer="Banana Republic", name="Satin Midi Skirt", url="https://bananarepublic.gap.com/browse/product.do?pid=775221004", image_url="https://bananarepublic.gap.com/webcontent/0016/849/570/cn16849570.jpg", current_price=119.99, original_price=None, discount_pct=None, modest_length="midi"),
        # J.Crew
        dict(retailer="J.Crew", name="Tall A-Line Midi Skirt", url="https://www.jcrew.com/p/womens-clothing/skirts/midi/tall-a-line-midi-skirt/AZ394", image_url="https://cache.jcrew.com/s7-img-facade/AZ394_GQ3929_m", current_price=79.50, original_price=118.00, discount_pct=32.6, modest_length="midi"),
        dict(retailer="J.Crew", name="Pleated Georgette Midi Skirt", url="https://www.jcrew.com/p/womens-clothing/skirts/midi/pleated-georgette-midi-skirt/BG291", image_url="https://cache.jcrew.com/s7-img-facade/BG291_GQ3930_m", current_price=89.50, original_price=128.00, discount_pct=30.1, modest_length="midi"),
        dict(retailer="J.Crew", name="Linen-Blend Maxi Skirt", url="https://www.jcrew.com/p/womens-clothing/skirts/maxi/linen-blend-maxi-skirt/CK182", image_url="https://cache.jcrew.com/s7-img-facade/CK182_GQ3931_m", current_price=98.00, original_price=None, discount_pct=None, modest_length="maxi"),
        # ModCloth
        dict(retailer="ModCloth", name="Vintage-Inspired Midi Skirt", url="https://www.modcloth.com/shop/skirts/vintage-midi-skirt/product/p123401", image_url="https://images.modcloth.com/images/1/large/vintage-midi.jpg", current_price=54.99, original_price=79.99, discount_pct=31.3, modest_length="midi"),
        dict(retailer="ModCloth", name="Floral Maxi Wrap Skirt", url="https://www.modcloth.com/shop/skirts/floral-maxi-wrap-skirt/product/p123402", image_url="https://images.modcloth.com/images/1/large/floral-maxi.jpg", current_price=64.99, original_price=89.99, discount_pct=27.8, modest_length="maxi"),
        dict(retailer="ModCloth", name="Retro Polka Dot Midi Skirt", url="https://www.modcloth.com/shop/skirts/retro-polka-dot-midi-skirt/product/p123403", image_url="https://images.modcloth.com/images/1/large/polka-dot-midi.jpg", current_price=49.99, original_price=None, discount_pct=None, modest_length="midi"),
    ]

    added = 0
    for p in sample:
        if db.query(Product).filter(Product.url == p["url"]).first():
            continue
        db.add(Product(
            retailer=p["retailer"],
            name=p["name"],
            url=p["url"],
            image_url=p["image_url"],
            current_price=p["current_price"],
            original_price=p["original_price"],
            discount_pct=p["discount_pct"],
            currency="USD",
            is_modest=True,
            modest_confidence=1.0,
            modest_reason="seeded",
            modest_length=p["modest_length"],
            is_available=True,
            price_dropped=False,
            scraped_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ))
        added += 1

    db.commit()
    return {"seeded": added}


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
