"""Order and checkout session models for UCP server."""

import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, Numeric, Integer, Text, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class CheckoutStatus(enum.Enum):
    """Checkout session status."""
    OPEN = "open"
    COMPLETE = "complete"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class OrderStatus(enum.Enum):
    """Order status."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class CheckoutSession(Base):
    """Checkout session model."""

    __tablename__ = "checkout_sessions"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    status: Mapped[CheckoutStatus] = mapped_column(
        Enum(CheckoutStatus), default=CheckoutStatus.OPEN
    )
    line_items: Mapped[dict] = mapped_column(JSON, default=list)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    
    # Customer info
    customer_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    customer_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Shipping
    shipping_address: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    shipping_method: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Payment
    payment_handler: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    payment_instrument: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    def to_response(self) -> dict:
        """Convert to UCP CheckoutResponse format."""
        return {
            "id": self.id,
            "status": self.status.value,
            "line_items": self.line_items,
            "subtotal": {
                "amount": str(self.subtotal),
                "currency": self.currency,
            },
            "total": {
                "amount": str(self.total),
                "currency": self.currency,
            },
            "customer": {
                "email": self.customer_email,
                "name": self.customer_name,
            } if self.customer_email else None,
            "shipping": {
                "address": self.shipping_address,
                "method": self.shipping_method,
            } if self.shipping_address else None,
            "payment": {
                "handler": self.payment_handler,
            } if self.payment_handler else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Order(Base):
    """Order model."""

    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    checkout_session_id: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.PENDING
    )
    
    line_items: Mapped[dict] = mapped_column(JSON, default=list)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    
    # Customer
    customer_email: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Shipping
    shipping_address: Mapped[dict] = mapped_column(JSON, nullable=False)
    shipping_method: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Payment
    payment_handler: Mapped[str] = mapped_column(String(100), nullable=False)
    payment_status: Mapped[str] = mapped_column(String(50), default="paid")
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_response(self) -> dict:
        """Convert to UCP Order format."""
        return {
            "id": self.id,
            "checkout_session_id": self.checkout_session_id,
            "status": self.status.value,
            "line_items": self.line_items,
            "subtotal": {
                "amount": str(self.subtotal),
                "currency": self.currency,
            },
            "total": {
                "amount": str(self.total),
                "currency": self.currency,
            },
            "customer": {
                "email": self.customer_email,
                "name": self.customer_name,
            },
            "shipping": {
                "address": self.shipping_address,
                "method": self.shipping_method,
            },
            "payment": {
                "handler": self.payment_handler,
                "status": self.payment_status,
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
