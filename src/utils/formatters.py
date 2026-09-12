from datetime import datetime


def format_urgent_alert(news):
    """Format tin khẩn cấp để gửi ngay."""
    a = news.get("analysis", {})
    emoji = {"positive": "🟢", "negative": "🔴", "rumor": "⚠️", "neutral": "⚪"}
    senti = a.get("sentiment", "neutral")

    text = "🚨 <b>TIN ĐẶC BIỆT</b>\n\n"
    text += f"📌 <b>{news.get('title', '')}</b>\n"
    text += f"📰 Nguồn: {news.get('source', '')}\n"
    text += f"{emoji.get(senti, '⚪')} Sentiment: {senti}\n"

    if a.get("stock_codes"):
        text += f"📈 Mã: {', '.join(a['stock_codes'])}\n"
    if a.get("affected_sectors"):
        text += f"🏭 Ngành: {', '.join(a['affected_sectors'])}\n"

    text += f"\n📝 {a.get('summary', '')}\n"
    if news.get("url"):
        text += f"\n🔗 {news['url']}"
    return text


def format_daily_report(news_list, title="BÁO CÁO TIN TỨC"):
    """Format báo cáo tổng hợp."""
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    text = f"📊 <b>{title}</b>\n🕐 {now}\n\n"

    macro = [n for n in news_list if n.get("analysis", {}).get("news_type") == "macro"]
    stocks = [n for n in news_list if n.get("analysis", {}).get("news_type") == "stock_specific"]
    rumors = [n for n in news_list if n.get("analysis", {}).get("sentiment") == "rumor"]

    if macro:
        text += "🌍 <b>TIN VĨ MÔ</b>\n"
        for n in macro[:10]:
            text += f"• {n['title']}\n"
        text += "\n"

    if stocks:
        text += "📈 <b>TIN MÃ CỔ PHIẾU</b>\n"
        for n in stocks[:10]:
            a = n.get("analysis", {})
            codes = ", ".join(a.get("stock_codes", []))
            prefix = f"[{codes}] " if codes else ""
            text += f"• {prefix}{n['title']}\n"
        text += "\n"

    if rumors:
        text += "⚠️ <b>RUMOR / CẢNH BÁO</b>\n"
        for n in rumors[:5]:
            text += f"• {n['title']}\n"

    return text