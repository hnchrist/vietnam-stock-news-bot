import requests
from bs4 import BeautifulSoup
from datetime import datetime


def scrape_cafef_news(limit=20):
    """Scrape tin tức từ CafeF."""
    news_list = []
    try:
        url = "https://cafef.vn/tin-tuc-chung-khoan.chn"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        }
        r = requests.get(url, headers=headers, timeout=15)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "lxml")

        articles = soup.select("li.item, div.item-news")[:limit]
        for art in articles:
            title_el = art.select_one("h3 a, h2 a, a.title")
            if not title_el:
                continue
            news_list.append({
                "source": "CafeF",
                "title": title_el.get_text(strip=True),
                "content": title_el.get("title", "") or "",
                "url": title_el.get("href", ""),
                "time": datetime.now().isoformat(),
            })
    except Exception as e:
        print(f"⚠️ CafeF lỗi: {e}")

    return news_list