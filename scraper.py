from playwright.sync_api import Page, sync_playwright
import time
import re

def scrape_lowest_reviews(
	page: Page, place_id: str, min_text_len: int = 20
) -> list[dict]:

    # open url
    url = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
    page.goto(url)
    page.wait_for_timeout(500)

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
    print("Sorted lowest rating")
    page.wait_for_timeout(2000)

    extracted_reviews = []
    processed_count = 0
    stop_scraping = False

    while not stop_scraping:
        cards = page.locator("div.jftiEf")
        total_cards = cards.count()
        print(f"1st Total reviews found: {total_cards}")

        if processed_count >= total_cards:
            # scrolls inside the reviews tab using js script 
            page.evaluate("""
            const card = document.querySelector('div.jftiEf');
            if (card) {
                let parent = card.parentElement;
                while (parent) {
                    const overflow = window.getComputedStyle(parent).overflowY;
                    if (overflow === 'auto' || overflow === 'scroll') {
                        parent.scrollTop += 2500;
                        break;
                    }
                    parent = parent.parentElement;
                }
            }
            """)
        time.sleep(2)
        print(f"Total reviews found: {total_cards}")

        if page.locator("div.jftiEf").count() == total_cards:
            print("No new reviews loaded after scroll. Ending extraction.")
            break
        continue

    return extracted_reviews


if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        
        context = browser.new_context()
        page = context.new_page()

        # Test 
        print(scrape_lowest_reviews(page, "ChIJNW-EOx-ZToYR0Crz6bac4EI"))

        context.close()
        browser.close()