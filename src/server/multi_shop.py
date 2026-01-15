"""Multi-shop UCP server - runs multiple shops on different ports."""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import asyncio

# Shop configurations
SHOPS = {
    "garden_paradise": {
        "name": "Garden Paradise",
        "port": 8184,
        "description": "Budget-friendly flowers for everyone",
        "products": [
            {"id": "gp_001", "name": "Red Roses Bouquet", "price": 12.99, "description": "Affordable dozen roses", "category": "flowers", "image": "https://images.unsplash.com/photo-1518882605630-8eb-cd7d?w=400"},
            {"id": "gp_002", "name": "White Daisies", "price": 8.99, "description": "Fresh white daisies", "category": "flowers", "image": "https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=400"},
            {"id": "gp_003", "name": "Mixed Tulips", "price": 11.99, "description": "Colorful tulip bunch", "category": "flowers", "image": "https://images.unsplash.com/photo-1520763185298-1b434c919102?w=400"},
            {"id": "gp_004", "name": "Sunflowers", "price": 9.99, "description": "Bright sunflower bunch", "category": "flowers", "image": "https://images.unsplash.com/photo-1597848212624-a19eb35e2651?w=400"},
            {"id": "gp_005", "name": "Carnations", "price": 7.99, "description": "Classic carnations", "category": "flowers", "image": "https://images.unsplash.com/photo-1455659817273-f96807779a8a?w=400"},
        ]
    },
    "luxury_blooms": {
        "name": "Luxury Blooms",
        "port": 8185,
        "description": "Premium flowers for special occasions",
        "products": [
            {"id": "lb_001", "name": "Premium Red Roses", "price": 89.99, "description": "24 long-stem Ecuador roses", "category": "flowers", "image": "https://images.unsplash.com/photo-1518882605630-8eb-cd7d?w=400"},
            {"id": "lb_002", "name": "Exotic Orchids", "price": 129.99, "description": "Rare imported orchids", "category": "flowers", "image": "https://images.unsplash.com/photo-1567331711402-509c12c41959?w=400"},
            {"id": "lb_003", "name": "Peony Paradise", "price": 79.99, "description": "Luxury peony arrangement", "category": "flowers", "image": "https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=400"},
            {"id": "lb_004", "name": "Wedding Masterpiece", "price": 299.99, "description": "Bridal bouquet with crystals", "category": "arrangements", "image": "https://images.unsplash.com/photo-1519378058457-4c29a0a2efac?w=400"},
            {"id": "lb_005", "name": "Anniversary Special", "price": 149.99, "description": "50 roses in a box", "category": "arrangements", "image": "https://images.unsplash.com/photo-1487530811176-3780de880c2d?w=400"},
        ]
    },
    "green_thumb": {
        "name": "Green Thumb Plants",
        "port": 8186,
        "description": "Indoor plants and succulents",
        "products": [
            {"id": "gt_001", "name": "Mini Succulent Set", "price": 14.99, "description": "Set of 3 mini succulents", "category": "plants", "image": "https://images.unsplash.com/photo-1509423350716-97f9360b4e09?w=400"},
            {"id": "gt_002", "name": "Snake Plant", "price": 24.99, "description": "Air-purifying sansevieria", "category": "plants", "image": "https://images.unsplash.com/photo-1593691512424-df9db8a5b3df?w=400"},
            {"id": "gt_003", "name": "Monstera Deliciosa", "price": 49.99, "description": "Trendy Swiss cheese plant", "category": "plants", "image": "https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?w=400"},
            {"id": "gt_004", "name": "Peace Lily", "price": 19.99, "description": "Elegant flowering plant", "category": "plants", "image": "https://images.unsplash.com/photo-1593691509543-c55fb32e9e3f?w=400"},
            {"id": "gt_005", "name": "Fiddle Leaf Fig", "price": 69.99, "description": "Statement indoor tree", "category": "plants", "image": "https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?w=400"},
        ]
    }
}


def create_shop_app(shop_id: str, config: dict) -> FastAPI:
    """Create a FastAPI app for a shop."""
    app = FastAPI(
        title=config["name"],
        description=config["description"],
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/.well-known/ucp")
    async def discovery():
        return {
            "ucp": {
                "version": "2026-01-11",
                "capabilities": ["dev.ucp.shopping.checkout", "dev.ucp.shopping.order"]
            },
            "merchant": {
                "id": shop_id,
                "name": config["name"],
                "description": config["description"]
            }
        }
    
    @app.get("/products")
    async def get_products():
        return config["products"]
    
    @app.get("/products/search")
    async def search_products(q: str = "", max_price: float = None, category: str = None):
        results = config["products"]
        if q:
            results = [p for p in results if q.lower() in p["name"].lower() or q.lower() in p["description"].lower()]
        if max_price:
            results = [p for p in results if p["price"] <= max_price]
        if category:
            results = [p for p in results if p["category"] == category]
        return {"shop": config["name"], "products": results}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "shop": config["name"]}
    
    return app


# Create apps for each shop
garden_paradise_app = create_shop_app("garden_paradise", SHOPS["garden_paradise"])
luxury_blooms_app = create_shop_app("luxury_blooms", SHOPS["luxury_blooms"])
green_thumb_app = create_shop_app("green_thumb", SHOPS["green_thumb"])


async def run_shop(app: FastAPI, port: int, name: str):
    """Run a shop on a specific port."""
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    print(f"🏪 Starting {name} on port {port}")
    await server.serve()


async def main():
    """Run all shops concurrently."""
    print("=" * 50)
    print("🌸 UCP Multi-Shop Federation")
    print("=" * 50)
    
    tasks = [
        run_shop(garden_paradise_app, 8184, "Garden Paradise"),
        run_shop(luxury_blooms_app, 8185, "Luxury Blooms"),
        run_shop(green_thumb_app, 8186, "Green Thumb Plants"),
    ]
    
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
