import json
import os
from datetime import datetime
from src.scrapers import scrape_fireant_news, scrape_cafef_news, scrape_ssi_news
from src.analyzers import analyze_news
from src.notifiers import broadcast
from src.utils import format_urgent_alert, format_daily_report
from src.utils.config import config

STATE_FILE = "sent_news.json"


def load_sent():
    """Đọc danh sách URL tin đã gửi."""
    if not os.path.exists(STATE_FILE):
        return set()
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data.get("sent_urls", []))
    except Exception as e:
        print(f"⚠️ Không đọc được state: {e}")
        return set()


def save_sent(sent_urls):
    """Lưu danh sách URL đã gửi (giữ 500 cái gần nhất)."""
    urls = list(sent_urls)[-500:]
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "sent_urls": urls,
            "updated": datetime.now().isoformat(),
        }, f, ensure_ascii=False)


def collect_all_news():
    """Thu thập tin từ tất cả nguồn."""
    all_news = []
    all_news.extend(scrape_fireant_news(limit=8))
    all_news.extend(scrape_cafef_news(limit=8))
    all_news.extend(scrape_ssi_news(limit=8))
    print(f"📥 Tổng cộng {len(all_news)} tin thô")
    return all_news


def main():
    now = datetime.now()
    print(f"🚀 Bot chạy lúc {now.strftime('%d/%m/%Y %H:%M')}")

    # 1. Thu thập tin
    raw_news = collect_all_news()
    if not raw_news:
        print("❌ Không có tin nào")
        return

    # 2. Lọc bỏ tin đã gửi trước đó
    sent_urls = load_sent()
    new_news = [n for n in raw_news if n.get("url") and n["url"] not in sent_urls]
    skipped = len(raw_news) - len(new_news)
    print(f"🆕 {len(new_news)} tin mới (bỏ qua {skipped} tin đã gửi)")

    if not new_news:
        print("✅ Không có tin mới, kết thúc")
        return

    # 3. Phân tích bằng DeepSeek
    analyzed = []
    for n in new_news:
        n["analysis"] = analyze_news(n)
        analyzed.append(n)
    print(f"✅ Đã phân tích {len(analyzed)} tin")

    # 4. Tách tin khẩn cấp
    urgent = [n for n in analyzed if n["analysis"].get("is_urgent")]

    # 5. Báo ngay nếu có tin khẩn
    if urgent:
        print(f"🚨 {len(urgent)} tin khẩn cấp!")
        for n in urgent[:5]:
            try:
                broadcast(format_urgent_alert(n))
            except Exception as e:
                print(f"⚠️ Lỗi gửi tin khẩn: {e}")

    # 6. Báo cáo tổng hợp vào 12h và 22h (giờ VN)
    is_report_time = now.hour in config.REPORT_HOURS
    if is_report_time:
        try:
            report = format_daily_report(analyzed)
            broadcast(report)
            print("📤 Đã gửi báo cáo tổng hợp")
        except Exception as e:
            print(f"⚠️ Lỗi gửi báo cáo: {e}")
    else:
        print(f"⏰ Chưa tới giờ báo cáo (giờ hiện tại: {now.hour}h)")

    # 7. Lưu state — chỉ lưu URL đã phân tích (để không gửi lại)
    sent_urls.update(n["url"] for n in analyzed if n.get("url"))
    save_sent(sent_urls)
    print(f"💾 Đã lưu state ({len(sent_urls)} URL)")


if __name__ == "__main__":
    main()