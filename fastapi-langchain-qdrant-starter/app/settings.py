import os

def get_env(name: str, default: str | None = None, required: bool = False) -> str:
    val = os.getenv(name, default)
    if required and not val:
        raise RuntimeError(f"Missing required env var: {name}")
    return val

OPENAI_API_KEY = get_env("OPENAI_API_KEY", required=True)
OPENAI_MODEL = get_env("OPENAI_MODEL", "gpt-4o-mini")
EMBEDDING_MODEL = get_env("EMBEDDING_MODEL", "text-embedding-3-small")

QDRANT_HOST = get_env("QDRANT_HOST", "localhost")
QDRANT_PORT = int(get_env("QDRANT_PORT", "6333"))
QDRANT_COLLECTION = get_env("QDRANT_COLLECTION", "docs")
