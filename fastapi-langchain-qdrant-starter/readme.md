# FastAPI + LangChain + Qdrant (RAG) – Starter

Stack:
- **FastAPI** (API REST)
- **LangChain** (LLM orchestration)
- **Qdrant** (Vector DB)
- **OpenAI API** (LLM + embeddings, OpenAI-compatible)

## 1) Requisitos
- Docker y Docker Compose
- Una API key de OpenAI (o compatible) en `.env`

## 2) Configuración
Crea `.env` a partir de `.env.example`:
```bash
cp .env.example .env
# edita .env y añade tu OPENAI_API_KEY
