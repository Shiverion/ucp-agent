"""Products API router."""

from fastapi import APIRouter
from typing import List

router = APIRouter()

PRODUCTS = [
    {"id": "prod_001", "name": "Red Roses Bouquet", "price": 49.99, "description": "Beautiful bouquet of 12 fresh red roses", "category": "flowers", "image": "https://images.unsplash.com/photo-1518882605630-8eb-cd7d?w=400"},
    {"id": "prod_002", "name": "White Lilies", "price": 39.99, "description": "Elegant white lilies arrangement", "category": "flowers", "image": "https://images.unsplash.com/photo-1533616688419-b7a585564566?w=400"},
    {"id": "prod_003", "name": "Mixed Tulips", "price": 34.99, "description": "Colorful mix of spring tulips", "category": "flowers", "image": "https://images.unsplash.com/photo-1520763185298-1b434c919102?w=400"},
    {"id": "prod_004", "name": "Sunflower Bunch", "price": 29.99, "description": "Bright and cheerful sunflowers", "category": "flowers", "image": "https://images.unsplash.com/photo-1597848212624-a19eb35e2651?w=400"},
    {"id": "prod_005", "name": "Pink Peonies", "price": 54.99, "description": "Romantic pink peony bouquet", "category": "flowers", "image": "https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=400"},
    {"id": "prod_006", "name": "Yellow Daffodils", "price": 24.99, "description": "Fresh spring daffodils", "category": "flowers", "image": "https://images.unsplash.com/photo-1455659817273-f96807779a8a?w=400"},
    {"id": "prod_007", "name": "Purple Lavender", "price": 19.99, "description": "Fragrant lavender stems", "category": "flowers", "image": "https://images.unsplash.com/photo-1468327768560-75b778cbb551?w=400"},
    {"id": "prod_008", "name": "Orange Gerberas", "price": 32.99, "description": "Vibrant gerbera daisies", "category": "flowers", "image": "https://images.unsplash.com/photo-1536306099827-f0e642eac99e?w=400"},
    {"id": "prod_010", "name": "Orchid Plant", "price": 59.99, "description": "Potted phalaenopsis orchid", "category": "plants", "image": "https://images.unsplash.com/photo-1567331711402-509c12c41959?w=400"},
    {"id": "prod_011", "name": "Peace Lily", "price": 44.99, "description": "Air-purifying peace lily", "category": "plants", "image": "https://images.unsplash.com/photo-1593691509543-c55fb32e9e3f?w=400"},
    {"id": "prod_012", "name": "Succulent Garden", "price": 29.99, "description": "Mini succulent arrangement", "category": "plants", "image": "https://images.unsplash.com/photo-1509423350716-97f9360b4e09?w=400"},
    {"id": "prod_013", "name": "Fiddle Leaf Fig", "price": 89.99, "description": "Trendy indoor tree", "category": "plants", "image": "https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?w=400"},
    {"id": "prod_014", "name": "Snake Plant", "price": 34.99, "description": "Low-maintenance sansevieria", "category": "plants", "image": "https://images.unsplash.com/photo-1593691512424-df9db8a5b3df?w=400"},
    {"id": "prod_020", "name": "Wedding Bouquet", "price": 149.99, "description": "Elegant bridal arrangement", "category": "arrangements", "image": "https://images.unsplash.com/photo-1519378058457-4c29a0a2efac?w=400"},
    {"id": "prod_021", "name": "Sympathy Wreath", "price": 99.99, "description": "Respectful funeral wreath", "category": "arrangements", "image": "https://images.unsplash.com/photo-1561181286-d3fee7d55364?w=400"},
    {"id": "prod_022", "name": "Birthday Celebration", "price": 64.99, "description": "Festive mixed bouquet", "category": "arrangements", "image": "https://images.unsplash.com/photo-1487530811176-3780de880c2d?w=400"},
    {"id": "prod_023", "name": "Get Well Soon", "price": 44.99, "description": "Cheerful recovery flowers", "category": "arrangements", "image": "https://images.unsplash.com/photo-1518882605630-8eb-cd7d?w=400"},
]


@router.get("/products")
async def get_products() -> List[dict]:
    """Get all products."""
    return PRODUCTS


@router.get("/products/search")
async def search_products(q: str = "", max_price: float = None, category: str = None) -> dict:
    """Search products."""
    results = PRODUCTS
    if q:
        results = [p for p in results if q.lower() in p["name"].lower() or q.lower() in p["description"].lower()]
    if max_price:
        results = [p for p in results if p["price"] <= max_price]
    if category:
        results = [p for p in results if p["category"] == category]
    return {"shop": "UCP Flower Shop", "products": results}

@router.get("/products/{product_id}")
async def get_product(product_id: str) -> dict:
    """Get a single product by ID."""
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product
    return {"error": "Product not found"}
