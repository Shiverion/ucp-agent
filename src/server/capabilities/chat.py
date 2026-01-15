"""Chat API router for Gemini agent integration."""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

# Use the Federation Agent to search across all shops
from src.agent.federation_agent import FederationAgent

router = APIRouter()

# Global agent instance
_agent: Optional[FederationAgent] = None


def get_agent() -> FederationAgent:
    """Get or create the agent instance."""
    global _agent
    if _agent is None:
        try:
            _agent = FederationAgent()
        except ValueError as e:
            print(f"Error initializing agent: {e}")
            raise
    return _agent


class ChatRequest(BaseModel):
    """Chat request body."""
    message: str


class ChatResponse(BaseModel):
    """Chat response body."""
    response: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Send a message to the shopping agent."""
    try:
        print(f"DEBUG: Received chat request: {request.message}", flush=True)
        
        if request.message.lower() == "ping":
             return ChatResponse(response="pong 🏓")

        agent = get_agent()
        print("DEBUG: Agent retrieved", flush=True)
        
        # Add 30s timeout
        import asyncio
        response = await asyncio.wait_for(agent.chat(request.message), timeout=30.0)
        
        print(f"DEBUG: Agent response length: {len(response)}", flush=True)
        return ChatResponse(response=response)
    except asyncio.TimeoutError:
        print("ERROR: Chat timed out", flush=True)
        return ChatResponse(response="I'm sorry, the search is taking too long. Please try again.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Chat error: {e}", flush=True)
        return ChatResponse(response=f"I'm sorry, I'm having trouble connecting to the shops right now. Please try again.")


@router.post("/chat/reset")
async def reset_chat():
    """Reset the conversation."""
    global _agent
    if _agent:
        _agent.reset()
    return {"status": "ok", "message": "Conversation reset"}
