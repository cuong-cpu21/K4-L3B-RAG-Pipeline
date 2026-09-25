"""
Task 10 — Generation có citation.

Hướng dẫn:
    1. Retrieve top-k chunks.
    2. Reorder để giảm lost-in-the-middle.
    3. Format context kèm title và source.
    4. Gọi provider được chọn trong .env.
    5. Trả answer, sources và retrieval_source.

Nếu context không đủ hoặc provider lỗi, trả safe refusal; không bịa thông tin.
"""

import os
from dotenv import load_dotenv

from .task9_retrieval_pipeline import retrieve

load_dotenv()

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
LLM_MODEL = os.getenv("LLM_MODEL", "")

SYSTEM_PROMPT = """Bạn là trợ lý giải đáp thông tin về Lễ hội Glastonbury 2025.
Trả lời câu hỏi CHỈ DỰA TRÊN NGỮ CẢNH ĐƯỢC CUNG CẤP.
Với mỗi khẳng định trong câu trả lời, hãy đính kèm trích dẫn số thứ tự tài liệu (ví dụ: [Document 1], [Document 2]).
Nếu thông tin trong ngữ cảnh không đủ để trả lời câu hỏi, hãy từ chối xác minh một cách an toàn và lịch sự."""


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Đưa chunks quan trọng về đầu và cuối context (Lost-in-the-middle mitigation)."""
    if len(chunks) <= 2:
        return list(chunks)
    front = chunks[::2]
    back = chunks[1::2]
    return front + back[::-1]


def format_context(chunks: list[dict]) -> str:
    """Tạo context có title và source label."""
    parts = []
    for index, chunk in enumerate(chunks, 1):
        metadata = chunk.get("metadata", {})
        title = metadata.get("title", "Untitled")
        source = metadata.get("source", "Unknown")
        content = chunk.get("content", "").strip()
        parts.append(
            f"[Document {index} | Title: {title} | Source: {source}]\n{content}"
        )
    return "\n\n---\n\n".join(parts)


def call_llm(system_prompt: str, user_message: str) -> str:
    """Gọi Gemini, OpenAI hoặc Anthropic theo cấu hình."""
    provider = os.getenv("LLM_PROVIDER", LLM_PROVIDER).lower()

    if provider == "gemini":
        import time
        from google import genai
        api_key = os.getenv("GEMINI_API_KEY", "")
        client = genai.Client(api_key=api_key)
        preferred_model = os.getenv("LLM_MODEL") or "gemini-3.5-flash"
        
        # Danh sách mô hình dự phòng không trùng lặp
        raw_candidates = [preferred_model, "gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-3.6-flash"]
        candidate_models = list(dict.fromkeys(raw_candidates))

        full_prompt = f"{system_prompt}\n\n{user_message}"
        for model_name in candidate_models:
            for attempt in range(2):
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=full_prompt,
                    )
                    if response.text and response.text.strip():
                        return response.text.strip()
                except Exception as exc:
                    err_msg = str(exc)
                    if ("503" in err_msg or "UNAVAILABLE" in err_msg) and attempt == 0:
                        time.sleep(1.0)
                        continue
                    print(f"Model {model_name} failed: {exc}, trying next fallback...")
                    break
        return "Tôi không thể xác minh thông tin này từ nguồn hiện có."

    elif provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
        model = os.getenv("LLM_MODEL") or "gpt-4o-mini"
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=TEMPERATURE,
        )
        return response.choices[0].message.content.strip()

    elif provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
        model = os.getenv("LLM_MODEL") or "claude-3-5-sonnet-20241022"
        response = client.messages.create(
            model=model,
            max_tokens=1000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            temperature=TEMPERATURE,
        )
        return response.content[0].text.strip()

    else:
        # Fallback text if provider not recognized or offline test
        return "Tôi không thể xác minh thông tin này từ nguồn hiện có."


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Trả về GenerationResult chuẩn contract."""
    chunks = retrieve(query, top_k=top_k)
    if not chunks:
        return {
            "answer": "Tôi không thể xác minh thông tin này từ nguồn hiện có.",
            "sources": [],
            "retrieval_source": "none",
        }

    reordered = reorder_for_llm(chunks)
    context = format_context(reordered)
    user_message = f"Ngữ cảnh trích dẫn:\n{context}\n\nCâu hỏi: {query}"

    try:
        answer = call_llm(SYSTEM_PROMPT, user_message)
        if not answer.strip():
            answer = "Tôi không thể xác minh thông tin này từ nguồn hiện có."
    except Exception as e:
        print(f"LLM Generation error: {e}")
        answer = "Tôi không thể xác minh thông tin này từ nguồn hiện có."

    # Xác định retrieval_source theo hợp đồng: 'hybrid' | 'pageindex' | 'none'
    first_method = chunks[0].get("retrieval_method", "hybrid")
    if first_method == "pageindex":
        retrieval_source = "pageindex"
    elif first_method in {"dense", "bm25", "hybrid"}:
        retrieval_source = "hybrid"
    else:
        retrieval_source = "none"

    return {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": retrieval_source,
    }


if __name__ == "__main__":
    result = generate_with_citation("Giá vé Glastonbury 2025 là bao nhiêu?")
    print("Answer:", result["answer"])
    print("Sources count:", len(result["sources"]))
