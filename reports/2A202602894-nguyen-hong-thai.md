# Individual contribution report

## Thông tin

- **Họ và tên:** Nguyễn Hồng Thái
- **Mã học viên:** 2A202602894
- **Nhóm:** sieunhandienquang (Lớp 3B)
- **Repository/branch:** `https://github.com/cuong-cpu21/K4-L3B-RAG-Pipeline` / `main`

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| **Golden Dataset** | Thiết kế 16 Q&A cases bao gồm: câu hỏi factual có số liệu cụ thể, câu hỏi policy/quy định, câu hỏi tổng hợp nhiều chunks, và 3 câu out-of-domain để kiểm tra fallback | `group_project/evaluation/golden_dataset.json` | Done |
| **Ragas Evaluation – Config A** | Chạy benchmark Dense-only (ChromaDB cosine, top_k=5) trên 16 cases, đo 4 metrics với Ragas 0.4.3 | `group_project/evaluation/RESULT.md` | Done |
| **Ragas Evaluation – Config B** | Chạy benchmark Hybrid+RRF trên cùng 16 cases; ghi nhận delta so với Config A | `group_project/evaluation/RESULT.md` | Done |
| **A/B Analysis & Worst-case** | Phân tích nguyên nhân gốc rễ 3 ca thất bại, xác định giai đoạn lỗi (Retrieval vs Generation), đề xuất 3 cải tiến ưu tiên | `group_project/evaluation/RESULT.md` | Done |
| **Bonus – HyDE thử nghiệm** | Thử nghiệm HyDE so với Dense-only; ghi nhận +0.07 Context Recall nhưng latency tăng ~420ms | `group_project/evaluation/RESULT.md` (Bonus Experiments) | Done |
| **Bonus – Cross-Encoder Reranker** | Thử nghiệm BGE-Reranker-Base thay RRF; Context Precision tăng +0.025, latency tăng ~350ms trên CPU | `group_project/evaluation/RESULT.md` (Bonus Experiments) | Done |
| **TEAMMATES.md** | Cập nhật thông tin thành viên 3 | `TEAMMATES.md` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Thiết kế golden dataset với câu hỏi bao phủ nhiều dạng thay vì chỉ câu factual đơn giản.  
   **Lý do/evidence:** Corpus Glastonbury 2025 có cả chính sách pháp lý (terms & conditions) và tin tức, nên cần câu hỏi vừa kiểm tra entity matching (giá tiền, địa danh) vừa kiểm tra cross-document synthesis.  
   **Trade-off:** Một số câu tổng hợp phức tạp có score thấp hơn và khó đánh giá tự động với Ragas — cần kiểm tra thủ công thêm.

2. **Quyết định:** Chọn `SCORE_THRESHOLD = 0.30` cho fallback sau khi hiệu chỉnh trên 10 câu in-domain và 10 câu out-of-domain.  
   **Lý do/evidence:** Threshold thấp hơn (0.25) gây false negative — câu hỏi in-domain bị fallback nhầm. Threshold cao hơn (0.40) khiến câu out-of-domain không được fallback, LLM hallucinate.  
   **Trade-off:** 0.30 là điểm cân bằng nhưng vẫn có 1 ca biên (câu hỏi về bus route) bị thiếu ngữ cảnh do chunk nhỏ bị loãng trong vector space.

## Kiểm thử và kết quả

- **Test in-domain:** 13/16 câu → Hybrid+RRF trả về đúng chunk trong top-3; Config A chỉ đạt 10/13 do bị nhầm tài liệu chính sách.
- **Test out-of-domain:** 3 câu không liên quan Glastonbury → fallback kích hoạt đúng cả 3 lần với threshold 0.30.
- **Kết quả A/B:** Config B (Hybrid+RRF) vượt Config A trên cả 4 metrics; Context Recall cải thiện nhiều nhất (+13.5%) nhờ BM25 ghim đúng số tiền và địa danh tiếng Anh khi user hỏi bằng tiếng Việt.
- **Lỗi phát hiện:** Case #3 (chính sách Challenge 21) — LLM tóm tắt đại ý, bỏ sót chi tiết "Challenge 21 wristband". Giai đoạn lỗi là Generation, không phải Retrieval.

## Điều còn hạn chế

- **Hạn chế:** 16 cases là số tối thiểu; một số câu hỏi về giá vé và địa danh trùng ngữ nghĩa nhau, làm kết quả Context Precision trên Config A có thể bị inflate nhẹ.
- **Nếu có thêm thời gian:** Thêm Metadata Filtering theo `source` vào retrieval pipeline (đề xuất Ưu tiên 1 trong RESULT.md) và chạy lại 5 ca về vé Chủ Nhật để xác nhận Context Precision tăng lên > 0.95.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- **Ngày:** 25/09/2026
- **Tên thành viên:** Nguyễn Hồng Thái
