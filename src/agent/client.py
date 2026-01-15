"""UCP Client for making API calls to the server."""

import httpx
import os
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

UCP_SERVER_URL = os.getenv("UCP_SERVER_URL", "http://localhost:8183")


class UCPClient:
    """Client for interacting with UCP-compliant servers."""

    def __init__(self, base_url: str = UCP_SERVER_URL):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=30.0)
        self._capabilities = None

    def discover(self) -> dict:
        """Discover server capabilities."""
        response = self.client.get(f"{self.base_url}/.well-known/ucp")
        response.raise_for_status()
        self._capabilities = response.json()
        return self._capabilities

    def get_products(self) -> List[dict]:
        """Get available products from the server."""
        return [
            {"id": "prod_001", "name": "Red Roses Bouquet", "price": "49.99", "description": "Beautiful bouquet of 12 fresh red roses", "category": "flowers"},
            {"id": "prod_002", "name": "White Lilies", "price": "39.99", "description": "Elegant white lilies arrangement", "category": "flowers"},
            {"id": "prod_003", "name": "Mixed Tulips", "price": "34.99", "description": "Colorful mix of spring tulips", "category": "flowers"},
            {"id": "prod_004", "name": "Sunflower Bunch", "price": "29.99", "description": "Bright and cheerful sunflowers", "category": "flowers"},
            {"id": "prod_005", "name": "Pink Peonies", "price": "54.99", "description": "Romantic pink peony bouquet", "category": "flowers"},
            {"id": "prod_006", "name": "Yellow Daffodils", "price": "24.99", "description": "Fresh spring daffodils", "category": "flowers"},
            {"id": "prod_007", "name": "Purple Lavender", "price": "19.99", "description": "Fragrant lavender stems", "category": "flowers"},
            {"id": "prod_008", "name": "Orange Gerberas", "price": "32.99", "description": "Vibrant gerbera daisies", "category": "flowers"},
            {"id": "prod_010", "name": "Orchid Plant", "price": "59.99", "description": "Potted phalaenopsis orchid", "category": "plants"},
            {"id": "prod_011", "name": "Peace Lily", "price": "44.99", "description": "Air-purifying peace lily", "category": "plants"},
            {"id": "prod_012", "name": "Succulent Garden", "price": "29.99", "description": "Mini succulent arrangement", "category": "plants"},
            {"id": "prod_013", "name": "Fiddle Leaf Fig", "price": "89.99", "description": "Trendy indoor tree", "category": "plants"},
            {"id": "prod_014", "name": "Snake Plant", "price": "34.99", "description": "Low-maintenance sansevieria", "category": "plants"},
            {"id": "prod_020", "name": "Wedding Bouquet", "price": "149.99", "description": "Elegant bridal arrangement", "category": "arrangements"},
            {"id": "prod_021", "name": "Sympathy Wreath", "price": "99.99", "description": "Respectful funeral wreath", "category": "arrangements"},
            {"id": "prod_022", "name": "Birthday Celebration", "price": "64.99", "description": "Festive mixed bouquet", "category": "arrangements"},
            {"id": "prod_023", "name": "Get Well Soon", "price": "44.99", "description": "Cheerful recovery flowers", "category": "arrangements"},
        ]

    def create_checkout(
        self,
        product_id: str,
        quantity: int = 1,
        customer_email: Optional[str] = None,
    ) -> dict:
        """Create a checkout session."""
        payload = {
            "line_items": [{"product_id": product_id, "quantity": quantity}],
        }
        if customer_email:
            payload["customer"] = {"email": customer_email}

        response = self.client.post(
            f"{self.base_url}/checkout-sessions",
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    def get_checkout(self, checkout_id: str) -> dict:
        """Get a checkout session by ID."""
        response = self.client.get(f"{self.base_url}/checkout-sessions/{checkout_id}")
        response.raise_for_status()
        return response.json()

    def update_checkout(
        self,
        checkout_id: str,
        customer_email: Optional[str] = None,
        customer_name: Optional[str] = None,
        shipping_address: Optional[dict] = None,
        shipping_method: Optional[str] = None,
    ) -> dict:
        """Update a checkout session."""
        payload = {}
        if customer_email or customer_name:
            payload["customer"] = {}
            if customer_email:
                payload["customer"]["email"] = customer_email
            if customer_name:
                payload["customer"]["name"] = customer_name
        if shipping_address:
            payload["shipping_address"] = shipping_address
        if shipping_method:
            payload["shipping_method"] = shipping_method

        response = self.client.put(
            f"{self.base_url}/checkout-sessions/{checkout_id}",
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    def complete_checkout(
        self,
        checkout_id: str,
        payment_handler: str = "mock_payment_handler",
    ) -> dict:
        """Complete a checkout and create an order."""
        payload = {
            "payment": {"handler": payment_handler},
        }
        response = self.client.post(
            f"{self.base_url}/checkout-sessions/{checkout_id}/complete",
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    def cancel_checkout(self, checkout_id: str) -> dict:
        """Cancel a checkout session."""
        response = self.client.post(
            f"{self.base_url}/checkout-sessions/{checkout_id}/cancel"
        )
        response.raise_for_status()
        return response.json()

    def get_order(self, order_id: str) -> dict:
        """Get an order by ID."""
        response = self.client.get(f"{self.base_url}/orders/{order_id}")
        response.raise_for_status()
        return response.json()

    def close(self):
        """Close the HTTP client."""
        self.client.close()
