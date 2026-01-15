"""Capabilities package for UCP server."""

from .discovery import router as discovery_router
from .checkout import router as checkout_router

__all__ = ["discovery_router", "checkout_router"]
