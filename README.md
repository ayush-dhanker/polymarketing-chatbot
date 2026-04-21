# 📈 PolyMarketing Assistant

A domain-specific conversational AI assistant for marketing professionals, built with LangGraph, Groq (LLaMA 3.3 70B), and Streamlit. Features persistent conversation state, time travel (state rewind), and a two-layer guardrails system — containerized with Docker.

---

## 🚀 Features

- **Conversational AI** — Marketing-focused assistant powered by LLaMA 3.3 70B via Groq
- **Persistent Memory** — Conversations saved to SQLite via LangGraph checkpointing, surviving server restarts
- **Time Travel** — Rewind to any previous checkpoint and branch the conversation from that point
- **Two-Layer Guardrails** — Keyword-based hard block + LLM-based topic classifier to keep conversations on-topic
- **Streamlit UI** — Clean chat interface with sidebar checkpoint history
- **Docker Ready** — Fully containerized with persistent volume for checkpoint storage

---

## 🏗️ Architecture

```
User Input
    ↓
[Guardrail Node] ── blocked ──→ ⚠️ Rejection message
    ↓ safe
[Assistant Node]
    ↓
Groq LLM (LLaMA 3.3 70B)
    ↓
Response + Checkpoint saved to SQLite
```

### Guardrails — Two Layers

| Layer | Method | Blocks |
|---|---|---|
| Hard block | Keyword matching | Harmful content (weapons, violence, etc.) |
| Soft block | LLM classifier | Off-topic content (non-marketing questions) |

Fast keyword check runs first (cheap), LLM classifier only runs if keywords pass (smart).

---

## 🗂️ Project Structure

```
polymarketing-chatbot/
├── app/
│   ├── __init__.py
│   ├── graph.py          # LangGraph graph definition
│   ├── state.py          # Shared state (TypedDict)
│   ├── nodes.py          # Guardrail + Assistant nodes
│   └── checkpointer.py   # SQLite checkpointer setup
├── ui/
│   └── streamlit_app.py  # Streamlit chat interface
├── .env                  # API keys (not committed)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## ⚙️ Setup

### Prerequisites
- Python 3.12+
- Docker (for containerized run)
- Groq API key — free at [console.groq.com](https://console.groq.com)

### Local Setup

```bash
# Clone the repo
git clone https://github.com/your-username/polymarketing-chatbot
cd polymarketing-chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Add your Groq API key
echo "GROQ_API_KEY=your_key_here" > .env

# Run the app
streamlit run ui/streamlit_app.py
```

### Docker Setup

```bash
# Build and run
docker-compose up --build

# Open in browser
http://localhost:8501
```

---

## 🧠 Key Design Decisions

### 1. SQLite over In-Memory Checkpointing
LangGraph supports `InMemorySaver` out of the box, but I chose `SqliteSaver` because production chatbots must survive server restarts. The checkpointer is injected at graph compile time, making it a swappable component — SQLite locally, PostgreSQL in production — without changing any graph logic.

### 2. Guardrails Outside the Happy Path
Guardrails run as the first node on every execution, including time travel replays. This ensures that rewinding to a previous state and branching never bypasses safety checks — a real vulnerability in naive implementations where guardrails only run once.

### 3. Docker Volume for Checkpoint Persistence
`checkpoints.db` is mounted as a Docker volume rather than stored inside the container. This means conversation history survives container restarts — the same principle as mounting a production database volume.

---

## 🔧 What I'd Improve Next

- **Per-user checkpoint namespacing** — currently all sessions share one SQLite file. In production, each user would have isolated storage with access control.
- **Swap SQLite → PostgreSQL** — `langgraph-checkpoint-postgres` is a one-line change in `checkpointer.py`, making this production-ready for multi-user deployments.
- **LLM-based guardrail upgrade** — replace keyword list with a dedicated safety classifier model for more robust harmful content detection.
- **Streaming responses** — use LangGraph's streaming mode so responses appear token by token, improving perceived latency.

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| LangGraph | Graph-based agent orchestration + checkpointing |
| LangChain | LLM abstractions + message types |
| Groq (LLaMA 3.3 70B) | Fast, free LLM inference |
| SQLite | Local checkpoint persistence |
| Streamlit | Chat UI |
| Docker | Containerization |
| Python 3.12 | Runtime |

---

## 📚 Concepts Demonstrated

- **Agentic AI** — multi-node graph with conditional routing
- **State persistence** — checkpoint-based conversation memory
- **Time travel** — branching from historical states
- **Guardrails** — two-layer input validation pattern
- **MLOps thinking** — swappable components, Docker volumes, production-aware design

---

## 👤 Author

**Ayush** — M.Sc. Data & Knowledge Engineering, Otto-von-Guericke University Magdeburg  
Built as part of a 7-week Agentic AI learning curriculum using LangGraph.