"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""

from typing import Any
import numpy as np
from rank_bm25 import BM25Okapi

CORPUS: list[dict] = []


def get_or_load_corpus() -> list[dict]:
    """Trả về CORPUS, nếu chưa có thì load và chunk từ standardized docs."""
    global CORPUS
    if not CORPUS:
        try:
            from .task4_chunking_indexing import load_documents, chunk_documents
            documents = load_documents()
            CORPUS = chunk_documents(documents)
        except Exception as e:
            print(f"Error loading corpus for BM25: {e}")
            CORPUS = []
    return CORPUS


def build_bm25_index(corpus: list[dict]) -> BM25Okapi:
    """Tạo BM25 index từ corpus chunks."""
    tokenized = [item["content"].lower().split() for item in corpus]
    return BM25Okapi(tokenized)


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    if not query.strip() or top_k <= 0:
        return []

    corpus = CORPUS if CORPUS else get_or_load_corpus()
    if not corpus:
        return []

    tokens = query.lower().split()
    if not tokens:
        return []

    bm25 = build_bm25_index(corpus)
    scores = bm25.get_scores(tokens)

    # Thêm term frequency boost nhỏ để giải quyết tie-break khi corpus siêu nhỏ (N=2, df=1 -> IDF=0)
    adjusted_scores = []
    for idx, raw_score in enumerate(scores):
        doc_words = corpus[idx]["content"].lower().split()
        match_count = sum(1 for w in tokens if w in doc_words)
        adjusted_score = float(raw_score) + (0.01 * match_count)
        adjusted_scores.append(adjusted_score)

    scores_arr = np.array(adjusted_scores)
    sorted_indices = np.argsort(scores_arr)[::-1]

    results = []
    seen_ids = set()
    for index in sorted_indices:
        score = float(scores_arr[index])
        item = corpus[index]
        item_id = item["id"]

        if item_id in seen_ids:
            continue
        seen_ids.add(item_id)

        results.append({
            "id": item_id,
            "content": item["content"],
            "score": score,
            "metadata": item["metadata"],
            "retrieval_method": "bm25",
        })
        if len(results) >= top_k:
            break

    # Đảm bảo sắp xếp giảm dần theo điểm số
    return sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]


if __name__ == "__main__":
    for result in lexical_search("ticket price", top_k=3):
        print(result)
