from typing import Dict
import os
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory, RedisChatMessageHistory

_in_memory_store: Dict[str, ChatMessageHistory] = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """Return a chat history bound to `session_id`.
    Uses Redis if REDIS_URL is set, otherwise in-memory store.
    """
    url = os.getenv("REDIS_URL", "").strip()
    if url:
        return RedisChatMessageHistory(session_id=session_id, url=url)
    if session_id not in _in_memory_store:
        _in_memory_store[session_id] = ChatMessageHistory()
    return _in_memory_store[session_id]

def clear_session(session_id: str) -> None:
    url = os.getenv("REDIS_URL", "").strip()
    if url:
        RedisChatMessageHistory(session_id=session_id, url=url).clear()
    else:
        _in_memory_store.pop(session_id, None)
