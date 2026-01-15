"""Gemini tool definitions for UCP shopping agent."""

from google import genai
from google.genai import types


# Tool function declarations for Gemini
LIST_PRODUCTS = types.FunctionDeclaration(
    name="list_products",
    description="List all available products in the flower shop. Use this when the user wants to browse or see what's available.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={},
    ),
)

GET_PRODUCT_DETAILS = types.FunctionDeclaration(
    name="get_product_details",
    description="Get detailed information about a specific product by its ID.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "product_id": types.Schema(
                type=types.Type.STRING,
                description="The product ID (e.g., 'prod_001')",
            ),
        },
        required=["product_id"],
    ),
)

CREATE_CHECKOUT = types.FunctionDeclaration(
    name="create_checkout",
    description="Create a checkout session to purchase a product. Use this when the user wants to buy something.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "product_id": types.Schema(
                type=types.Type.STRING,
                description="The product ID to purchase",
            ),
            "quantity": types.Schema(
                type=types.Type.INTEGER,
                description="Quantity to purchase (default: 1)",
            ),
        },
        required=["product_id"],
    ),
)

UPDATE_CHECKOUT = types.FunctionDeclaration(
    name="update_checkout",
    description="Update a checkout session with customer and shipping information.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "checkout_id": types.Schema(
                type=types.Type.STRING,
                description="The checkout session ID",
            ),
            "customer_email": types.Schema(
                type=types.Type.STRING,
                description="Customer's email address",
            ),
            "customer_name": types.Schema(
                type=types.Type.STRING,
                description="Customer's name",
            ),
            "shipping_address": types.Schema(
                type=types.Type.OBJECT,
                description="Shipping address with line1, city, state, postal_code, country",
                properties={
                    "line1": types.Schema(type=types.Type.STRING),
                    "city": types.Schema(type=types.Type.STRING),
                    "state": types.Schema(type=types.Type.STRING),
                    "postal_code": types.Schema(type=types.Type.STRING),
                    "country": types.Schema(type=types.Type.STRING),
                },
            ),
            "shipping_method": types.Schema(
                type=types.Type.STRING,
                description="Shipping method (e.g., 'standard', 'express')",
            ),
        },
        required=["checkout_id"],
    ),
)

COMPLETE_CHECKOUT = types.FunctionDeclaration(
    name="complete_checkout",
    description="Complete a checkout session and place the order. Use this after all customer and shipping info is collected.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "checkout_id": types.Schema(
                type=types.Type.STRING,
                description="The checkout session ID to complete",
            ),
        },
        required=["checkout_id"],
    ),
)

GET_ORDER = types.FunctionDeclaration(
    name="get_order",
    description="Get details of an order by its ID.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "order_id": types.Schema(
                type=types.Type.STRING,
                description="The order ID",
            ),
        },
        required=["order_id"],
    ),
)

# All tools combined
UCP_TOOLS = types.Tool(
    function_declarations=[
        LIST_PRODUCTS,
        GET_PRODUCT_DETAILS,
        CREATE_CHECKOUT,
        UPDATE_CHECKOUT,
        COMPLETE_CHECKOUT,
        GET_ORDER,
    ]
)
