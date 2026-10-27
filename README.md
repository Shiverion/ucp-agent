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

## System Design

### Requirements

**Functional**
- Discover products, search shop catalogs, create and complete checkout sessions, and retrieve orders through a UCP-style server.
- Let a Gemini shopping agent query multiple shop catalogs and present results in a React interface.

**Non-functional**
- The merchant API uses FastAPI and a local SQLite database; shop discovery/search and agent calls use HTTP.
- The federation agent queries configured shops concurrently with bounded HTTP timeouts.

### High-Level Architecture

```text
React/Vite client → FastAPI UCP merchant API → SQLite products / checkouts / orders
                 → Gemini shopping agent → federated shop search over HTTP
```

`src/server/multi_shop.py` runs three sample shops with static catalogs. Checkout and order handling are demo flows; no external payment processor is configured.

### Data Model / API Contract

| API group | Responsibility |
| --- | --- |
| `/.well-known/ucp` | Publish merchant capabilities |
| `/products*` | List, search, and retrieve catalog items |
| `/checkout-sessions*` | Create, update, complete, or cancel checkout sessions |
| `/orders/{order_id}` | Retrieve an order record |

### Scale and Reliability

- The sample shops and SQLite files are local single-process components; no shared production inventory service is configured.
- Federation search runs concurrently and uses a 10-second HTTP timeout per shop request.

### Trade-offs

| Decision | Benefit | Cost |
| --- | --- | --- |
| Use a local SQLite merchant store | Simple setup for protocol demonstrations | Limited coordination across multiple server replicas |
| Federate a small fixed set of shops | Shows cross-shop search behavior | Shop URLs and catalogs require explicit configuration |

### What to Revisit as It Grows

- Replace sample catalogs with merchant-owned inventory APIs.
- Add durable idempotency and payment-provider integration before processing real orders.
- Move shared order state to a database designed for concurrent deployments.

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

## 📚 Official Documentation

*   **UCP Specification**: [ucp.dev](https://ucp.dev) — Authoritative JSON schemas for Shopping, Checkout, and Discovery.
*   **Python SDK**: [github.com/Universal-Commerce-Protocol/python-sdk](https://github.com/Universal-Commerce-Protocol/python-sdk) — Core library for building UCP-compliant servers and agents.
*   **Samples Repository**: [github.com/Universal-Commerce-Protocol/samples](https://github.com/Universal-Commerce-Protocol/samples) — Full "Flower Shop" demo implementation.

---

