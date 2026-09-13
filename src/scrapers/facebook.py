import os
import base64
import hashlib
import tempfile
from datetime import datetime
from camoufox.sync_api import Camoufox

MAX_POSTS_PER_GROUP = 15
MAX_SCROLLS = 10
PAGE_TIMEOUT = 90000


def decode_session_from_env():
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
            page.set_default_timeout(PAGE_TIMEOUT)

            for group_url in group_urls:
                print(f"🔍 Quét nhóm: {group_url}")
                try:
                    page.goto(group_url, timeout=PAGE_TIMEOUT, wait_until="domcontentloaded")
                    page.wait_for_timeout(5000)

                    posts = []
                    seen = set()
                    scrolls = 0

                    while len(posts) < limit and scrolls < MAX_SCROLLS:
                        scrolls += 1
                        try:
                            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        except Exception:
                            pass
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

                        try:
                            elements = page.locator(
                                "div[data-ad-rendering-role='story_message']"
                            )
                            count = elements.count()
                        except Exception:
                            count = 0

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
                        content_hash = hashlib.md5(text.encode("utf-8")).hexdigest()[:12]
                        group_id = group_url.rstrip("/").split("/")[-1]
                        unique_url = f"fb://{group_id}/{content_hash}"

                        all_posts.append({
                            "source": "Facebook",
                            "title": text[:100].replace("\n", " "),
                            "content": text[:1500],
                            "url": unique_url,
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
