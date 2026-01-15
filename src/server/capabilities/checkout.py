"""UCP Checkout capability - session management."""

import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import get_db, CheckoutSession, CheckoutStatus, Product, Order, OrderStatus

router = APIRouter()


# --- Pydantic Schemas ---

class LineItemRequest(BaseModel):
    """Line item in checkout request."""
    product_id: str
    quantity: int = 1


class AddressRequest(BaseModel):
    """Address in checkout request."""
    line1: str
    line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str = "US"


class CustomerRequest(BaseModel):
    """Customer info in checkout request."""
    email: str
    name: Optional[str] = None


class PaymentRequest(BaseModel):
    """Payment info in checkout request."""
    handler: str = "mock_payment_handler"
    instrument: Optional[dict] = None


class CheckoutCreateRequest(BaseModel):
    """Request to create a checkout session."""
    line_items: List[LineItemRequest]
    customer: Optional[CustomerRequest] = None


class CheckoutUpdateRequest(BaseModel):
    """Request to update a checkout session."""
    customer: Optional[CustomerRequest] = None
    shipping_address: Optional[AddressRequest] = None
    shipping_method: Optional[str] = None
    payment: Optional[PaymentRequest] = None


class CheckoutCompleteRequest(BaseModel):
    """Request to complete a checkout session."""
    payment: PaymentRequest


# --- Helper Functions ---

async def get_checkout_by_id(
    checkout_id: str, db: AsyncSession
) -> CheckoutSession:
    """Get checkout session by ID or raise 404."""
    result = await db.execute(
        select(CheckoutSession).where(CheckoutSession.id == checkout_id)
    )
    checkout = result.scalar_one_or_none()
    if not checkout:
        raise HTTPException(status_code=404, detail="Checkout session not found")
    return checkout


async def get_product_by_id(product_id: str, db: AsyncSession) -> Product:
    """Get product by ID or raise 404."""
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return product


# --- Routes ---

@router.post("/checkout-sessions", status_code=201)
async def create_checkout(
    body: CheckoutCreateRequest,
    db: AsyncSession = Depends(get_db),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    request_id: Optional[str] = Header(None, alias="Request-Id"),
) -> dict:
    """Create a new checkout session."""
    
    # Generate checkout ID
    checkout_id = f"cs_{uuid.uuid4().hex[:16]}"
    
    # Build line items and calculate total
    line_items = []
    subtotal = Decimal("0")
    currency = "USD"
    
    for item in body.line_items:
        product = await get_product_by_id(item.product_id, db)
        
        # Check inventory
        if product.inventory < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient inventory for {product.name}"
            )
        
        line_item = product.to_line_item(item.quantity)
        line_items.append(line_item)
        subtotal += product.price * item.quantity
        currency = product.currency
    
    # Create checkout session
    checkout = CheckoutSession(
        id=checkout_id,
        status=CheckoutStatus.OPEN,
        line_items=line_items,
        subtotal=subtotal,
        total=subtotal,  # Will add shipping/tax later
        currency=currency,
        customer_email=body.customer.email if body.customer else None,
        customer_name=body.customer.name if body.customer else None,
        expires_at=datetime.utcnow() + timedelta(hours=24),
    )
    
    db.add(checkout)
    await db.commit()
    await db.refresh(checkout)
    
    return checkout.to_response()


@router.get("/checkout-sessions/{checkout_id}")
async def get_checkout(
    checkout_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get a checkout session by ID."""
    checkout = await get_checkout_by_id(checkout_id, db)
    return checkout.to_response()


@router.put("/checkout-sessions/{checkout_id}")
async def update_checkout(
    checkout_id: str,
    body: CheckoutUpdateRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Update a checkout session."""
    checkout = await get_checkout_by_id(checkout_id, db)
    
    if checkout.status != CheckoutStatus.OPEN:
        raise HTTPException(
            status_code=400, 
            detail="Cannot update a closed checkout session"
        )
    
    # Update fields
    if body.customer:
        checkout.customer_email = body.customer.email
        checkout.customer_name = body.customer.name
    
    if body.shipping_address:
        checkout.shipping_address = body.shipping_address.model_dump()
    
    if body.shipping_method:
        checkout.shipping_method = body.shipping_method
    
    if body.payment:
        checkout.payment_handler = body.payment.handler
        checkout.payment_instrument = body.payment.instrument
    
    checkout.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(checkout)
    
    return checkout.to_response()


@router.post("/checkout-sessions/{checkout_id}/complete")
async def complete_checkout(
    checkout_id: str,
    body: CheckoutCompleteRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Complete a checkout and create an order."""
    checkout = await get_checkout_by_id(checkout_id, db)
    
    if checkout.status != CheckoutStatus.OPEN:
        raise HTTPException(
            status_code=400,
            detail="Checkout session is not open"
        )
    
    # Validate required fields
    if not checkout.customer_email:
        raise HTTPException(status_code=400, detail="Customer email is required")
    if not checkout.shipping_address:
        raise HTTPException(status_code=400, detail="Shipping address is required")
    if not checkout.shipping_method:
        raise HTTPException(status_code=400, detail="Shipping method is required")
    
    # Process payment (mock)
    checkout.payment_handler = body.payment.handler
    checkout.payment_instrument = body.payment.instrument
    
    # Create order
    order_id = f"ord_{uuid.uuid4().hex[:16]}"
    order = Order(
        id=order_id,
        checkout_session_id=checkout.id,
        status=OrderStatus.CONFIRMED,
        line_items=checkout.line_items,
        subtotal=checkout.subtotal,
        total=checkout.total,
        currency=checkout.currency,
        customer_email=checkout.customer_email,
        customer_name=checkout.customer_name,
        shipping_address=checkout.shipping_address,
        shipping_method=checkout.shipping_method,
        payment_handler=checkout.payment_handler,
        payment_status="paid",
    )
    
    # Update inventory
    for item in checkout.line_items:
        product = await get_product_by_id(item["id"], db)
        product.inventory -= item["quantity"]
    
    # Update checkout status
    checkout.status = CheckoutStatus.COMPLETE
    checkout.updated_at = datetime.utcnow()
    
    db.add(order)
    await db.commit()
    await db.refresh(checkout)
    
    response = checkout.to_response()
    response["order"] = order.to_response()
    return response


@router.post("/checkout-sessions/{checkout_id}/cancel")
async def cancel_checkout(
    checkout_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Cancel a checkout session."""
    checkout = await get_checkout_by_id(checkout_id, db)
    
    if checkout.status != CheckoutStatus.OPEN:
        raise HTTPException(
            status_code=400,
            detail="Checkout session is not open"
        )
    
    checkout.status = CheckoutStatus.CANCELLED
    checkout.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(checkout)
    
    return checkout.to_response()


@router.get("/orders/{order_id}")
async def get_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get an order by ID."""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order.to_response()
