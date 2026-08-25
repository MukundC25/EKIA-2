# EKIA: AI Debugging Assistant

<div align="center">

```
  ███████╗██╗  ██╗██╗ █████╗
  ██╔════╝██║ ██╔╝██║██╔══██╗
  █████╗  █████╔╝ ██║███████║
  ██╔══╝  ██╔═██╗ ██║██╔══██║
  ███████╗██║  ██╗██║██║  ██║
  ╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝
```

**Production-grade AI Debugging Assistant**
*LangGraph · Llama3 (Groq) · FAISS · Neo4j GraphRAG · FastAPI · React*

**EKIA** — Error & Knowledge Intelligence Assistant

</div>


---

## Demo




https://github.com/user-attachments/assets/c5165148-ea17-4b85-8e14-fdc64ba22577




---

## Architecture

```
React Frontend (Vite)
       ↓ HTTP / Proxy
FastAPI Backend (Python)
       ↓
LangGraph Agent Pipeline
   ┌── 1. Query Parser Node    → Extracts error type, language, context
   ├── 2. Retriever Node       → FAISS semantic search + Neo4j graph context
   ├── 3. Reasoning Node       → Llama3 via Groq (blazing fast cloud API)
   ├── 4. Validation Node      → Confidence scoring + schema validation
   └── 5. Response Node        → Structured JSON output
       ↓
Langfuse (Tracing, Scoring, Evaluation)
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **LLM** | Groq / Llama3 (cloud API) |
| **Embeddings** | HuggingFace `all-MiniLM-L6-v2` |
| **Vector DB** | FAISS (local) |
| **Graph DB** | Neo4j (Desktop) |
| **Agent Framework** | LangGraph + LangChain |
| **Backend** | FastAPI + Pydantic |
| **Observability** | Langfuse |
| **Frontend** | React + Vite + react-force-graph-2d |

---

## Quick Start

### Prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| Python 3.11+ | Backend | [python.org](https://python.org) |
| Groq API Key | LLM Provider | [console.groq.com](https://console.groq.com/keys) |
| Neo4j Desktop | Graph DB | [neo4j.com/download](https://neo4j.com/download/) |
| Node.js 18+ | Frontend | [nodejs.org](https://nodejs.org) |

### Step 1 — Clone and configure

```bash
git clone <your-repo-url>
cd EKIA-2
cp .env.example .env
# Edit .env with your Neo4j password, Langfuse keys, and GROQ_API_KEY
```

### Step 2 — Install Python dependencies

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3 — Get a free Groq API key

1. Visit [console.groq.com/keys](https://console.groq.com/keys)
2. Create an API key
3. Add it to your `.env` file as `GROQ_API_KEY`

### Step 4 — Start Neo4j Desktop

1. Open **Neo4j Desktop**
2. Create a new database → Start it
3. Note your password and update `.env`

### Step 5 — Seed the knowledge graph

```bash
# Ingest 25 errors into Neo4j
python -m graph.ingest_graph
```

### Step 6 — Start the backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will auto-build the FAISS index on first startup.

### Step 7 — Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** 🎉

---

## API Reference

### `POST /api/debug`

Analyze an error using the full EKIA agent pipeline.

**Request:**
```json
{
  "error": "NullPointerException",
  "language": "java",
  "context": "Calling getName() on a user object that might be null",
  "code_snippet": "User user = repo.findById(id);\nSystem.out.println(user.getName());"
}
```

**Response:**
```json
{
  "error": "NullPointerException",
  "root_cause": "...",
  "beginner_explanation": "...",
  "technical_explanation": "...",
  "fix": "...",
  "related_concepts": ["Optional", "Null Safety"],
  "practice_problems": ["LeetCode 206 - Reverse Linked List"],
  "confidence_score": 0.92,
  "sources": ["NullPointerException (Java)"],
  "trace_id": "tr-abc123"
}
```

### `GET /api/graph/`

Returns nodes and edges for the knowledge graph visualization.

### `GET /api/graph/search?error=NullPointerException`

Search graph for a specific error and get its neighborhood.

### `GET /health`

System health check including RAG, graph, and LLM status.

---

## Project Structure

```
EKIA-2/
├── app/                        # FastAPI backend
│   ├── main.py                 # App entry + lifespan + CORS
│   ├── routes/
│   │   ├── debug.py            # POST /api/debug
│   │   └── graph.py            # GET /api/graph/*
│   ├── services/
│   │   ├── agent_service.py    # Orchestrates LangGraph pipeline
│   │   ├── rag_service.py      # FAISS vector store management
│   │   ├── graph_service.py    # Neo4j driver + queries
│   │   └── evaluation.py       # Langfuse tracing + scoring
│   ├── models/
│   │   └── schemas.py          # All Pydantic models
│   └── utils/
│       └── parser.py           # Query rewriting utility
│
├── agent/
│   ├── langgraph_flow.py       # 5-node StateGraph pipeline
│   └── prompts.py              # All LLM prompts
│
├── rag/
│   ├── embeddings.py           # HuggingFace embedding model
│   ├── vector_store.py         # FAISS build/load/save
│   └── retriever.py            # Semantic search interface
│
├── graph/
│   ├── neo4j_schema.cypher     # Full graph schema
│   └── ingest_graph.py         # Knowledge base → Neo4j
│
├── data/
│   └── error_knowledge_base/
│       └── errors.json         # 25 curated error entries
│
├── frontend/                   # Vite + React app
│   └── src/
│       ├── components/         # Reusable UI components
│       ├── pages/              # Debugger, GraphExplorer, History
│       └── services/api.js     # Axios client
│
├── tests/
│   ├── test_rag.py             # RAG layer tests
│   ├── test_agent.py           # Agent pipeline tests
│   └── test_api.py             # FastAPI route tests
│
├── .env.example
├── requirements.txt
└── docker-compose.yml
```

---

## Running Tests

```bash
# Activate virtual environment first
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Individual suites
pytest tests/test_rag.py -v     # Vector store tests
pytest tests/test_agent.py -v   # Parser + agent tests
pytest tests/test_api.py -v     # API route tests (uses mocks)
```

---

## Knowledge Graph Schema

```cypher
(Error)-[:CAUSED_BY]->(Concept)
(Error)-[:FIXED_BY]->(Fix)
(Error)-[:IN_LANGUAGE]->(Language)
(Error)-[:RELATED_TO]->(Concept)
(Concept)-[:PRACTICED_BY]->(Problem)
```

Covers **25 errors** across Java, Python, JavaScript, React, C++, SQL, Docker/K8s.

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Your Groq API key (`gsk_...`) |
| `EMBEDDING_MODEL` | HuggingFace model (`sentence-transformers/all-MiniLM-L6-v2`) |
| `NEO4J_URI` | Neo4j connection URI |
| `NEO4J_USERNAME` | Neo4j username |
| `NEO4J_PASSWORD` | Neo4j password |
| `LANGFUSE_PUBLIC_KEY` | Langfuse public key |
| `LANGFUSE_SECRET_KEY` | Langfuse secret key |
| `LANGFUSE_HOST` | Langfuse host URL |

---

## Features

- **Cloud AI** — Llama3 via Groq API for blazing fast inference
- **Hybrid Retrieval** — FAISS semantic search + Neo4j graph traversal
- **Observability** — Every session traced and scored in Langfuse
- **Premium UI** — Dark mode, glassmorphism, animated graph visualization
- **Production Ready** — Pydantic schemas, proper error handling, Docker support
- **25 Error Knowledge Base** — Java, Python, JS, C++, SQL, Docker errors

---

<div align="center">
  Built with ❤️ for software engineers
</div>
