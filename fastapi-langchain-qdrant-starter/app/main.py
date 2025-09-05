from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory
from operator import itemgetter
from uuid import uuid4

from .deps import get_vector_store, get_llm
from .ingest import ingest_path
from .db import init_db, get_session
from .models import ChatSession, ChatMessage, ChatMessageRead
from .history import get_session_history, clear_session
from . import settings

app = FastAPI(title="FastAPI + LangChain + Qdrant (RAG) with Sessions + History")

@app.on_event("startup")
def _startup():
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: str
    message: str
    k: int = 4

class IngestRequest(BaseModel):
    path: str = "data/docs"
    reset: bool = False

@app.get("/health")
def health():
    return {"status": "ok"}

# ---- Session helpers ----
@app.post("/session")
def create_session():
    sid = str(uuid4())
    return {"session_id": sid}

@app.delete("/session/{session_id}")
def delete_session(session_id: str):
    clear_session(session_id)
    return {"deleted": session_id}

# ---- Ingest ----
@app.post("/ingest")
def ingest(req: IngestRequest):
    try:
        n = ingest_path(req.path, reset=req.reset)
        return {"ingested_chunks": n, "collection": settings.QDRANT_COLLECTION}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def format_docs(docs):
    return "\n\n".join([f"Fuente: {d.metadata.get('source', 'N/A')}\n{d.page_content}" for d in docs])

# ---- Conversational RAG ----
@app.post("/chat")
def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="message is empty")

    vs = get_vector_store()
    retriever = vs.as_retriever(search_kwargs={"k": req.k})
    llm = get_llm()

    # 1) Objetos de historial persistente/temporal
    history_obj = get_session_history(req.session_id)  
    # 2) Condensador de pregunta 
    condense_prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Reescribe la consulta del usuario como una pregunta independiente, breve y clara, "
         "usando el historial si aporta contexto. Devuelve solo la pregunta reescrita."),
        MessagesPlaceholder("history"),
        ("human", "{question}")
    ])
    standalone = condense_prompt | llm
    standalone = standalone.invoke({
        "question": req.message,
        "history": history_obj.messages,   # pasamos explícitamente la history al prompt
    }).content.strip() or req.message

    # 3) Recuperación con la pregunta condensada
    docs = retriever.get_relevant_documents(standalone)
    context_text = format_docs(docs)

    # 4) Prompt final con contexto + historial (todavía NO actualizamos historial)
    answer_prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Eres un asistente experto. Responde en español con precisión y cita fuentes cuando existan. "
         "Si no hay evidencia suficiente en el contexto, dilo explícitamente."
         "Si la pregunta no está relacionada con el contexto responde: 'Mi objetivo es ayudarte con temas sobre los productos, nada más'"
         "No asumas escenarios hipoteticos, no ayudes con preguntas generales."),
        MessagesPlaceholder("history"),
        ("human", "Pregunta: {question}\n\nContexto:\n{context}")
    ])
    messages = answer_prompt.format_messages(
        history=history_obj.messages,   # historial actual
        question=standalone,
        context=context_text
    )
    reply_msg = llm.invoke(messages)
    reply = reply_msg.content

    # 5) Ahora SÍ: actualizamos historial de la sesión (original del usuario y respuesta)
    history_obj.add_user_message(req.message)
    history_obj.add_ai_message(reply)

    # 6) (Opcional) Persistir en DB si añadiste SQLModel (sesión, mensajes y fuentes)
    try:
        from .db import get_session
        from .models import ChatSession, ChatMessage
        import json as _json
        with get_session() as s:
            if not s.get(ChatSession, req.session_id):
                s.add(ChatSession(session_id=req.session_id))
                s.commit()
            s.add(ChatMessage(session_id=req.session_id, role="user", content=req.message))
            s.add(ChatMessage(
                session_id=req.session_id,
                role="assistant",
                content=reply,
                standalone_question=standalone,
                sources_json=_json.dumps([{"source": d.metadata.get("source", "N/A")} for d in docs])
            ))
            s.commit()
    except Exception:
        # Si no tienes la parte de DB, ignoramos silenciosamente
        pass

    # 7) Respuesta HTTP con fuentes coherentes a la pregunta condensada
    sources = [{"source": d.metadata.get("source", "N/A")} for d in docs]
    return {"reply": reply, "sources": sources}



from typing import Optional
from fastapi import Query

@app.get("/sessions")
def list_sessions(limit: int = 50):
    with get_session() as s:
        rows = s.exec("""SELECT session_id, MIN(created_at) AS created_at
                          FROM chatsession
                          GROUP BY session_id
                          ORDER BY created_at DESC
                          LIMIT :lim""", {"lim": limit}).all() if False else s.query(ChatSession).order_by(ChatSession.created_at.desc()).limit(limit).all()
        return [{"session_id": r.session_id, "created_at": r.created_at.isoformat()} for r in rows]

@app.get("/session/{session_id}/messages", response_model=list[ChatMessageRead])
def get_session_messages(session_id: str, limit: int = 200):
    with get_session() as s:
        rows = s.query(ChatMessage).filter(ChatMessage.session_id==session_id).order_by(ChatMessage.created_at.asc()).limit(limit).all()
        out = []
        import json as _json
        for r in rows:
            out.append(ChatMessageRead(
                id=r.id,
                session_id=r.session_id,
                role=r.role,
                content=r.content,
                standalone_question=r.standalone_question,
                sources=_json.loads(r.sources_json) if r.sources_json else None,
                created_at=r.created_at,
            ))
        return out
