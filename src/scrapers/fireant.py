import requests
from datetime import datetime


def scrape_fireant_news(limit=20):
    """Scrape tin tức từ FireAnt."""
    news_list = []
    try:
        url = "https://fireant.vn/api/News/GetListNews"
        params = {"page": 1, "pageSize": limit}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "application/json",
        }
        r = requests.get(url, params=params, headers=headers, timeout=15)

        if r.status_code == 200:
            data = r.json()
            for item in data.get("data", [])[:limit]:
                news_list.append({
                    "source": "FireAnt",
                    "title": item.get("title", ""),
                    "content": item.get("shortDescription", "") or item.get("content", ""),
                    "url": item.get("url", ""),
                    "time": item.get("publishDate", datetime.now().isoformat()),
                })
    except Exception as e:
        print(f"⚠️ FireAnt lỗi: {e}")

    return news_list


if __name__ == "__main__":
    news = scrape_fireant_news()
    print(f"Lấy được {len(news)} tin từ FireAnt")
    for n in news[:3]:
        print(f"- {n['title']}")