"""
Task 9 — Retrieval pipeline hoàn chỉnh.

Luồng xử lý:
    1. Chạy semantic_search.
    2. Lấy best cosine score gốc từ dense results.
    3. Nếu score dưới threshold, thử PageIndex fallback.
    4. Nếu score >= threshold hoặc fallback không có kết quả/lỗi:
       Chạy lexical_search và fuse bằng RRF đúng một lần.

Không so sánh threshold với RRF score vì hai thang đo khác nhau.
"""

from .task5_semantic_search import semantic_search
from .task6_lexical_search import lexical_search
from .task7_reranking import rerank_rrf
from .task8_pageindex_vectorless import pageindex_search


SCORE_THRESHOLD = 0.3
DEFAULT_TOP_K = 5


VI_EN_KEYWORDS = {
    "vé": "ticket tickets admission",
    "giá": "price cost fee deposit gbp",
    "tiền": "payment balance deposit fee",
    "chủ nhật": "sunday ticket",
    "cấm": "prohibited ban forbidden confiscated",
    "vật dụng": "items glass weapon",
    "đồ": "items belongings pack",
    "lều": "campsite tent tents gazebo",
    "cắm trại": "camp campsite camping",
    "chó": "dog dogs assistance guide",
    "khuyết tật": "access accessible disability nimbus",
    "trợ lý": "pa personal assistant complimentary",
    "xe buýt": "bus coach shuttle national express",
    "tàu": "train railway castle cary",
    "xe đạp": "cycling bike sustrans",
    "di chuyển": "travel journey transport",
    "ứng dụng": "app mobile vodafone",
    "sạc": "charge battery power pack",
    "hoàn": "refund cancel cancellation",
    "hủy": "cancel cancellation refund fee",
    "rượu": "alcohol challenge 21 bar",
    "trẻ em": "children under 16 adult supervision",
    "quảng cáo": "commercial marketing hashtag ad gifted",
}


def expand_query_for_bm25(query: str) -> str:
    """Bổ sung từ khóa tiếng Anh nếu query bằng tiếng Việt để BM25 tìm chính xác."""
    q_lower = query.lower()
    additions = []
    for vi_word, en_words in VI_EN_KEYWORDS.items():
        if vi_word in q_lower:
            additions.append(en_words)
    if additions:
        return f"{query} {' '.join(additions)}"
    return query


def retrieve(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = SCORE_THRESHOLD,
    use_reranking: bool = True,
) -> list[dict]:
    """Trả về hybrid hoặc pageindex SearchResult."""
    if not query.strip() or top_k <= 0:
        return []

    # 1. Truy xuất Dense
    dense = semantic_search(query, top_k=top_k * 2)
    best_dense_score = dense[0]["score"] if dense else 0.0

    # 2. Kiểm tra điều kiện Fallback theo điểm Cosine gốc
    if best_dense_score < score_threshold:
        try:
            fallback = pageindex_search(query, top_k=top_k)
            if fallback:
                return fallback
        except Exception as e:
            pass

    # 3. Luồng chính: Kết hợp Dense và Sparse qua RRF
    sparse_query = expand_query_for_bm25(query)
    sparse = lexical_search(sparse_query, top_k=top_k * 2)
    if use_reranking:
        hybrid = rerank_rrf([dense, sparse], top_k=top_k)
        return hybrid
    return dense[:top_k]


if __name__ == "__main__":
    for result in retrieve("ticket price", top_k=3):
        print(result)
