#  Universal Commerce Protocol (UCP) Agent



This project allows AI Agents to shop autonomously. It implements the **Universal Commerce Protocol (UCP)**, standardized by Google/Shopify, enabling seamless discovery, search, checkout, and order tracking between AI and Commerce Backends.

##  Key Features & Improvements

We have significantly expanded upon the initial plan, delivering a production-ready demo with advanced capabilities:

### 1. Federated Multi-Shop Architecture
*   **Decentralized Search**: Instead of a single store, we run **3 independent shops** (Main, Budget, Luxury) on different ports.
*   **Federation Agent**: A smart orchestrator that queries all shops in parallel to find the best deals for the user.
*   **Real-time Inventory**: Live checks against each shop's database.

### 2. Intelligent Shopping Agent
*   **Powered by Gemini 2.0 Flash**: Fast, low-latency conversational AI.
*   **Conversational Checkout**: The agent collects shipping details (Name, Address) naturally during the chat.
*   **Smart Tool Use**: The agent autonomously decides when to search, checks order status, or trigger a purchase.

### 3. Modern React Frontend (`/frontend`)
*   **Multi-Page Experience**: Split into a visual `Catalog` for browsing and a dedicated `Chat` interface.
*   **Interactive Chat Cards**: Product results are rendered as beautiful, actionable cards (not just text).
*   **One-click Tracking**: Ask "Where is my order?", and the agent returns a live status card. clicking it opens a detailed tracking timeline.
*   **Checkout Modal**: Smooth, integrated payment flow.

---

##  Technology Stack

*   **Backend**: Python 3.10+, FastAPI, UCP Standards.
*   **Frontend**: React, Vite, CSS Modules.
*   **AI**: Google GenAI SDK (Gemini).
*   **Transport**: HTTP REST (UCP Discovery/Search/Checkout).

---

##  Quick Start

### Prerequisites
*   Python 3.10+
*   Node.js 18+
*   `uv` package manager (`pip install uv`)

### 1. Installation
```bash
# Install Python dependencies
uv sync

# Install Frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Running the Full Stack
We have a helper script to launch the Federation (3 shops + simple agent) or you can run components individually.

**Option A: Run everything manually (Recommended for Dev)**
```powershell
# Terminal 1: Multi-Shop Server (Ports 8183, 8184, 8185)
uv run python -m src.server.multi_shop

# Terminal 2: React Frontend
cd frontend
npm run dev
```
*   **Frontend**: `http://localhost:5173`
*   **Main Shop**: `http://localhost:8183`

### 3. Usage Guide

1.  **Browse**: Visit the frontend to see the aggregated catalog.
2.  **Chat**: Click the **Chat Bubble** 💬 to open the AI Assistant.
3.  **Shop**: Ask "Find me red roses under $40".
4.  **Buy**: The Agent will find the best option. Click "Buy Now" or say "I'll take the cheap one".
5.  **Track**: After buying, ask "Track order [ORD-ID]".

---

## 📂 Project Structure

```
ucp/
├── src/
│   ├── agent/          # Gemini Agent & Tools
│   └── server/         # FastAPI UCP Server
├── frontend/           # React Web App
├── data/               # SQLite Databases (Products/Orders)
└── README.md           # This file
```

---

*Note: `plan.md` and testing scripts have been excluded from this repository structure for cleanliness.*
