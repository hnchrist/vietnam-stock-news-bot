from datetime import datetime
from src.scrapers import scrape_fireant_news, scrape_cafef_news, scrape_ssi_news
from src.analyzers import analyze_news
from src.notifiers import broadcast
from src.utils import format_urgent_alert, format_daily_report
from src.utils.config import config


def collect_all_news():
    """Thu thập tin từ tất cả nguồn."""
    all_news = []
    all_news.extend(scrape_fireant_news(limit=20))
    all_news.extend(scrape_cafef_news(limit=20))
    all_news.extend(scrape_ssi_news(limit=20))
    print(f"📥 Tổng cộng {len(all_news)} tin thô")
    return all_news


def main():
    now = datetime.now()
    print(f"🚀 Bot chạy lúc {now.strftime('%d/%m/%Y %H:%M')}")

    # 1. Thu thập
    raw_news = collect_all_news()
    if not raw_news:
        print("❌ Không có tin nào")
        return

    # 2. Phân tích bằng DeepSeek
    for n in raw_news:
        n["analysis"] = analyze_news(n)
    print(f"✅ Đã phân tích {len(raw_news)} tin")

    # 3. Tách tin khẩn cấp
    urgent = [n for n in raw_news if n["analysis"].get("is_urgent")]

    # 4. Báo ngay nếu có tin khẩn
    if urgent:
        print(f"🚨 {len(urgent)} tin khẩn cấp!")
        for n in urgent[:5]:
            broadcast(format_urgent_alert(n))

    # 5. Báo cáo tổng hợp vào 12h và 22h
    is_report_time = now.hour in config.REPORT_HOURS
    if is_report_time:
        report = format_daily_report(raw_news)
        broadcast(report)
        print("📤 Đã gửi báo cáo tổng hợp")


if __name__ == "__main__":
    main()