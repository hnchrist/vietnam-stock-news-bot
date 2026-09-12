import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime


RSS_FEEDS = [
    ("Vietstock", "https://vietstock.vn/144/chung-khoan.rss"),
    ("VnEconomy", "https://vneconomy.vn/chung-khoan.rss"),
    ("VnExpress", "https://vnexpress.net/rss/kinh-doanh.rss"),
    ("VietnamNet", "https://vietnamnet.vn/rss/kinh-doanh.rss"),
]

MAX_AGE_HOURS = 12


def is_recent(pub_date_str, max_age_hours=MAX_AGE_HOURS):
    """Kiểm tra tin có nằm trong khoảng thời gian cho phép không."""
    if not pub_date_str:
        return True
    try:
        pub_dt = parsedate_to_datetime(pub_date_str)
        if pub_dt.tzinfo is None:
            pub_dt = pub_dt.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return (now - pub_dt) <= timedelta(hours=max_age_hours)
    except Exception:
        return True


def fetch_rss(source_name, url, limit):
    """Lấy tin mới từ 1 RSS feed."""
    items = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            print(f"  ⚠️ {source_name}: HTTP {r.status_code}")
            return items

        root = ET.fromstring(r.content)
        for item in root.findall(".//item")[:limit * 3]:
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            desc = (item.findtext("description") or "").strip()
            pub = (item.findtext("pubDate") or "").strip()

            if not title or not is_recent(pub):
                continue

            items.append({
                "source": source_name,
                "title": title,
                "content": desc[:500],
                "url": link,
                "time": pub,
            })

            if len(items) >= limit:
                break

        print(f"  ✅ {source_name}: {len(items)} tin mới")
    except Exception as e:
        print(f"  ❌ {source_name} lỗi: {e}")
    return items


def scrape_fireant_news(limit=8):
    """Lấy tin thị trường từ nhiều nguồn RSS (tin trong 12h gần nhất)."""
    all_news = []
    for name, url in RSS_FEEDS:
        news = fetch_rss(name, url, limit)
        all_news.extend(news)

    # Sắp xếp tin mới nhất lên đầu
    all_news.sort(key=lambda x: x.get("time", ""), reverse=True)
    print(f"📰 Tổng RSS: {len(all_news)} tin (trong {MAX_AGE_HOURS}h gần nhất)")
    return all_news


if __name__ == "__main__":
    news = scrape_fireant_news()
    print(f"\n=== Kết quả ({len(news)} tin) ===")
    for n in news[:10]:
        print(f"- [{n['source']}] [{n['time']}]")
        print(f"  {n['title'][:90]}")