import json
from openai import OpenAI
from src.utils.config import config

client = OpenAI(
    api_key=config.DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "classify_news",
            "description": "Phân loại tin tức chứng khoán Việt Nam",
            "parameters": {
                "type": "object",
                "properties": {
                    "news_type": {
                        "type": "string",
                        "enum": ["macro", "stock_specific", "other"],
                        "description": "macro=tin vĩ mô, stock_specific=tin mã cổ phiếu"
                    },
                    "sentiment": {
                        "type": "string",
                        "enum": ["positive", "negative", "neutral", "rumor"]
                    },
                    "affected_sectors": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Ngành hưởng lợi hoặc bị thiệt hại"
                    },
                    "stock_codes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Mã cổ phiếu liên quan (VNM, VCB, ...)"
                    },
                    "is_urgent": {
                        "type": "boolean",
                        "description": "Tin đặc biệt cần báo ngay lập tức"
                    },
                    "summary": {
                        "type": "string",
                        "description": "Tóm tắt 2-3 câu"
                    }
                },
                "required": ["news_type", "sentiment", "is_urgent", "summary"]
            }
        }
    }
]

SYSTEM_PROMPT = """Bạn là chuyên gia phân tích chứng khoán Việt Nam.
Nhiệm vụ: Đọc tin tức và phân loại theo schema được cung cấp.

Hướng dẫn:
- Tin vĩ mô: lãi suất, thuế, giá dầu, urea, tỷ giá, chính sách...
- Tin mã cổ phiếu: tăng vốn, cổ tức, KQKD, pháp lý, rumor...
- Đánh dấu is_urgent=true nếu: tin cực xấu/tốt, ảnh hưởng diện rộng, rumor nóng
- Nếu không rõ, chọn "other" và sentiment="neutral"
"""


def analyze_news(news_item):
    """Phân tích 1 tin, trả về dict."""
    text = f"Tiêu đề: {news_item.get('title', '')}\nNội dung: {news_item.get('content', '')[:500]}"

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            tools=TOOLS,
            tool_choice={"type": "function", "function": {"name": "classify_news"}},
            temperature=0.3,
        )

        tool_call = response.choices[0].message.tool_calls[0]
        return json.loads(tool_call.function.arguments)
    except Exception as e:
        print(f"⚠️ DeepSeek lỗi: {e}")
        return {
            "news_type": "other", "sentiment": "neutral",
            "is_urgent": False, "summary": news_item.get("title", ""),
            "affected_sectors": [], "stock_codes": []
        }