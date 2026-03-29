# ET AI Concierge — Demo Script
**Duration: ~4–5 minutes | Audience: Judges / ET Stakeholders**

---

## 🎬 OPENING — Hook (0:00–0:30)

> *[Open the landing page at localhost:3000]*

"Imagine you walk into a bank. Instead of being handed a brochure and left to figure things out yourself — a brilliant financial advisor greets you, learns who you are in three minutes, and then says: *here's exactly what you need, and here's why.*

That's ET AI Concierge.

Economic Times has built one of India's most powerful financial ecosystems — ET Money, ET Markets, masterclasses, insurance, loans, wealth summits. But studies show most users discover **less than 10%** of what ET offers.

We built an AI that fixes that."

---

## 🧩 PROBLEM + SOLUTION OVERVIEW (0:30–1:00)

> *[Scroll through the feature grid on the landing page]*

"The problem isn't content — ET has plenty. The problem is **discovery and personalisation**.

Our solution has four components that directly map to the problem statement:

- **ET Welcome Concierge** — a chat agent that profiles you in one conversation
- **Financial Life Navigator** — a RAG-powered assistant that answers your financial questions using ET's knowledge base
- **Cross-Sell Recommendation Engine** — scores and ranks ET products based on who you are and how you behave
- **Services Marketplace Agent** — finds the right loan, insurance, or credit card for your specific profile

Let me show you how each of these works — live."

---

## 💬 LIVE DEMO — ONBOARDING CHAT (1:00–2:15)

> *[Navigate to /chat]*

"This is ET Concierge. A new user lands here — no forms, no dropdowns. Just a conversation.

Watch what happens when I type."

> *[Type]: "Hi, I'm Nimish, 22 years old, software engineering student"*

"The LLM — powered by **Groq's llama-3.3-70b** — responds instantly. It asks one question at a time, naturally covering seven key profiling areas: income, goals, existing investments, risk tolerance, immediate needs, and ET familiarity.

Now, technically, what's happening behind the scenes:

Every message hits our **FastAPI backend** at `POST /chat`. The full conversation history is sent stateless — no session management needed. The backend routes to our LLM service, which calls Groq with a carefully engineered system prompt that keeps responses under 80 words and asks exactly one question per turn."

> *[Continue the conversation to completion — answer 5–6 questions]*

"The moment the LLM has enough information, it signals completion with a specific phrase. Our backend detects this, and immediately fires a **second Groq call at temperature 0.1** — near-deterministic — to extract a structured JSON financial profile:

```
persona: student
risk_level: conservative
goals: [start SIP, build habits, financial independence]
interests: [SIP, mutual funds, cryptocurrency]
```

This profile is stored in **Weaviate** — our vector database that handles both structured data and semantic search in one system. No separate SQL database needed."

---

## 📊 LIVE DEMO — DASHBOARD (2:15–3:00)

> *[Navigate to /dashboard]*

"Instantly, the dashboard lights up.

Here's the user's **financial persona card** — student, conservative risk profile — extracted purely from the conversation.

Below it, **AI-ranked product recommendations**. These come from our scoring engine, which evaluates every ET product using a three-factor formula:

- **Interest weight** — how much the user's stated interests match the product's tags
- **Persona and risk match** — does this product suit their life stage?
- **Behaviour weight** — based on their clicks, searches, and time spent across ET

Each recommendation has a score from 0 to 100, a progress bar, and an AI-generated one-line reason — *'Matches your student profile and interest in SIP investments'* — and a direct link to the ET product page.

As the user interacts — clicking products, searching articles — our `POST /events` endpoint logs every action. The recommendations dynamically re-rank when they click Refresh."

---

## 🔍 LIVE DEMO — RAG FINANCIAL Q&A (3:00–3:40)

> *[Go back to /chat and type a financial question]*

> *[Type]: "Should I invest in ELSS or a regular mutual fund to save tax?"*

"Now the user has a profile, so the system switches to **RAG mode** — Retrieval-Augmented Generation.

The question is embedded locally using **sentence-transformers all-MiniLM-L6-v2** — an 80MB model that runs entirely on our server, zero API cost. The vector is used to search Weaviate's `FinancialContent` and `ETProduct` collections using **near-vector similarity**.

The top matching articles — *'Tax Saving with ELSS Funds'*, *'Understanding Mutual Fund Risk Levels'* — are pulled as context and passed to Groq alongside the user's profile.

The answer is personalised: knowing Nimish is a conservative student, the model recommends ELSS as a starting point with a cautious allocation strategy. Not generic advice — personalised guidance."

---

## 💼 BUSINESS IMPACT (3:40–4:30)

"Now let's talk about what this means for Economic Times as a business.

**Discovery is revenue.** If ET can guide users to one additional product — an SIP, a credit card, an insurance plan — the lifetime value of that customer multiplies.

Our system turns every ET touchpoint into a cross-sell opportunity. A user who read a stock article gets nudged toward ET Markets. Someone who asked about retirement planning gets recommended NPS. Someone who logged a search event for *'credit card'* sees the ET Rewards Card at the top of their dashboard next time.

**Scale:** Because we use Groq's free tier and local embeddings, the marginal cost per user is near zero. The system can handle thousands of simultaneous conversations without any API cost increase.

**Personalisation at depth:** Most recommendation systems are collaborative filtering — they look at what similar users did. We go deeper — we understand *this user's* stated goals, risk level, and life stage within three minutes of their first visit.

**EThas 10 million+ users.** Even moving from 10% product discovery to 20% represents millions of new product interactions — and significant revenue uplift across ET's financial services partnerships."

---

## 🚀 CLOSING (4:30–5:00)

"To summarise what we built:

A **full-stack, production-ready AI platform** — FastAPI backend, Next.js frontend, Groq LLM, Weaviate vector database — entirely on free-tier infrastructure.

It covers all four problem statement requirements: conversational profiling, financial Q&A navigation, cross-sell recommendations, and services marketplace matching.

The code is live on GitHub at **github.com/nimish1402/ET-Concierge**, fully documented, with a one-command seed script to populate the knowledge base.

ET AI Concierge doesn't just answer questions. It understands people — and then connects them to everything ET has to offer.

Thank you."

---

## 📌 Quick Reference — Key Technical Talking Points

| What you say | Underlying tech |
|---|---|
| "Instant responses" | Groq free tier — <500ms LLM calls |
| "No forms or dropdowns" | Stateless chat — full history per request |
| "Structured profile from conversation" | Groq @ temp 0.1, JSON extraction |
| "One database for everything" | Weaviate — vector + structured storage |
| "Personalised Q&A" | RAG: all-MiniLM-L6-v2 embed → Weaviate near_vector → Groq |
| "Dynamic recommendations" | Rule-based score: interest + persona + events |
| "Zero API cost for embeddings" | sentence-transformers runs locally |
| "Real-time typing effect" | SSE streaming via `/chat/stream` |
