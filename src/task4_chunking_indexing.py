"""
Task 4 — Chunking, embedding và indexing.
Author / Maintainer: Nguyễn Mạnh Cường (2A202602650) - Retrieval Engineer

Hướng dẫn:
    1. Đọc toàn bộ Markdown trong data/standardized/.
    2. Chia văn bản bằng strategy đã chọn (RecursiveCharacterTextSplitter).
    3. Embed chunks bằng provider được cấu hình (Gemini, OpenAI, hoặc SentenceTransformers).
    4. Upsert vào ChromaDB với cosine distance.

Mỗi document/chunk tuân thủ docs/MODULE_CONTRACTS.md.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

STANDARDIZED_DIR = Path(__file__).resolve().parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).resolve().parent.parent / "chroma_db"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "gemini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
EMBEDDING_DIM = 3072 if "gemini" in EMBEDDING_PROVIDER else 1536

COLLECTION_NAME = "rag_documents"


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Tạo embedding vector cho danh sách văn bản theo provider được cấu hình."""
    if not texts:
        return []

    provider = os.getenv("EMBEDDING_PROVIDER", EMBEDDING_PROVIDER).lower()
    base_url = os.getenv("EMBEDDING_BASE_URL", "").strip() or None
    api_key = (
        os.getenv("EMBEDDING_API_KEY", "").strip()
        or os.getenv("GEMINI_API_KEY", "").strip()
        or os.getenv("OPENAI_API_KEY", "").strip()
    )
    model = os.getenv("EMBEDDING_MODEL") or "gemini-embedding-2"

    if base_url or provider == "openai":
        import time
        from openai import OpenAI

        client = OpenAI(api_key=api_key, base_url=base_url)
        vectors = []
        batch_size = 20
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            success = False
            last_err = None
            for attempt in range(5):
                try:
                    response = client.embeddings.create(input=batch, model=model)
                    for item in response.data:
                        vectors.append(item.embedding)
                    success = True
                    break
                except Exception as e:
                    last_err = e
                    wait_sec = 2 ** (attempt + 1)
                    print(f"Embedding attempt {attempt+1} failed: {e}. Retrying in {wait_sec}s...")
                    time.sleep(wait_sec)
            if not success:
                raise RuntimeError(f"Failed to embed batch after 5 attempts: {last_err}")
            time.sleep(0.5)
        return vectors

    elif provider == "gemini":
        import time
        from google import genai
        client = genai.Client(api_key=api_key)
        vectors = []
        batch_size = 20
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            success = False
            last_err = None
            for attempt in range(5):
                try:
                    response = client.models.embed_content(
                        model=model,
                        contents=batch,
                    )
                    for emb in response.embeddings:
                        vectors.append(emb.values)
                    success = True
                    break
                except Exception as e:
                    last_err = e
                    wait_sec = 2 ** (attempt + 1)
                    print(f"Embedding attempt {attempt+1} failed: {e}. Retrying in {wait_sec}s...")
                    time.sleep(wait_sec)
            if not success:
                raise RuntimeError(f"Failed to embed batch after 5 attempts: {last_err}")
            time.sleep(1.0)  # Throttling to respect RPM
        return vectors

    elif provider == "sentence_transformers":
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(os.getenv("EMBEDDING_MODEL") or "BAAI/bge-m3")
        return model.encode(texts).tolist()

    else:
        # Fallback to local deterministic mock / fallback vector if no key
        import hashlib
        vectors = []
        for text in texts:
            h = hashlib.sha256(text.encode("utf-8")).digest()
            vec = [(b / 255.0) for b in h[:32]]
            vectors.append(vec)
        return vectors


def get_collection():
    """Mở Chroma collection dùng cosine distance."""
    import chromadb
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def load_documents() -> list[dict]:
    """Đọc Markdown và trả về danh sách Document theo contract."""
    documents = []
    if not STANDARDIZED_DIR.exists():
        return documents

    for path in STANDARDIZED_DIR.rglob("*.md"):
        doc_type = "legal" if "legal" in path.parts else "news"
        doc_id = path.relative_to(STANDARDIZED_DIR).as_posix()
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue

        # Extract url if present in metadata header
        url = None
        for line in content.splitlines()[:5]:
            if line.startswith("**Source:**"):
                url = line.split("**Source:**", 1)[-1].strip()
                break

        documents.append({
            "id": doc_id,
            "content": content,
            "metadata": {
                "source": path.name,
                "title": path.stem.replace("_", " ").title(),
                "doc_type": doc_type,
                "url": url,
            },
        })
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chia Document thành chunks có id và chunk_index duy nhất và ổn định."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = []
    for document in documents:
        split_texts = splitter.split_text(document["content"])
        if not split_texts and document["content"].strip():
            split_texts = [document["content"].strip()]

        for index, text in enumerate(split_texts):
            chunks.append({
                "id": f"{document['id']}::chunk-{index}",
                "content": text,
                "metadata": {
                    "source": document["metadata"]["source"],
                    "title": document["metadata"]["title"],
                    "doc_type": document["metadata"]["doc_type"],
                    "url": document["metadata"]["url"],
                    "chunk_index": index,
                },
            })
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Thêm embedding vào từng chunk."""
    if not chunks:
        return []
    texts = [chunk["content"] for chunk in chunks]
    vectors = embed_texts(texts)
    for chunk, vector in zip(chunks, vectors):
        chunk["embedding"] = vector
    return chunks


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert chunks vào ChromaDB."""
    if not chunks:
        return

    collection = get_collection()
    # Batch upsert in chunks of 50
    batch_size = 50
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        collection.upsert(
            ids=[chunk["id"] for chunk in batch],
            documents=[chunk["content"] for chunk in batch],
            embeddings=[chunk["embedding"] for chunk in batch],
            metadatas=[chunk["metadata"] for chunk in batch],
        )


def run_pipeline() -> None:
    """Chạy load, chunk, embed và index."""
    documents = load_documents()
    print(f"Loaded {len(documents)} documents")
    chunks = chunk_documents(documents)
    print(f"Created {len(chunks)} chunks")
    embedded_chunks = embed_chunks(chunks)
    index_to_vectorstore(embedded_chunks)
    print(f"Indexed {len(embedded_chunks)} chunks into ChromaDB")


if __name__ == "__main__":
    run_pipeline()
