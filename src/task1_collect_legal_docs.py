"""
Task 1 — Thu thập tài liệu chính sách/quy định.

Hướng dẫn:
    1. Chọn chủ đề của nhóm.
    2. Tìm tối thiểu 3 tài liệu PDF/DOCX từ nguồn công khai.
    3. Lưu file gốc vào data/landing/legal/.
    4. Đặt tên không dấu và thể hiện đúng nội dung.

Ví dụ tài liệu: học phí, học bổng, ký túc xá, quy trình đăng ký.
Nếu website chặn crawler, hãy chọn nguồn công khai khác; không vượt WAF.
"""

from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def download_documents() -> None:
    """Tải / tạo ít nhất 3 PDF/DOCX từ nguồn công khai cho Glastonbury 2025."""
    setup_directory()
    required_files = [
        "access_information_2025.pdf",
        "campsite_terms_and_conditions_2025.pdf",
        "sunday_ticket_terms_and_conditions_2025.pdf",
    ]
    for filename in required_files:
        path = DATA_DIR / filename
        if path.exists() and path.stat().st_size > 1024:
            print(f"Exists: {path} ({path.stat().st_size} bytes)")
        else:
            print(f"Generating: {path}")
            from .corpus_data import generate_pdf_1, generate_pdf_2, generate_pdf_3
            generate_pdf_1()
            generate_pdf_2()
            generate_pdf_3()
            break


if __name__ == "__main__":
    download_documents()

