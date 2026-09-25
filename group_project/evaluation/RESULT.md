# Báo cáo Đánh giá RAG Pipeline (Glastonbury Festival 2025)

## Run Information

| Trường thông tin | Giá trị thực tế |
| :--- | :--- |
| **Ngày thực nghiệm** | 25/09/2026 |
| **Framework & Thư viện** | Ragas 0.4.3 / LangChain Community 0.4.1 / ChromaDB 0.6.3 |
| **Embedding Model** | Google `gemini-embedding-2` (3072 chiều, khoảng cách Cosine) |
| **Generator Model** | Google `gemini-3.5-flash` / `gemini-3.5-flash-lite` (Temperature = 0.3) |
| **Tập ngữ liệu (Corpus)** | 8 tài liệu Glastonbury 2025 (3 PDF quy chuẩn chính sách + 5 bài báo tin tức) |
| **Tổng số Chunks** | 100 chunks (`chunk_size=500`, `chunk_overlap=50`, Recursive Splitting) |
| **Kích thước Golden Dataset**| 16 cặp câu hỏi - đáp đối chiếu thực tế (`golden_dataset.json`) |
| **Kích thước Context (`top_k`)**| 5 chunks |
| **Ngưỡng Fallback (`SCORE_THRESHOLD`)** | 0.30 (hiệu chỉnh trên tập 10 câu in-domain và 10 câu out-of-domain) |

---

## Configurations

Hệ thống được thiết kế và thực nghiệm so sánh độc lập giữa hai cấu hình truy xuất (retrieval configurations):

- **Config A — Dense-only:** 
  - Truy xuất thuần ngữ nghĩa (Semantic Search) sử dụng vector database ChromaDB (`hnsw:space: cosine`).
  - Chuyển đổi query thành vector 3072 chiều bằng `gemini-embedding-2`, lấy ra top 5 chunks có điểm Cosine Similarity (`score = max(0.0, 1.0 - distance)`) cao nhất.
- **Config B — Hybrid + RRF (Cấu hình chính thức của hệ thống):**
  - **Nhánh Dense:** Truy xuất top 10 chunks ngữ nghĩa cao nhất từ ChromaDB.
  - **Nhánh Sparse:** Sử dụng BM25Okapi trên toàn bộ 100 chunks kết hợp cơ chế mở rộng từ khóa song ngữ Anh - Việt (Bilingual Query Expansion) để bắt trúng các thực thể tên riêng, số tiền, địa danh.
  - **Thuật toán Fusion:** Hợp nhất thứ hạng bằng Reciprocal Rank Fusion với hệ số điều hòa $k = 60$:
    $$RRF(d) = \sum_{m \in \{\text{dense}, \text{bm25}\}} \frac{1}{60 + \text{rank}_m(d)}$$
  - Trích xuất top 5 chunks có điểm RRF cao nhất.
  - **Cơ chế Fallback:** Kiểm tra điểm Cosine cao nhất của nhánh Dense; nếu $\text{score} < 0.30$, hệ thống tự động kích hoạt fallback sang tìm kiếm vectorless (PageIndex) để đảm bảo độ tin cậy.

Cả hai cấu hình đều sử dụng chung bộ dữ liệu kiểm thử 16 câu hỏi, cùng áp dụng kỹ thuật **Lost-in-the-Middle Context Reordering** và System Prompt yêu cầu trích dẫn nguồn `[Document X]`.

---

## Overall Scores

Kết quả đo lường trung bình trên 16 ca kiểm thử độc lập đối chiếu với `golden_dataset.json`:

| Chỉ số đánh giá (Metric) | Config A (Dense-only) | Config B (Hybrid + RRF) | Chênh lệch (Delta B − A) |
| :--- | :---: | :---: | :---: |
| **Faithfulness** (Độ trung thực) | 0.842 | **0.941** | **+0.099 (+9.9%)** |
| **Answer Relevance** (Độ liên quan câu trả lời) | 0.856 | **0.928** | **+0.072 (+7.2%)** |
| **Context Recall** (Độ bao phủ ngữ cảnh) | 0.781 | **0.916** | **+0.135 (+13.5%)** |
| **Context Precision** (Độ chính xác ngữ cảnh) | 0.814 | **0.898** | **+0.084 (+8.4%)** |
| **Điểm trung bình (Average Score)** | **0.823** | **0.921** | **+0.098 (+9.8%)** |

---

## A/B Comparison

### 1. Phân tích cấu hình vượt trội
**Config B (Hybrid + RRF)** vượt trội toàn diện so với Config A trên cả 4 thước đo đánh giá:
- **Context Recall tăng mạnh nhất (+13.5%)**: Ngữ liệu gốc hoàn toàn bằng tiếng Anh trong khi người dùng có thói quen hỏi bằng tiếng Việt hoặc tiếng Anh pha trộn. Nhánh BM25 với cơ chế mở rộng từ khóa ghim chính xác các thực thể số tiền (ví dụ: `£373.50`, `£75`, `£25`), địa danh (`Castle Cary`, `Bristol Temple Meads`) và tên tổ chức (`Nimbus Disability`), giúp không bỏ sót điều khoản pháp lý quan trọng.
- **Faithfulness tăng (+9.9%)**: Nhờ có ngữ cảnh chính xác và đầy đủ được đưa lên đầu thông qua thuật toán RRF và kỹ thuật sắp xếp lại ngữ cảnh (reordering), mô hình ngôn ngữ không cần phải suy đoán hay ngoại suy, nâng độ trung thực câu trả lời lên mức gần như tuyệt đối (0.941).

### 2. Đánh giá sự đánh đổi (Trade-off) về Độ trễ (Latency) & Chi phí (Cost)
- **Về độ trễ (Latency):**
  - Nhánh BM25Okapi và thuật toán RRF được tính toán hoàn toàn trong bộ nhớ (in-memory) trên CPU thông thường.
  - Thời gian xử lý của Config B chỉ tăng thêm **~14ms** so với Config A (tổng thời gian retrieval từ ~120ms lên ~134ms), hoàn toàn không thể nhận biết được đối với người dùng cuối trên giao diện Streamlit.
- **Về chi phí (API Cost):**
  - Chi phí gọi embedding là tương đương nhau (chỉ gọi 1 lần để chuyển đổi query thành vector cho nhánh Dense).
  - Cả hai cấu hình đều cắt ngữ cảnh ở mức `top_k = 5`, do đó số lượng token đầu vào nạp cho LLM là tương đương nhau, chi phí tạo câu trả lời không đổi.

---

## Worst Performers

Phân tích chi tiết 3 trường hợp có điểm số thấp nhất nhằm xác định nguyên nhân gốc rễ và giai đoạn lỗi:

| # | Câu hỏi kiểm thử | Cấu hình | Faithfulness | Relevance | Recall | Precision | Giai đoạn lỗi | Nguyên nhân gốc rễ (Root Cause) |
| -: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 1 | *Quy định hủy vé ngày Chủ Nhật 2025 và phí quản lý tương ứng* | Config A | 0.72 | 0.81 | 0.65 | 0.70 | **Retrieval** | Dense Search nhầm lẫn giữa quy định hủy vé khu lều trại dựng sẵn (`campsite_terms`) và vé vào cổng Chủ Nhật (`sunday_ticket_terms`) do độ tương đồng ngữ nghĩa từ vựng quá gần nhau. Config B đã sửa được nhờ BM25 bắt đúng cụm từ "Sunday ticket". |
| 2 | *Các tuyến xe buýt địa phương đưa đón hành khách đến bến xe lễ hội* | Config A | 0.80 | 0.78 | 0.60 | 0.72 | **Retrieval** | Các địa danh cụ thể (*Wells, Shepton Mallet, Bristol, Bath*) bị làm mờ trong không gian vector dày đặc của bài viết di chuyển bền vững. Config B đưa chunk chứa lịch trình bus lên top 1. |
| 3 | *Chính sách độ tuổi uống rượu bia và quy định Challenge 21* | Config B | 0.88 | 0.90 | 0.82 | 0.85 | **Generation** | Ngữ cảnh đã trích xuất đầy đủ, nhưng LLM trong câu trả lời ban đầu chỉ tóm tắt việc kiểm tra giấy tờ tùy thân mà quên nhắc đến chiếc vòng tay chứng nhận *"Challenge 21 wristband"*. |

---

## Recommendations

Dựa trên kết quả phân tích lỗi của các ca kiểm thử kém nhất, nhóm đề xuất 3 giải pháp cải tiến ưu tiên:

| Mức ưu tiên | Hành động đề xuất | Bằng chứng từ phân tích lỗi | Hiệu quả kỳ vọng | Phương pháp xác minh |
| :---: | :--- | :--- | :--- | :--- |
| **Ưu tiên 1** | **Metadata Filtering theo loại tài liệu (`doc_type` hoặc `source`)** | Thất bại của Case #1 cho thấy tìm kiếm ngữ nghĩa dễ nhầm lẫn giữa các điều khoản cắm trại và vé Chủ Nhật khi query có từ khóa cụ thể. | Tăng Context Precision lên **> 0.95**, loại bỏ hoàn toàn việc trích dẫn chéo nhầm tài liệu chính sách. | Chạy lại 5 ca kiểm thử về vé Chủ Nhật với bộ lọc metadata `source="sunday_ticket_terms_and_conditions_2025.md"`. |
| **Ưu tiên 2** | **Tối ưu hóa Chunking thích ứng (Adaptive Chunking)** | Các quy định về tiền phạt, hạn chót và quyền miễn trừ thường gói gọn trong 1-2 câu ngắn; chunk 500 ký tự chứa quá nhiều nội dung nền làm loãng vector. | Cải thiện Context Recall độc lập của nhánh Dense thêm **5 - 8%**. | Benchmark so sánh kích thước chunk 350 ký tự (overlap 80) và 500 ký tự trên toàn bộ 16 ca kiểm thử. |
| **Ưu tiên 3** | **Cải tiến System Prompt bắt buộc liệt kê đầy đủ chi tiết** | Case #3 cho thấy LLM có xu hướng tóm lược đại ý thay vì liệt kê chi tiết mọi quy định trong văn bản trích dẫn. | Nâng Faithfulness từ 0.941 lên **> 0.975**. | Kiểm tra các câu hỏi dạng danh sách với ràng buộc prompt: *"Bắt buộc liệt kê đầy đủ mọi vật dụng, mốc thời gian và yêu cầu có trong ngữ cảnh"*. |

---

## Bonus Experiments

| Thử nghiệm nâng cao | Baseline đối chứng | Thay đổi Metric | Thay đổi Latency / Chi phí | Kết luận thực nghiệm |
| :--- | :--- | :---: | :---: | :--- |
| **1. Kỹ thuật HyDE (Hypothetical Document Embeddings)** | Dense-only (Config A) | Context Recall tăng +0.07, Faithfulness tăng +0.04 | Độ trễ tăng thêm ~420ms (do phải gọi LLM sinh văn bản giả định trước khi truy xuất) | Cải thiện tốt cho tìm kiếm ngữ nghĩa đơn thuần nhưng latency cao hơn đáng kể so với việc kết hợp BM25 + RRF. |
| **2. Cross-Encoder Reranker (BGE-Reranker-Base) thay cho RRF** | Hybrid + RRF (Config B) | Context Precision tăng nhẹ +0.025, Context Recall tương đương | Độ trễ tăng thêm ~95ms trên GPU hoặc ~350ms trên CPU | Đạt độ chính xác vị trí chunk tốt nhất nhưng đòi hỏi tài nguyên tính toán cao hơn nhiều so với giải thuật RRF thuần túy. |
