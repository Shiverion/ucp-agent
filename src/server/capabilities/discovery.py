"""UCP Discovery capability - manifest endpoint."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

# UCP Discovery Profile
UCP_MANIFEST = {
    "ucp": {
        "version": "2026-01-11",
        "services": {
            "dev.ucp.shopping": {
                "version": "2026-01-11",
                "spec": "https://ucp.dev/specification/reference",
                "rest": {
                    "schema": "https://ucp.dev/services/shopping/openapi.json",
                    "endpoint": "http://localhost:8183"
                }
            }
        },
        "capabilities": [
            {
                "name": "dev.ucp.shopping.checkout",
                "version": "2026-01-11",
                "spec": "https://ucp.dev/specification/checkout",
                "schema": "https://ucp.dev/schemas/shopping/checkout.json"
            },
            {
                "name": "dev.ucp.shopping.order",
                "version": "2026-01-11",
                "spec": "https://ucp.dev/specification/order",
                "schema": "https://ucp.dev/schemas/shopping/order.json"
            }
        ]
    },
    "payment": {
        "handlers": [
            {
                "id": "mock_payment_handler",
                "name": "dev.ucp.mock_payment",
                "version": "2026-01-11",
                "spec": "https://ucp.dev/specs/mock",
                "config_schema": "https://ucp.dev/schemas/mock.json",
                "instrument_schemas": [
                    "https://ucp.dev/schemas/shopping/types/card_payment_instrument.json"
                ],
                "config": {
                    "supported_tokens": ["success_token", "fail_token"]
                }
            }
        ]
    },
    "merchant": {
        "name": "UCP Custom Shop",
        "description": "Custom UCP-compliant merchant implementation",
        "support_email": "support@example.com",
        "language": "en"
    }
}


@router.get("/.well-known/ucp")
async def get_discovery() -> JSONResponse:
    """Return UCP discovery manifest."""
    return JSONResponse(content=UCP_MANIFEST)
