import requests
import xml.etree.ElementTree as ET
from datetime import datetime


RSS_FEEDS = [
    ("CafeF-ChungKhoan", "https://cafef.vn/tin-tuc-chung-khoan.rss"),
    ("CafeF-DoanhNghiep", "https://cafef.vn/doanh-nghiep.rss"),
    ("CafeF-ThiTruong", "https://cafef.vn/thi-truong-chung-khoan.rss"),
]


def fetch_rss(source_name, url, limit):
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
                    "source": "CafeF",
                    "title": title,
                    "content": desc[:500],
                    "url": link,
                    "time": pub or datetime.now().isoformat(),
                })
        print(f"  ✅ {source_name}: {len(items)} tin")
    except Exception as e:
        print(f"  ❌ {source_name} lỗi: {e}")
    return items


def scrape_cafef_news(limit=20):
    all_news = []
    for name, url in RSS_FEEDS:
        news = fetch_rss(name, url, limit)
        all_news.extend(news)

    print(f"📰 Tổng CafeF: {len(all_news)} tin")
    return all_news[:limit]


if __name__ == "__main__":
    news = scrape_cafef_news()
    print(f"\n=== Kết quả ===")
    for n in news[:5]:
        print(f"- {n['title'][:80]}")