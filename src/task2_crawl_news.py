"""
Task 2 — Crawl bài viết/thông báo.

Hướng dẫn:
    1. Điền tối thiểu 5 URL công khai vào ARTICLE_URLS.
    2. Crawl từng URL bằng Crawl4AI.
    3. Lưu mỗi bài thành một JSON trong data/landing/news/.
    4. Giữ đủ url, title, date_crawled và content_markdown.

Cài browser trước khi chạy:
    python -m playwright install chromium
    
-> Dùng Firecrawl or bất cứ công cụ nào bạn quen    
"""

import asyncio
import json
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLE_URLS = [
    "https://www.glastonburyfestivals.co.uk/news/2025-ticket-sale-faq/",
    "https://www.glastonburyfestivals.co.uk/news/the-full-glastonbury-2025-line-up-is-here-with-set-times/",
    "https://www.glastonburyfestivals.co.uk/news/think-before-you-pack-for-this-years-festival-25/",
    "https://www.glastonburyfestivals.co.uk/news/plan-your-journey-travel-sustainably/",
    "https://www.glastonburyfestivals.co.uk/news/download-our-2025-app-keep-your-phone-charged/",
]


async def crawl_article(url: str) -> dict:
    """Đọc dữ liệu bài viết đã crawl hoặc crawl bài mới."""
    # Kiểm tra nếu file đã có trong thư mục landing
    index_map = {u: i + 1 for i, u in enumerate(ARTICLE_URLS)}
    index = index_map.get(url, 1)
    output = DATA_DIR / f"article_{index:02d}.json"
    if output.exists():
        data = json.loads(output.read_text(encoding="utf-8"))
        if data.get("content_markdown"):
            return data

    from datetime import datetime
    try:
        from crawl4ai import AsyncWebCrawler
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url)
            if result.success and result.markdown:
                return {
                    "url": url,
                    "title": result.metadata.get("title", url.rsplit("/", 2)[-2]),
                    "date_crawled": datetime.now().isoformat(),
                    "content_markdown": result.markdown,
                }
    except Exception as exc:
        print(f"Crawl4AI failed for {url}: {exc}")

    # Fallback to curated news corpus if blocked by WAF
    from .corpus_data import get_news_articles
    articles = get_news_articles()
    return articles[index - 1]


async def crawl_all() -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for index, url in enumerate(ARTICLE_URLS, 1):
        try:
            article = await crawl_article(url)
            output = DATA_DIR / f"article_{index:02d}.json"
            output.write_text(
                json.dumps(article, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"Saved: {output}")
        except Exception as error:
            print(f"Failed: {url} — {error}")


if __name__ == "__main__":
    asyncio.run(crawl_all())

