import requests
import xml.etree.ElementTree as ET
from datetime import datetime


RSS_FEEDS = [
    ("Vietstock", "https://vietstock.vn/144/chung-khoan.rss"),
    ("VnEconomy", "https://vneconomy.vn/chung-khoan.rss"),
    ("VnExpress", "https://vnexpress.net/rss/kinh-doanh.rss"),
    ("VietnamNet", "https://vietnamnet.vn/rss/kinh-doanh.rss"),
]


def fetch_rss(source_name, url, limit):
    """Lấy tin từ 1 RSS feed, trả về list."""
    items = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            print(f"  ⚠️ {source_name}: HTTP {r.status_code}")
            return items

        root = ET.fromstring(r.content)
        for item in root.findall(".//item")[:limit]:
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            desc = (item.findtext("description") or "").strip()
            pub = (item.findtext("pubDate") or "").strip()

            if title:
                items.append({
                    "source": source_name,
                    "title": title,
                    "content": desc[:500],
                    "url": link,
                    "time": pub or datetime.now().isoformat(),
                })
        print(f"  ✅ {source_name}: {len(items)} tin")
    except Exception as e:
        print(f"  ❌ {source_name} lỗi: {e}")
    return items


def scrape_fireant_news(limit=20):
    """Lấy tin thị trường từ nhiều nguồn RSS."""
    all_news = []
    for name, url in RSS_FEEDS:
        news = fetch_rss(name, url, limit)
        all_news.extend(news)

    print(f"📰 Tổng RSS: {len(all_news)} tin")
    return all_news[:limit * 2]


if __name__ == "__main__":
    news = scrape_fireant_news()
    print(f"\n=== Kết quả ===")
    for n in news[:5]:
        print(f"- [{n['source']}] {n['title'][:80]}")