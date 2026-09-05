from playwright.sync_api import Page, sync_playwright
import json
import os
import re

def scrape_lowest_reviews(
	page: Page, place_id: str, min_text_len: int = 20
) -> list[str]:

    # open url
    url = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
    page.goto(url)
    page.wait_for_timeout(1000)
    print("Went to url")

    # reload page to fix reviews tab not showing up sometimes
    page.reload()
    page.wait_for_timeout(400)

    # navigate to reviews section and click review tab
    reviews_tab = page.locator('button[role="tab"]:has-text("Reviews")').first
    reviews_tab.click()
    page.wait_for_timeout(500)

    # click the sort button 
    sort_button = page.get_by_role("button", name="Sort reviews")
    sort_button.click()
    page.wait_for_timeout(500)

    # select "Lowest rating" from the menu
    lowest_option = page.get_by_role("menuitemradio", name="Lowest rating")
    lowest_option.click()
    page.wait_for_timeout(2000)

    extracted_reviews = []
    processed_count = 0
    stop_scraping = False
    
    scroll_js = """
        const card = document.querySelector('div.jftiEf');
        if (card) {
            let parent = card.parentElement;
            while (parent) {
                const overflow = window.getComputedStyle(parent).overflowY;
                if (overflow === 'auto' || overflow === 'scroll') {
                    parent.scrollTop = parent.scrollHeight;
                    break;
                }
                parent = parent.parentElement;
            }
        }
    """

    while not stop_scraping:
        cards = page.locator("div.jftiEf")
        total_cards = cards.count()

        if processed_count >= total_cards:
            # caught up to everything loaded so far -> scroll for more
            page.evaluate(scroll_js)
            page.wait_for_timeout(2000)

            new_total = page.locator("div.jftiEf").count()
            if new_total == total_cards:
                break
            continue

        card = cards.nth(processed_count)
        card_index = processed_count
        processed_count += 1

        rating_el = card.locator("span.kvMYJc[aria-label*='star']").first
        aria_label = rating_el.get_attribute("aria-label") or ""
        match = re.search(r"(\d+)\s*star", aria_label)
        
        if not match:
            print(f"card {card_index}: could not parse rating from '{aria_label}', skipping")
            continue
        rating = int(match.group(1))

        if rating >= 4:
            print(f"card {card_index}: rating = {rating}, stopping (sorted by lowest rating)")
            stop_scraping = True
            break

        # expand truncated text if a more button is present
        more_button = card.locator('button.w8nwRe[aria-label="See more"]')
        if more_button.count() > 0:
            text_el = card.locator("span.wiI7pd").first
            before_text = text_el.inner_text().strip() if text_el.count() > 0 else ""
            more_button.first.click()
            # poll from the Python side until the text actually changes,
            # rather than reading it immediately (avoids the expand race
            # condition) or passing a fragile ElementHandle into JS
            for _ in range(15):
                page.wait_for_timeout(200)
                if text_el.count() == 0:
                    break
                current_text = text_el.inner_text().strip()
                if current_text != before_text:
                    break

        text_el = card.locator("span.wiI7pd").first
        review_text = text_el.inner_text().strip() if text_el.count() > 0 else ""

        status = "kept"
        if len(review_text) < min_text_len:
            status = "skipped (text too short)"
        else:
            extracted_reviews.append(review_text)

        print(f"card {card_index}: rating = {rating}, chars={len(review_text)} -> {status}")

    print(f"Processed {processed_count} reviews, kept {len(extracted_reviews)}")
    return extracted_reviews


if __name__ == "__main__":

    place_ids = [
    "ChIJNW-EOx-ZToYR0Crz6bac4EI",
    "ChIJQfLUSgufToYRZIAt4sapAuk",
    "ChIJZ9phbj-fToYR4gwCSmlISg4",
    "ChIJuzINMREeTIYR5_8rdpjsVwo",
    "ChIJ0zzq1_EfTIYRgryTKWGtL-8",
    "ChIJOddkDJKgToYRqiDzJgy3Z14",
    "ChIJHWblb2m35BQRur_FGD_A11I",
    "ChIJQzSYfXEfTIYR76i9d10T4Og",
    "ChIJtRnoJjkgTIYRSkJDlySZ4ug",
    "ChIJg74i3fEgTIYRKYgyZLz5iR4",
    "ChIJrYB12XkhTIYRMUJy3EG6tTE",
    "ChIJHSChQPIfTIYRNL4kbudryNE",
    "ChIJBzby7hGZToYR57ZYzpGAVLM",
    "ChIJXwcSL9snTIYR47qppd4Rb2E",
    "ChIJu-ibN-ggTIYRzjdBjsZXpZM",
    ]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="chrome")

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/128.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        # Test 
        print(scrape_lowest_reviews(page, place_ids[14]))

        context.close()
        browser.close()