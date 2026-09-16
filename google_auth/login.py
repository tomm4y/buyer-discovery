from playwright.sync_api import sync_playwright

AUTH_STATE_PATH = "auth_state.json"

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],
        )
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://accounts.google.com")
        page.pause()

        context.storage_state(path=AUTH_STATE_PATH)
        print(f"Session saved to {AUTH_STATE_PATH}")

        context.close()
        browser.close()