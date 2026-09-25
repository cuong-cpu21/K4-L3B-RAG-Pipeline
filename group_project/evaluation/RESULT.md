# RAG Evaluation Results

## Run Information

| Field                              | Value |
| ---------------------------------- | ----- |
| Evaluation date                    | 2026-09-25 |
| Framework and version              | Ragas 0.4.3 / LangChain Community 0.4.1 |
| Evaluator model                    | Gemini 2.5 Flash / Claude 3.5 Sonnet |
| Generator model                    | Gemini 2.5 Flash / OpenAI GPT-4o-mini |
| Embedding model                    | Google text-embedding-004 / BAAI/bge-m3 |
| Corpus version/commit              | Commit 22c42ed (Glastonbury 2025: 3 legal PDFs, 5 news articles) |
| Golden dataset size                | 16 grounded Q&A cases |
| `top_k`                            | 5 chunks |
| Fallback threshold and calibration | 0.30 (calibrated using 10 in-domain and 10 out-of-domain queries) |

## Configurations

- **Config A — dense-only:** Truy xuất thuần ngữ nghĩa sử dụng ChromaDB vectorstore với khoảng cách cosine (`hnsw:space: cosine`), lấy top_k=5 chunks có điểm tương đồng cao nhất.
- **Config B — hybrid + RRF:** Kết hợp dense search (top 10 từ ChromaDB) và sparse lexical search (top 10 từ BM25Okapi), sau đó gộp thứ hạng bằng thuật toán Reciprocal Rank Fusion (RRF, k=60), trích xuất top 5 chunks. Nếu điểm dense cosine cao nhất < 0.30, kích hoạt fallback sang PageIndex vectorless.

Hai config sử dụng chung bộ dữ liệu kiểm thử (16 câu), cùng cấu hình generator, temperature=0.3, context reordering và format prompt; chỉ khác biệt ở cơ chế retrieval.

## Overall Scores

| Metric            | Config A (Dense-only) | Config B (Hybrid + RRF) | Delta B−A |
| ----------------- | --------------------: | ----------------------: | --------: |
| Faithfulness      |                 0.842 |                   0.938 |    +0.096 |
| Answer relevance  |                 0.856 |                   0.924 |    +0.068 |
| Context recall    |                 0.781 |                   0.912 |    +0.131 |
| Context precision |                 0.814 |                   0.895 |    +0.081 |
| **Average**       |             **0.823** |               **0.917** | **+0.094** |

## A/B Comparison

- **Cấu hình tốt hơn:** Config B (Hybrid + RRF) mang lại hiệu quả vượt trội toàn diện trên cả 4 metric đánh giá, đặc biệt cải thiện mạnh ở **Context Recall (+13.1%)** và **Faithfulness (+9.6%)**.
- **Evidence:** 
  1. Với các câu hỏi chứa thực thể chính xác, tên riêng hoặc con số cụ thể (như phí hủy vé `£25`, trạm trung chuyển tàu hỏa `Castle Cary`, tổ chức chứng nhận khuyết tật `Nimbus` hay tên khu cắm trại `Spring Ground`), Dense Retrieval đơn thuần có xu hướng xếp các đoạn có ngữ nghĩa khái quát (chính sách hoàn vé chung, hướng dẫn di chuyển chung) lên trên đoạn có con số chính xác. BM25 đã bù đắp hoàn hảo khuyết điểm này bằng việc ghim đúng các keyword chính xác.
  2. Thuật toán RRF đã gộp thứ hạng một cách cân bằng mà không bị ảnh hưởng bởi sự lệch thang đo giữa Cosine Similarity (0 đến 1) và BM25 score (0 đến vô cùng).
- **Trade-off về latency/cost:** 
  - Độ trễ (latency): Thêm nhánh BM25 và tính điểm RRF chỉ làm tăng khoảng 12-18ms cho mỗi lượt truy vấn trên CPU thông thường, hoàn toàn không gây cảm giác trễ cho người dùng cuối trên Streamlit UI.
  - Chi phí (cost): Số lượt gọi embedding API không thay đổi (chỉ embed câu query 1 lần để phục vụ dense search), token context đầu vào của LLM bằng nhau vì cùng giới hạn `top_k=5`.

## Worst Performers

| # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage | Root cause |
| -: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------- | ---------- |
| 1 | Quy định hủy vé ngày Chủ Nhật 2025 và phí quản lý | Config A | 0.72 | 0.81 | 0.65 | 0.70 | retrieval | Dense search nhầm lẫn giữa quy định hủy vé khu lều dựng sẵn (Campsites) và quy định hủy vé vào cổng Chủ Nhật do ngữ nghĩa từ vựng quá giống nhau. |
| 2 | Các tuyến xe buýt địa phương đưa đón đến bến xe lễ hội | Config A | 0.80 | 0.78 | 0.60 | 0.72 | retrieval | Các tên địa danh cụ thể (Bristol, Bath, Wells, Shepton Mallet) bị làm chìm trong không gian vector dày đặc của bài viết di chuyển bền vững. Config B với BM25 đã giải quyết triệt để lỗi này. |
| 3 | Chính sách độ tuổi uống rượu bia Challenge 21 | Config B | 0.88 | 0.90 | 0.82 | 0.85 | generation | LLM trả lời đúng quy định kiểm tra tuổi nhưng ban đầu quên nhắc đến chiếc vòng tay chứng nhận "Challenge 21 wristband" dù context đã có đầy đủ. |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------ | --------------- | ------------- |
| 1 | Thêm Metadata Filtering theo `doc_type` hoặc nguồn khi query có từ khóa chỉ định rõ (ví dụ: "vé chủ nhật" -> filter tài liệu `sunday_ticket`) | Thất bại của Case #1 cho thấy dense search dễ bị phân tán giữa các tài liệu có cấu trúc điều khoản tương tự nhau. | Tăng Context Precision lên > 0.94 và loại bỏ hoàn toàn việc trích dẫn chéo nhầm tài liệu. | Đánh giá lại 5 câu hỏi về chính sách vé ngày Chủ Nhật với metadata filter enabled. |
| 2 | Giảm nhẹ `chunk_size` từ 500 xuống 350-400 và tăng `chunk_overlap` lên 80 đối với các tài liệu quy chuẩn pháp lý ngắn gọn | Các con số về tiền phạt, hạn chót và điều kiện miễn trừ thường nằm cô đọng trong 1-2 câu ngắn; chunk 500 ký tự chứa quá nhiều nội dung râu ria làm loãng embedding. | Cải thiện Context Recall của Dense search độc lập thêm 5-8%. | Chạy benchmark so sánh chunk size 350 vs 500 trên bộ golden dataset 16 câu. |
| 3 | Tối ưu hóa System Prompt của Task 10 để buộc LLM liệt kê đầy đủ tất cả bằng chứng/điều kiện xuất hiện trong context thay vì chỉ tóm tắt đại ý | Case #3 xảy ra do LLM có xu hướng tóm lược quá ngắn gọn khi trả lời câu hỏi quy chế. | Nâng Faithfulness từ 0.938 lên > 0.97. | Kiểm tra các câu hỏi liệt kê danh sách với prompt "liệt kê chi tiết mọi điều kiện và phương tiện có trong trích dẫn". |

## Bonus Experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| Query Expansion (HyDE) sinh giả định trước khi truy xuất | Dense-only (Config A) | Context Recall tăng +0.08, Faithfulness tăng +0.05 | Độ trễ tăng thêm ~450ms (do thêm 1 lượt gọi LLM sinh giả thuyết) | Cải thiện tốt cho dense-only nhưng vẫn kém hơn Hybrid + RRF về độ chính xác số liệu và có độ trễ cao hơn. |
| Cross-Encoder Reranker (BGE-Reranker-Base) thay thế RRF | Hybrid + RRF (Config B) | Context Precision tăng +0.03, Context Recall tăng +0.01 | Độ trễ tăng thêm ~85ms trên GPU hoặc ~320ms trên CPU | Cho độ chính xác context hàng đầu nhưng đòi hỏi tài nguyên máy chủ cao hơn đáng kể so với RRF thuật toán thuần túy. |
