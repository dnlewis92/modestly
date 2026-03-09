import os
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean,
    DateTime, ForeignKey, Text
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/modest_fashion.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    retailer = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    image_url = Column(String)
    current_price = Column(Float)
    original_price = Column(Float)
    discount_pct = Column(Float, index=True)
    currency = Column(String, default="USD")

    # Modesty classification
    is_modest = Column(Boolean, default=False, index=True)
    modest_confidence = Column(Float)
    modest_reason = Column(Text)
    modest_length = Column(String)  # mini/knee/midi/maxi/unknown

    # Status
    is_available = Column(Boolean, default=True)
    price_dropped = Column(Boolean, default=False, index=True)
    price_changed_at = Column(DateTime)

    scraped_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    price = Column(Float)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="price_history")


def create_tables():
    os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
