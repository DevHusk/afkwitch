import os
import json
import time
import threading
from flask import Flask
from playwright.sync_api import sync_playwright

app = Flask(__name__)

AFK_URL = os.environ.get("AFK_URL", "https://dash.witchly.host/earn/afk")
COOKIES_JSON = os.environ.get("COOKIES_JSON", "[]")

def run_browser():
    while True:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-gpu",
                        "--single-process"
                    ]
                )
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
                )

                raw_cookies = json.loads(COOKIES_JSON)
                same_site_map = {"strict": "Strict", "lax": "Lax", "no_restriction": "None"}
                formatted_cookies = []
                for c in raw_cookies:
                    cookie = {
                        "name": c["name"],
                        "value": c["value"],
                        "domain": c["domain"],
                        "path": c.get("path", "/"),
                        "secure": c.get("secure", False),
                        "httpOnly": c.get("httpOnly", False),
                    }
                    ss = str(c.get("sameSite", "")).lower()
                    if ss in same_site_map:
                        cookie["sameSite"] = same_site_map[ss]
                    formatted_cookies.append(cookie)

                context.add_cookies(formatted_cookies)
                page = context.new_page()

                print(f"Opening {AFK_URL}...", flush=True)
                page.goto(AFK_URL, wait_until="domcontentloaded", timeout=60000)
                time.sleep(10)

                print("Current URL:", page.url, flush=True)
                print("Page Text:\n", page.inner_text("body")[:600], flush=True)

                while True:
                    time.sleep(60)
                    print("Still AFK | URL:", page.url, flush=True)

        except Exception as e:
            print("Error:", e, flush=True)
            time.sleep(15)

@app.route("/")
def home():
    return "AFK Browser Running"

if __name__ == "__main__":
    threading.Thread(target=run_browser, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
