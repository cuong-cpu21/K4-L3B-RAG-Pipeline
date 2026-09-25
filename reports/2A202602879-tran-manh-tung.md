# Individual Contribution Report

## Thông tin

- Họ và tên: Trần Mạnh Tùng
- Mã học viên: 2A202602879
- Nhóm: Group Glastonbury 2025
- Repository/branch: `https://github.com/cuong-cpu21/K4-L3B-RAG-Pipeline` / `main`

---

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 1 — Thu thập Legal Docs | Thu thập và chuẩn hóa 3 tài liệu quy chế chính sách Glastonbury 2025 (tiếp cận, điều khoản cắm trại, vé Chủ Nhật). | `src/task1_collect_legal_docs.py`, `src/corpus_data.py`, `data/landing/legal/` | Done |
| Task 2 — Crawl News | Xây dựng pipeline crawl 5 bài viết chính thức về vé, lịch diễn, chuẩn bị đồ đạc, di chuyển xanh và app mobile. | `src/task2_crawl_news.py`, `data/landing/news/` | Done |
| Task 3 — Chuẩn hóa Markdown | Triển khai bộ chuyển đổi dữ liệu sang định dạng Markdown chuẩn hóa với đầy đủ metadata header. | `src/task3_convert_markdown.py`, `data/standardized/` | Done |
| Task 4 — Chunking & Indexing | Xây dựng bộ chia văn bản đệ quy, kết nối Google Gemini Embedding (`gemini-embedding-001`) và index vào ChromaDB. | `src/task4_chunking_indexing.py` | Done |
| Task 5, 6, 7 — Hybrid Search & RRF | Cài đặt Dense search (ChromaDB cosine), Lexical search (BM25Okapi) và thuật toán hợp nhất thứ hạng Reciprocal Rank Fusion. | `src/task5_semantic_search.py`, `src/task6_lexical_search.py`, `src/task7_reranking.py` | Done |
| Task 8, 9, 10 — Pipeline & Generation | Hoàn thiện luồng kiểm tra cosine threshold để fallback an toàn; lost-in-the-middle context reordering; generation có trích dẫn nguồn kiểm chứng được. | `src/task8_pageindex_vectorless.py`, `src/task9_retrieval_pipeline.py`, `src/task10_generation.py` | Done |
| Evaluation & Reporting | Xây dựng bộ golden dataset 16 câu hỏi Q&A chuẩn xác, đánh giá A/B Testing và hoàn thiện báo cáo RESULT.md. | `group_project/evaluation/golden_dataset.json`, `group_project/evaluation/RESULT.md` | Done |
| Chatbot UI | Tích hợp toàn bộ pipeline lên giao diện Streamlit với thanh điều khiển top_k, câu hỏi gợi ý và expander trích dẫn nguồn. | `app.py` | Done |

---

## Quyết định kỹ thuật quan trọng

1. **Quyết định: Sử dụng Cloud Embedding (Gemini text-embedding-001) thay cho Sentence-Transformers cục bộ**  
   **Lý do/evidence:** Thư viện PyTorch và mô hình bge-m3 cục bộ dung lượng rất lớn (>1.5GB), tải chậm và dễ gặp xung đột tài nguyên trên môi trường Windows CPU. Việc chuyển sang Gemini API giúp môi trường siêu nhẹ, indexing 100 chunks chỉ mất dưới 1 phút.  
   **Trade-off:** Phụ thuộc vào kết nối mạng và API key của Google Cloud, nhưng được bù đắp bằng tốc độ và chất lượng biểu diễn ngữ nghĩa đa ngôn ngữ xuất sắc.

2. **Quyết định: Áp dụng cơ chế RRF (Reciprocal Rank Fusion, k=60) kết hợp Bilingual Query Expansion cho BM25**  
   **Lý do/evidence:** Tài liệu gốc hoàn toàn bằng tiếng Anh trong khi người dùng có thể đặt câu hỏi bằng tiếng Việt. BM25 thuần túy không thể so khớp từ khóa tiếng Việt. Việc bổ sung keyword mapping song ngữ giúp BM25 ghim chính xác các thực thể số tiền, tên riêng và quy định cấm, nâng Context Recall từ 78.1% lên 91.2%.  
   **Trade-off:** Cần duy trì một bộ từ điển ánh xạ từ khóa cốt lõi giữa hai ngôn ngữ.

---

## Kiểm thử và kết quả

- **Test đã dùng:** Toàn bộ test suite gồm `pytest tests/test_contracts.py` (15 bài test hợp đồng) và `pytest tests/test_acceptance.py` (5 bài test nghiệm thu).
- **Kết quả:** Đạt **20/20 passed (100%)** với thời gian chạy ~1.3s.
- **Lỗi đã phát hiện và cách xử lý:**
  1. *Lỗi BM25 tie-break khi test corpus nhỏ (N=2, df=1 -> IDF=0):* Đã bổ sung term frequency tie-breaker để ưu tiên tài liệu chứa từ khóa truy vấn.
  2. *Lỗi thiếu file và JSON rỗng trong acceptance test:* Đã sinh đầy đủ 16 cặp Q&A thực tế vào `golden_dataset.json` và hoàn thiện toàn bộ báo cáo `RESULT.md`.

---

## Điều còn hạn chế

- **Hạn chế:** Hệ thống hiện tại ưu tiên tìm kiếm đơn lượt (single-turn Q&A), chưa tích hợp memory hội thoại để theo dõi các câu hỏi nối tiếp (follow-up questions).
- **Hướng cải tiến nếu có thêm thời gian:** Tích hợp bộ nhớ hội thoại trượt (Sliding Window Conversation Memory) và Cross-Encoder Reranker (như BGE-Reranker) để tinh chỉnh độ chính xác của top 3 chunks cuối cùng.

---

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Trần Mạnh Tùng
