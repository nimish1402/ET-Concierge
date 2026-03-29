<div align="center">

# 🤖 ET AI Concierge

**An intelligent financial assistant powered by the Economic Times ecosystem**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=flat&logo=next.js)](https://nextjs.org)
[![Weaviate](https://img.shields.io/badge/Weaviate-Vector_DB-green?style=flat)](https://weaviate.io)
[![Groq](https://img.shields.io/badge/LLM-Groq_llama3-orange?style=flat)](https://groq.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Live Demo](#) · [API Docs](http://localhost:8000/docs) · [Report Bug](https://github.com/nimish1402/ET-Concierge/issues)

</div>

---

## 📌 Overview

ET AI Concierge is a production-ready AI platform that understands users through a short 3-minute conversation, builds a structured **financial persona**, and recommends the most relevant ET products and services — powered entirely by **free-tier APIs**.

### Key Capabilities

| Feature | Description |
|---------|-------------|
| 🗣️ **ET Welcome Concierge** | Chat-based onboarding that builds your financial profile in 5–7 questions |
| 🧠 **Financial Life Navigator** | RAG-powered Q&A personalized to your profile using Weaviate vector search |
| 🎯 **Smart Recommendations** | Rule-based scoring engine ranks ET products by interest, persona, and behavior |
| 🛍️ **Services Marketplace** | Matches credit cards, loans, and insurance to your specific financial needs |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Next.js Frontend                      │
│         Landing  ·  Chat UI  ·  Dashboard               │
└──────────────────────┬──────────────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────────────┐
│                   FastAPI Backend                        │
│   /chat  /profile  /recommendations  /events  /user     │
└───────┬───────────────────────────────┬─────────────────┘
        │                               │
┌───────▼────────┐             ┌────────▼────────────┐
│   Groq LLM     │             │   Weaviate (All-in) │
│ llama-3.3-70b  │             │  Users · Events     │
│ Chat · Profile │             │  Recommendations    │
│ RAG Answers    │             │  FinancialContent   │
└────────────────┘             │  ETProducts         │
                               └─────────────────────┘
        │
┌───────▼──────────────┐
│  sentence-transformers│
│  all-MiniLM-L6-v2    │
│  (local embeddings)  │
└──────────────────────┘
```

---

## 🧩 Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Frontend** | Next.js 14 (App Router) + Tailwind CSS | SSR, streaming, dark UI |
| **Backend** | FastAPI (Python 3.11+) | Async, modular, fast |
| **LLM** | Groq `llama-3.3-70b-versatile` | Free tier, ultra-fast |
| **Vector DB** | Weaviate (Cloud or local Docker) | Vector + structured storage in one |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` | Local, no API cost |

> **Zero paid APIs** — all services run on free tiers or open-source.

---

## 📁 Project Structure

```
ET Concierge/
├── docker-compose.yml          # Local Weaviate (optional)
├── .gitignore
│
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Settings from .env
│   ├── requirements.txt
│   ├── .env.example
│   │
│   ├── db/
│   │   └── weaviate_client.py  # Client singleton + schema init (5 collections)
│   │
│   ├── models/
│   │   └── schemas.py          # Pydantic request/response models
│   │
│   ├── services/
│   │   ├── llm_service.py       # Groq wrappers: chat, profiling, RAG answers
│   │   ├── rag_service.py       # Embedding + Weaviate near_vector search
│   │   └── recommendation_service.py  # Rule-based scoring engine
│   │
│   ├── routers/
│   │   ├── chat.py             # POST /chat, POST /chat/stream
│   │   ├── profile.py          # POST /profile/init, GET /profile/{id}
│   │   ├── events.py           # POST /events
│   │   ├── recommendations.py  # GET /recommendations, POST /recommendations/refresh
│   │   └── users.py            # GET /user/{id}
│   │
│   └── utils/
│       └── seed_data.py        # One-time data seeder (10 articles + 8 products)
│
└── frontend/
    ├── package.json
    ├── tailwind.config.js
    └── src/app/
        ├── page.tsx            # Landing page
        ├── chat/page.tsx       # AI Concierge chat interface
        └── dashboard/page.tsx  # Personalized recommendation dashboard
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (optional — only needed for local Weaviate)
- Free API keys: [Groq](https://console.groq.com) · [Weaviate Cloud](https://console.weaviate.cloud) *(or use local Docker)*

---

### 1. Clone the Repository

```bash
git clone https://github.com/nimish1402/ET-Concierge.git
cd ET-Concierge
```

---

### 2. Setup Weaviate

**Option A — Weaviate Cloud (Recommended, free sandbox cluster)**

1. Sign up at [console.weaviate.cloud](https://console.weaviate.cloud)
2. Create a free cluster and copy your **Cluster URL** and **API Key**

**Option B — Local Docker**

```bash
docker-compose up -d
# Weaviate will be available at http://localhost:8080
```

---

### 3. Setup Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

Create your `.env` file:

```bash
copy .env.example .env    # Windows
# cp .env.example .env    # macOS/Linux
```

Edit `.env` with your credentials:

```env
GROQ_API_KEY=gsk_...                    # https://console.groq.com
GEMINI_API_KEY=                         # Not required (Groq-only)

# Weaviate Cloud
WEAVIATE_URL=your-cluster.weaviate.cloud
WEAVIATE_API_KEY=your-api-key

# OR local Docker
# WEAVIATE_URL=http://localhost:8080
# WEAVIATE_API_KEY=

FRONTEND_URL=http://localhost:3000
```

Seed the knowledge base (run once):

```bash
python utils/seed_data.py
```

Start the backend:

```bash
uvicorn main:app --reload --port 8000
```

> API docs available at **http://localhost:8000/docs**

---

### 4. Setup Frontend

```bash
cd frontend
npm install
npm run dev
```

> Visit **http://localhost:3000**

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/chat` | Main chat (onboarding + RAG) |
| `POST` | `/chat/stream` | SSE streaming chat |
| `POST` | `/profile/init` | Create user profile manually |
| `GET` | `/profile/{user_id}` | Retrieve user profile |
| `POST` | `/events` | Log user behavior event |
| `GET` | `/recommendations?user_id=` | Get recommendations |
| `POST` | `/recommendations/refresh?user_id=` | Re-score recommendations |
| `GET` | `/user/{user_id}` | Get full user data |

### Example Requests

**Start a chat conversation:**
```json
POST /chat
{
  "user_id": null,
  "message": "Hi, I'm Nimish, 22 years old student",
  "history": []
}
```

**Response (after full onboarding):**
```json
{
  "reply": "Great! I now have a good picture of your financial goals...",
  "user_id": "uuid-here",
  "profile_complete": true
}
```

**Log a user event:**
```json
POST /events
{
  "user_id": "uuid-here",
  "event_type": "click",
  "metadata": { "category": "mutual_funds", "product": "SIP" }
}
```

---

## 🧠 How the AI Works

### 1. Conversational Profiling
The Groq LLM asks 5–7 targeted questions to understand the user. Once complete, it extracts a structured JSON profile:

```json
{
  "persona": "student",
  "risk_level": "conservative",
  "goals": ["start investing", "build financial habits"],
  "interests": ["sip", "mutual funds"],
  "recommended_products": ["ET Money SIP", "ET Markets"]
}
```

### 2. RAG Pipeline
```
User Query → sentence-transformers embedding → Weaviate near_vector search
→ Top-k relevant articles/products → Groq LLM answer with context
```

### 3. Recommendation Scoring
```
score = interest_weight (0–40) + persona_risk_weight (0–30) + behavior_weight (0–30)
```
Products are ranked by score and returned as the user's personalized dashboard.

---

## 🗄️ Weaviate Collections

| Collection | Type | Vectorized |
|------------|------|-----------|
| `User` | Structured profiles | ❌ |
| `Event` | User behavior logs | ❌ |
| `Recommendation` | Scored product recs | ❌ |
| `FinancialContent` | Articles & FAQs | ✅ (for RAG) |
| `ETProduct` | ET product catalog | ✅ (for RAG) |

---

## 🌐 Pages

| Route | Description |
|-------|-------------|
| `/` | Landing page with features and CTA |
| `/chat` | AI Concierge conversation interface |
| `/dashboard` | Personalized profile + recommendation cards |

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---


