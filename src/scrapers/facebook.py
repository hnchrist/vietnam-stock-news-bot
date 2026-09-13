import os
import base64
import tempfile
from datetime import datetime
from camoufox.sync_api import Camoufox

MAX_POSTS_PER_GROUP = 15
MAX_SCROLLS = 10


def decode_session_from_env():
    """Giải mã session Facebook từ biến môi trường FB_STORAGE_STATE_B64."""
    b64_state = os.environ.get("FB_STORAGE_STATE_B64")
    if not b64_state:
        return None
    try:
        state_json = base64.b64decode(b64_state).decode("utf-8")
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        )
        tmp.write(state_json)
        tmp.close()
        return tmp.name
    except Exception as e:
        print(f"❌ Lỗi giải mã session: {e}")
        return None


def scrape_facebook_groups(group_urls, limit=MAX_POSTS_PER_GROUP):
    """Scrape bài viết từ các nhóm Facebook dùng Camoufox + session đã lưu."""
    if not group_urls:
        print("ℹ️ Facebook: chưa cấu hình nhóm nào")
        return []

    state_path = decode_session_from_env()
    if not state_path:
        print("⚠️ Facebook: chưa có FB_STORAGE_STATE_B64, bỏ qua")
        return []

    all_posts = []

    try:
        with Camoufox(
            headless=True,
            humanize=True,
            os=["windows"],
            locale="vi-VN",
        ) as browser:
            context = browser.new_context(storage_state=state_path)
            page = context.new_page()
            for group_url in group_urls:
                print(f"🔍 Quét nhóm: {group_url}")
                try:
                    page.goto(group_url, timeout=60000)
                    page.wait_for_timeout(5000)

                    posts = []
                    seen = set()
                    scrolls = 0

                    while len(posts) < limit and scrolls < MAX_SCROLLS:
                        scrolls += 1
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        page.wait_for_timeout(2500)

                        try:
                            more = page.locator("text='Xem thêm'")
                            for i in range(min(more.count(), 5)):
                                try:
                                    more.nth(i).click(timeout=500)
                                except Exception:
                                    pass
                        except Exception:
                            pass

                        elements = page.locator(
                            "div[data-ad-rendering-role='story_message']"
                        )
                        count = elements.count()
                        for i in range(count):
                            try:
                                text = elements.nth(i).inner_text().strip()
                                if text and text not in seen and len(text) > 30:
                                    posts.append(text)
                                    seen.add(text)
                                    if len(posts) >= limit:
                                        break
                            except Exception:
                                continue

                    print(f"  ✅ Lấy được {len(posts)} bài")

                    for text in posts:
                        all_posts.append({
                            "source": "Facebook",
                            "title": text[:100].replace("\n", " "),
                            "content": text[:1500],
                            "url": group_url,
                            "time": datetime.now().isoformat(),
                        })
                except Exception as e:
                    print(f"  ❌ Lỗi nhóm {group_url}: {e}")

        try:
            os.unlink(state_path)
        except Exception:
            pass

    except Exception as e:
        print(f"❌ Camoufox lỗi: {e}")

    print(f"📘 Facebook: tổng {len(all_posts)} bài viết")
    return all_posts


if __name__ == "__main__":
    test_groups = ["https://www.facebook.com/groups/your_group_id"]
    results = scrape_facebook_groups(test_groups)
    for r in results[:3]:
        print(f"- {r['title']}")