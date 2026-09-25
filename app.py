import streamlit as st
from dotenv import load_dotenv
from src.task10_generation import generate_with_citation

load_dotenv()

st.set_page_config(
    page_title="Glastonbury 2025 RAG Assistant",
    page_icon="🎪",
    layout="wide",
)

# Khởi tạo lịch sử hội thoại trong session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Cấu hình thanh bên (Sidebar)
with st.sidebar:
    st.image("https://www.glastonburyfestivals.co.uk/wp-content/uploads/2024/04/Icon.png", width=70)
    st.title("🎪 Glastonbury 2025")
    st.markdown("**Trợ lý hỏi đáp thông minh RAG Pipeline**")
    st.caption("Chủ đề: Sự kiện & Lễ hội âm nhạc Glastonbury 2025")
    st.divider()

    st.subheader("⚙️ Cấu hình Truy xuất")
    top_k = st.slider("Số lượng ngữ cảnh (top_k chunks)", min_value=3, max_value=10, value=5)
    st.info("Pipeline: **Hybrid Retrieval**\n- Dense Search (ChromaDB)\n- Lexical Search (BM25Okapi)\n- Reciprocal Rank Fusion (RRF)\n- Vectorless Fallback")

    st.divider()
    st.subheader("💡 Câu hỏi gợi ý:")
    suggestions = [
        "Giá vé trọn gói Glastonbury 2025 là bao nhiêu?",
        "Ai đủ điều kiện nhận vé trợ lý cá nhân (PA)?",
        "Những vật dụng nào bị cấm mang vào lễ hội?",
        "Đi tàu hỏa đến lễ hội có xe buýt đưa đón không?",
        "Lều Vodafone Connect & Charge có dịch vụ gì?",
        "Quy định hoàn hủy vé ngày Chủ Nhật 2025?",
    ]
    for s in suggestions:
        if st.button(s, key=f"sug_{s}", use_container_width=True):
            st.session_state.pending_query = s

    st.divider()
    if st.button("🗑️ Xóa lịch sử trò chuyện", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Tiêu đề giao diện chính
st.title("🎪 Glastonbury Festival 2025 — RAG Assistant")
st.markdown(
    "Hệ thống trả lời câu hỏi dựa trên bộ tài liệu chính thức: quy định tiếp cận, điều khoản cắm trại, "
    "hướng dẫn vé ngày Chủ Nhật, sơ đồ biểu diễn, chuẩn bị đồ đạc và di chuyển bền vững."
)

# Hiển thị lịch sử chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander(f"📚 Nguồn trích dẫn ({len(msg['sources'])} tài liệu | Phương thức: {msg.get('retrieval_source', 'hybrid')})"):
                for idx, src in enumerate(msg["sources"], 1):
                    meta = src.get("metadata", {})
                    title = meta.get("title", "Tài liệu")
                    source = meta.get("source", "Nguồn")
                    score = src.get("score", 0.0)
                    method = src.get("retrieval_method", "hybrid")
                    url = meta.get("url")

                    st.markdown(f"**[Document {idx}] {title}** (`{source}`)")
                    st.caption(f"Score: `{score:.4f}` | Phương thức: `{method}` | Loại: `{meta.get('doc_type', 'N/A')}`")
                    if url:
                        st.markdown(f"🔗 [Xem bài viết gốc]({url})")
                    st.text(src.get("content", "")[:350] + ("..." if len(src.get("content", "")) > 350 else ""))
                    st.divider()

# Xử lý input từ người dùng (hoặc từ nút gợi ý)
query = None
if "pending_query" in st.session_state and st.session_state.pending_query:
    query = st.session_state.pending_query
    st.session_state.pending_query = None
else:
    query = st.chat_input("Nhập câu hỏi của bạn về Lễ hội Glastonbury 2025...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Đang truy xuất ngữ cảnh và tạo câu trả lời..."):
            result = generate_with_citation(query, top_k=top_k)
            answer = result["answer"]
            sources = result.get("sources", [])
            retrieval_source = result.get("retrieval_source", "hybrid")

            st.markdown(answer)

            if sources:
                with st.expander(f"📚 Nguồn trích dẫn ({len(sources)} tài liệu | Phương thức: {retrieval_source})"):
                    for idx, src in enumerate(sources, 1):
                        meta = src.get("metadata", {})
                        title = meta.get("title", "Tài liệu")
                        source = meta.get("source", "Nguồn")
                        score = src.get("score", 0.0)
                        method = src.get("retrieval_method", "hybrid")
                        url = meta.get("url")

                        st.markdown(f"**[Document {idx}] {title}** (`{source}`)")
                        st.caption(f"Score: `{score:.4f}` | Phương thức: `{method}` | Loại: `{meta.get('doc_type', 'N/A')}`")
                        if url:
                            st.markdown(f"🔗 [Xem bài viết gốc]({url})")
                        st.text(src.get("content", "")[:350] + ("..." if len(src.get("content", "")) > 350 else ""))
                        st.divider()

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
        "retrieval_source": retrieval_source,
    })
