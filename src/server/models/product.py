"""Product model for UCP server."""

from decimal import Decimal
from typing import Optional
from sqlalchemy import String, Numeric, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Product(Base):
    """Product catalog model."""

    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    inventory: Mapped[int] = mapped_column(Integer, default=0)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    def to_dict(self) -> dict:
        """Convert product to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": str(self.price),
            "currency": self.currency,
            "inventory": self.inventory,
            "image_url": self.image_url,
            "category": self.category,
        }

    def to_line_item(self, quantity: int = 1) -> dict:
        """Convert product to UCP line item format."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "quantity": quantity,
            "unit_price": {
                "amount": str(self.price),
                "currency": self.currency,
            },
            "total_price": {
                "amount": str(self.price * quantity),
                "currency": self.currency,
            },
        }
