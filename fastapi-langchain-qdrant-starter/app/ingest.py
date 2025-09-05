from typing import Iterable, List
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from qdrant_client.http import models as rest
from .deps import get_vector_store, get_qdrant_client, get_embeddings
from . import settings

def load_documents(path: str) -> List[Document]:
    base_path = Path(path)
    if not base_path.exists():
        raise FileNotFoundError(f"Data path not found: {path}")

    # Load .txt and .md files; you can extend with PDF, etc.
    loaders = [
        DirectoryLoader(path, glob="**/*.txt", loader_cls=TextLoader, show_progress=True),
        DirectoryLoader(path, glob="**/*.md", loader_cls=TextLoader, show_progress=True),
    ]
    docs: List[Document] = []
    for loader in loaders:
        docs.extend(loader.load())
    return docs

def split_documents(docs: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    return splitter.split_documents(docs)

def recreate_collection_if_needed(dimension: int, force: bool = False):
    client = get_qdrant_client()
    name = settings.QDRANT_COLLECTION
    exists = name in [c.name for c in client.get_collections().collections]
    if force and exists:
        client.delete_collection(name)
        exists = False
    if not exists:
        client.create_collection(
            collection_name=name,
            vectors_config=rest.VectorParams(size=dimension, distance=rest.Distance.COSINE),
        )

def ingest_path(path: str, reset: bool = False) -> int:
    docs = load_documents(path)
    chunks = split_documents(docs)
    embeddings = get_embeddings()

    # Ensure collection exists (or recreate with correct dimension)
    recreate_collection_if_needed(dimension=embeddings.embed_query("dim-probe").__len__(), force=reset)

    vs = get_vector_store()
    vs.add_documents(chunks)
    return len(chunks)
