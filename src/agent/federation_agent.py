"""Federation Agent - queries multiple UCP shops to find the best products."""

import httpx
import json
import os
import asyncio
from typing import Optional, List
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_ID = "models/gemini-2.5-flash"

# All UCP shops in the federation
SHOPS = [
    {"id": "ucp_flower_shop", "name": "UCP Flower Shop", "url": "http://localhost:8183"},
    {"id": "garden_paradise", "name": "Garden Paradise", "url": "http://localhost:8184"},
    {"id": "luxury_blooms", "name": "Luxury Blooms", "url": "http://localhost:8185"},
    {"id": "green_thumb", "name": "Green Thumb Plants", "url": "http://localhost:8186"},
]

SYSTEM_PROMPT = """You are a smart shopping assistant that can search across multiple flower shops to find the best deals.

Available shops:
1. UCP Flower Shop - Main shop with varied selection
2. Garden Paradise - Budget-friendly flowers
3. Luxury Blooms - Premium flowers for special occasions
4. Green Thumb Plants - Indoor plants and succulents

You can:
- Search products across ALL shops at once
- Filter by price (e.g., "under $15")
- Filter by category (flowers, plants, arrangements)
- Compare prices across shops
- Help users find the best deals

When you find matching products, you MUST display them to the user.
For each product you recommend, you MUST include a special JSON block at the end of your response so the UI can render a clickable card.
Format:
```json
[
  {
    "id": "product_id",
    "name": "Product Name",
    "price": 12.99,
    "description": "Description...",
    "image": "image_url",
    "shop_name": "Shop Name"
  }
]
```


CHECKOUT FLOW:
When a user wants to buy a product:
1. You MUST ask for their full name and shipping address.
2. DO NOT proceed to checkout until you have both.
3. Once you have the details, output the JSON block with the product info AND the collected "shipping_details".

Example JSON for checkout (include this ONLY after collecting details):
```json
[
  {
    "id": "product_id",
    "name": "Product Name",
    "price": 12.99,
    "image": "image_url",
    "shop_name": "Shop Name",
    "action": "checkout",
    "shipping_details": {
       "name": "User Name",
       "address": "123 Street, City"
    }
  }
]
```


When a user asks for something like "roses under $15", search all shops, summarize the results in text, AND include the JSON block for the top results (without shipping_details).


ORDER TRACKING:
If a user asks to track an order (e.g., "Where is my order?", "Track ID 123"), YOU MUST output a JSON block to trigger the client-side tracking tool.
EXTRACT the Order ID from the user's request. If no ID is provided, ask for it.

Example Tracking Output:
```json
[
  {
    "action": "track_order",
    "order_id": "ORD-8291"
  }
]
```
"""


# Tool declarations
SEARCH_ALL_SHOPS = types.FunctionDeclaration(
    name="search_all_shops",
    description="Search for products across all UCP shops. Use this to find products matching criteria like name, price, or category.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "query": types.Schema(type=types.Type.STRING, description="Product name or keyword to search"),
            "max_price": types.Schema(type=types.Type.NUMBER, description="Maximum price filter"),
            "category": types.Schema(type=types.Type.STRING, description="Category: flowers, plants, or arrangements"),
        },
    ),
)

FEDERATION_TOOLS = types.Tool(function_declarations=[SEARCH_ALL_SHOPS])


class FederationAgent:
    """Agent that queries multiple UCP shops."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required")
        
        self.client = genai.Client(api_key=self.api_key)
        self.http_client = httpx.Client(timeout=10.0)
        self.chat_history: list[types.Content] = []

    async def _search_shop(self, shop: dict, query: str = "", max_price: float = None, category: str = None) -> List[dict]:
        """Search a single shop for products."""
        try:
            params = {}
            if query:
                params["q"] = query
            if max_price:
                params["max_price"] = max_price
            if category:
                params["category"] = category
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try search endpoint first
                try:
                    response = await client.get(f"{shop['url']}/products/search", params=params)
                    if response.status_code == 200:
                        data = response.json()
                        products = data.get("products", data)
                        for p in products:
                            p["shop_name"] = shop["name"]
                            p["shop_url"] = shop["url"]
                        return products
                except:
                    pass
                
                # Fall back to getting all products
                response = await client.get(f"{shop['url']}/products")
                if response.status_code != 200:
                    return []
                
                products = response.json()
            
            # Filter locally
            if query:
                products = [p for p in products if query.lower() in p.get("name", "").lower() or query.lower() in p.get("description", "").lower()]
            if max_price:
                products = [p for p in products if float(p.get("price", 999)) <= max_price]
            if category:
                products = [p for p in products if p.get("category") == category]
            
            for p in products:
                p["shop_name"] = shop["name"]
                p["shop_url"] = shop["url"]
                # Ensure image exists
                if not p.get("image"):
                    p["image"] = "https://images.unsplash.com/photo-1596627685652-320c82276cb0?w=400" # Fallback flower image
            
            return products
        except Exception as e:
            print(f"Error searching {shop['name']}: {e}")
            return []

    async def search_all_shops(self, query: str = "", max_price: float = None, category: str = None) -> List[dict]:
        """Search all shops and combine results."""
        import asyncio
        tasks = [self._search_shop(shop, query, max_price, category) for shop in SHOPS]
        results_list = await asyncio.gather(*tasks)
        
        all_results = []
        for r in results_list:
            all_results.extend(r)
        
        # Sort by price
        all_results.sort(key=lambda x: float(x.get("price", 999)))
        return all_results

    async def _execute_tool(self, function_call: types.FunctionCall) -> str:
        """Execute a tool function."""
        name = function_call.name
        args = dict(function_call.args) if function_call.args else {}
        
        if name == "search_all_shops":
            results = await self.search_all_shops(
                query=args.get("query", ""),
                max_price=args.get("max_price"),
                category=args.get("category"),
            )
            
            if not results:
                return json.dumps({"message": "No products found matching your criteria", "results": []})
            
            return json.dumps({
                "total_results": len(results),
                "results": results[:10]  # Limit to top 10
            }, indent=2)
        
        return json.dumps({"error": f"Unknown function: {name}"})

    async def chat(self, user_message: str) -> str:
        """Send a message and get a response."""
        self.chat_history.append(
            types.Content(role="user", parts=[types.Part(text=user_message)])
        )

        # Run blocking generate_content in thread pool
        response = await asyncio.to_thread(
            self.client.models.generate_content,
            model=MODEL_ID,
            contents=self.chat_history,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=[FEDERATION_TOOLS],
            ),
        )

        # Handle function calls
        while response.candidates[0].content.parts:
            part = response.candidates[0].content.parts[0]
            
            if part.function_call:
                function_call = part.function_call
                # Execute tool asynchronously
                result = await self._execute_tool(function_call)
                
                self.chat_history.append(response.candidates[0].content)
                self.chat_history.append(
                    types.Content(
                        role="user",
                        parts=[types.Part(function_response=types.FunctionResponse(
                            name=function_call.name,
                            response={"result": result},
                        ))],
                    )
                )
                
                # Generate next response
                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model=MODEL_ID,
                    contents=self.chat_history,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        tools=[FEDERATION_TOOLS],
                    ),
                )
            else:
                break
        
        assistant_text = response.text if response.text else "Sorry, I couldn't process that."
        self.chat_history.append(
            types.Content(role="model", parts=[types.Part(text=assistant_text)])
        )
        
        return assistant_text

    def reset(self):
        self.chat_history = []

    def close(self):
        self.http_client.close()


def main():
    """Run the federation agent."""
    print("=" * 60)
    print("🌐 UCP Federation Agent - Search Across All Shops")
    print("=" * 60)
    print("\nConnected shops:")
    for shop in SHOPS:
        print(f"  • {shop['name']} ({shop['url']})")
    print("\nTry: 'Find roses under $15' or 'Show me cheap flowers'")
    print("Type 'quit' to exit\n")
    print("=" * 60)

    try:
        agent = FederationAgent()
    except ValueError as e:
        print(f"Error: {e}")
        return

    try:
        while True:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            if user_input.lower() == "quit":
                print("\nGoodbye! 🌸")
                break
            if user_input.lower() == "reset":
                agent.reset()
                print("\n[Conversation reset]")
                continue
            
            try:
                # Chat is now async
                response = asyncio.run(agent.chat(user_input))
                print(f"\n🤖 Agent: {response}")
            except Exception as e:
                print(f"\n❌ Error: {e}")
    finally:
        agent.close()


if __name__ == "__main__":
    main()
