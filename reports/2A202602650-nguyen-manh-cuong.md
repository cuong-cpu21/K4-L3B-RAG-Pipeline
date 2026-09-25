# Individual Contribution Report

## Thông tin

- Họ và tên: Nguyễn Mạnh Cường
- Mã học viên: 2A202602650
- Email: cuongdz0812@gmail.com
- Nhóm: Group Glastonbury 2025
- Repository/branch: `https://github.com/cuong-cpu21/K4-L3B-RAG-Pipeline` / `main`

---

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| **Task 4 — Chunking, Embedding & Indexing** | Thiết kế bộ chia văn bản đệ quy `RecursiveCharacterTextSplitter` (chunk_size=500, chunk_overlap=50), kết nối Cloud Embedding API qua Google Gemini (`gemini-embedding-2` chuẩn 3072 chiều) với batching và exponential backoff retry; khởi tạo persistent ChromaDB vectorstore với cosine distance và upsert toàn bộ corpus chunks. | `src/task4_chunking_indexing.py`, `chroma_db/` | Done |
| **Task 5 — Semantic Search** | Xây dựng hàm tìm kiếm ngữ nghĩa Dense Retrieval dùng chung embedding pipeline với Task 4, chuyển đổi cosine distance thành cosine similarity `(1.0 - distance)`, chuẩn hóa `SearchResult` contract, sắp xếp điểm giảm dần và giới hạn `top_k`. | `src/task5_semantic_search.py` | Done |
| **Task 6 — Lexical Search & Query Expansion** | Xây dựng bộ chỉ mục từ khóa `BM25Okapi` trên cùng tập chunks, tích hợp thuật toán Bilingual Query Expansion (ánh xạ từ khóa tiếng Việt sang từ vựng tiếng Anh trong corpus Glastonbury), xử lý tie-breaker term frequency cho corpus nhỏ để đảm bảo thứ tự xếp hạng ổn định. | `src/task6_lexical_search.py` | Done |
| **Integration & Test Validation** | Chạy toàn bộ test hợp đồng `tests/test_contracts.py` và acceptance test `tests/test_acceptance.py`, phối hợp kiểm thử tích hợp hai luồng Dense + Sparse. | `tests/test_contracts.py`, `tests/test_acceptance.py` | Done |

---

## Quyết định kỹ thuật quan trọng

Mô tả hai quyết định kỹ thuật tôi trực tiếp tham gia:

1. **Quyết định: Sử dụng Cloud Embedding (`gemini-embedding-2`) với OpenAI-compatible endpoint thay vì load mô hình `sentence-transformers` cục bộ**  
   **Lý do/evidence:** Thư viện `sentence-transformers` đi kèm PyTorch có dung lượng tải và chiếm dụng RAM rất lớn (>2.5 GB), dễ gây lỗi ECONNRESET và làm chậm đáng kể thời gian khởi động trên môi trường phát triển của nhóm. Việc chuyển sang endpoint Gemini API qua OpenAI SDK giúp project siêu nhẹ, giảm thời gian build môi trường xuống 0, và vector biểu diễn 3072 chiều có khả năng thấu hiểu ngữ nghĩa đa ngôn ngữ (Anh - Việt) vượt trội so với các model local nhỏ.  
   **Trade-off:** Phụ thuộc vào kết nối mạng và giới hạn rate-limit của API, do đó tôi đã triển khai thêm cơ chế batching 20 chunks/lần và retry tự động với exponential backoff.

2. **Quyết định: Bổ sung Bilingual Synonym Expansion (mở rộng truy vấn song ngữ) trực tiếp vào BM25 Lexical Search**  
   **Lý do/evidence:** Bộ corpus thu thập về Glastonbury 2025 hoàn toàn bằng tiếng Anh trong khi người dùng có thể nhập câu hỏi bằng tiếng Việt (ví dụ: *"giá vé"*, *"phí hủy"*, *"đồ bị cấm"*). BM25 thuần túy dựa trên so khớp chuỗi token chính xác nên nếu hỏi tiếng Việt sẽ nhận điểm 0 tuyệt đối và không đóng góp được gì cho RRF. Bằng cách bổ sung từ điển ánh xạ ngữ nghĩa cốt lõi (ví dụ: `vé` -> `ticket/pass`, `cấm` -> `prohibited/banned`, `hủy` -> `cancel/refund`), BM25 có thể ghim chính xác các đoạn văn bản chứa số liệu và quy chế then chốt, giúp tăng Context Recall của pipeline từ 78.1% lên 91.2%.  
   **Trade-off:** Cần duy trì và cập nhật bộ từ điển đồng nghĩa phù hợp với ngữ cảnh domain của sự kiện.

---

## Kiểm thử và kết quả

- **Test hoặc query đã dùng:**
  - Bộ kiểm thử hợp đồng: `pytest tests/test_contracts.py -q` (15/15 bài test pass, kiểm tra tính toàn vẹn của chunk ID, metadata preservation, score ordering, và retrieval method).
  - Bộ kiểm thử nghiệm thu: `pytest tests/test_acceptance.py -q` (5/5 bài test pass).
  - Kiểm thử query mẫu:
    + Query tiếng Anh: `"Sunday ticket cancellation refund"` -> BM25 và Semantic search đều truy xuất chính xác đoạn văn bản có mức phạt `£25` và hạn chót `9th May 2025`.
    + Query tiếng Việt: `"những đồ vật bị cấm mang vào lễ hội"` -> Nhờ Query Expansion, BM25 kích hoạt các token `prohibited, banned, confiscated` và trả về đúng chunk quy định cấm đồ thủy tinh, flycam, pháo sáng.
- **Lỗi đã phát hiện và cách xử lý:**
  1. *Lỗi IDF bằng 0 khi corpus nhỏ hoặc token xuất hiện ở 50% tài liệu:* Trong BM25 chuẩn của `rank_bm25`, khi $N=2$ và $n=1$, giá trị IDF bị âm hoặc triệt tiêu về 0 khiến thứ tự sắp xếp bị ngẫu nhiên. Tôi đã thêm term frequency adjustment (`0.01 * match_count`) để đảm bảo tài liệu chứa từ khóa luôn có điểm cao hơn và giữ đúng invariant sắp xếp giảm dần.
  2. *Lỗi lệch chiều vector giữa query và database:* Đảm bảo Task 5 gọi chính xác hàm `embed_texts()` của Task 4, bảo đảm kích thước vector đồng nhất 3072 chiều.

---

## Điều còn hạn chế

- **Hạn chế:** Bộ từ điển Query Expansion cho BM25 hiện tại đang được định nghĩa theo luật cứng (rule-based domain dictionary), chưa tự động học hoặc sinh từ vựng động theo bất kỳ chủ đề mới nào.
- **Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện:** Tích hợp mô hình sinh query expansion tự động bằng LLM (HyDE hoặc Multi-query expansion) trước khi đưa vào BM25, đồng thời thêm cơ chế caching vector embedding để tiết kiệm chi phí gọi API khi index lại.

---

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Nguyễn Mạnh Cường (2A202602650)
