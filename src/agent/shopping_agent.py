"""UCP Shopping Agent powered by Gemini Flash 2.5."""

import json
import os
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types

from .client import UCPClient
from .tools import UCP_TOOLS

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_ID = "models/gemini-2.5-flash"

SYSTEM_PROMPT = """You are a helpful shopping assistant for a flower shop powered by the Universal Commerce Protocol (UCP).

Your capabilities:
1. List available products in the shop
2. Help customers choose products
3. Create checkout sessions for purchases
4. Collect customer and shipping information
5. Complete orders

Be friendly, helpful, and guide customers through their shopping journey. When a customer wants to buy something:
1. First show them the available products
2. Help them choose the right product
3. Create a checkout session
4. Collect their email, name, and shipping address
5. Complete the order

Always confirm details before completing an order. Format prices nicely (e.g., "$49.99")."""


class ShoppingAgent:
    """AI Shopping Agent using Gemini Flash 2.5."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required. Set it in .env file.")
        
        self.client = genai.Client(api_key=self.api_key)
        self.ucp_client = UCPClient()
        self.chat_history: list[types.Content] = []
        self.current_checkout_id: Optional[str] = None
        
    def _execute_tool(self, function_call: types.FunctionCall) -> str:
        """Execute a tool function and return the result."""
        name = function_call.name
        args = dict(function_call.args) if function_call.args else {}
        
        try:
            if name == "list_products":
                products = self.ucp_client.get_products()
                return json.dumps({"products": products}, indent=2)
            
            elif name == "get_product_details":
                products = self.ucp_client.get_products()
                product = next(
                    (p for p in products if p["id"] == args["product_id"]), 
                    None
                )
                if product:
                    return json.dumps(product, indent=2)
                return json.dumps({"error": "Product not found"})
            
            elif name == "create_checkout":
                result = self.ucp_client.create_checkout(
                    product_id=args["product_id"],
                    quantity=args.get("quantity", 1),
                )
                self.current_checkout_id = result["id"]
                return json.dumps(result, indent=2)
            
            elif name == "update_checkout":
                result = self.ucp_client.update_checkout(
                    checkout_id=args["checkout_id"],
                    customer_email=args.get("customer_email"),
                    customer_name=args.get("customer_name"),
                    shipping_address=args.get("shipping_address"),
                    shipping_method=args.get("shipping_method"),
                )
                return json.dumps(result, indent=2)
            
            elif name == "complete_checkout":
                result = self.ucp_client.complete_checkout(
                    checkout_id=args["checkout_id"],
                )
                return json.dumps(result, indent=2)
            
            elif name == "get_order":
                result = self.ucp_client.get_order(order_id=args["order_id"])
                return json.dumps(result, indent=2)
            
            else:
                return json.dumps({"error": f"Unknown function: {name}"})
                
        except Exception as e:
            return json.dumps({"error": str(e)})

    def chat(self, user_message: str) -> str:
        """Send a message and get a response from the agent."""
        # Add user message to history
        self.chat_history.append(
            types.Content(
                role="user",
                parts=[types.Part(text=user_message)],
            )
        )

        # Generate response
        response = self.client.models.generate_content(
            model=MODEL_ID,
            contents=self.chat_history,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=[UCP_TOOLS],
            ),
        )

        # Handle function calls
        while response.candidates[0].content.parts:
            part = response.candidates[0].content.parts[0]
            
            if part.function_call:
                # Execute the function
                function_call = part.function_call
                result = self._execute_tool(function_call)
                
                # Add assistant's function call to history
                self.chat_history.append(response.candidates[0].content)
                
                # Add function result to history
                self.chat_history.append(
                    types.Content(
                        role="user",
                        parts=[
                            types.Part(
                                function_response=types.FunctionResponse(
                                    name=function_call.name,
                                    response={"result": result},
                                )
                            )
                        ],
                    )
                )
                
                # Get next response
                response = self.client.models.generate_content(
                    model=MODEL_ID,
                    contents=self.chat_history,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        tools=[UCP_TOOLS],
                    ),
                )
            else:
                break
        
        # Extract text response
        assistant_text = response.text if response.text else "I'm sorry, I couldn't process that request."
        
        # Add assistant response to history
        self.chat_history.append(
            types.Content(
                role="model",
                parts=[types.Part(text=assistant_text)],
            )
        )
        
        return assistant_text

    def reset(self):
        """Reset the conversation history."""
        self.chat_history = []
        self.current_checkout_id = None

    def close(self):
        """Clean up resources."""
        self.ucp_client.close()


def main():
    """Run the shopping agent in interactive mode."""
    print("🌸 Welcome to the UCP Flower Shop!")
    print("=" * 50)
    print("I'm your AI shopping assistant. I can help you:")
    print("  • Browse our flower selection")
    print("  • Place orders")
    print("  • Track your purchases")
    print("\nType 'quit' to exit, 'reset' to start over.")
    print("=" * 50)
    print()

    try:
        agent = ShoppingAgent()
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set GEMINI_API_KEY in your .env file.")
        return

    try:
        while True:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "quit":
                print("\nThank you for shopping with us! 🌸")
                break
            
            if user_input.lower() == "reset":
                agent.reset()
                print("\n[Conversation reset]\n")
                continue
            
            try:
                response = agent.chat(user_input)
                print(f"\n🤖 Assistant: {response}\n")
            except Exception as e:
                print(f"\n❌ Error: {e}\n")

    finally:
        agent.close()


if __name__ == "__main__":
    main()
