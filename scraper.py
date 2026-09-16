from playwright.sync_api import Page, sync_playwright
import json, os, re
from clean_reviews import clean_reviews

AUTH_STATE_PATH = "google_auth/auth_state.json"

class Scraper:
    def __init__(self, headless=True):
            self._playwright = sync_playwright().start()
            self.browser = self._playwright.chromium.launch(headless=headless, channel="chrome")

            context_kwargs = {
                "user_agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/128.0.0.0 Safari/537.36"
                )
            }
            if os.path.exists(AUTH_STATE_PATH):
                context_kwargs["storage_state"] = AUTH_STATE_PATH

            self.context = self.browser.new_context(**context_kwargs)
            self.page = self.context.new_page()

    def close(self):
        self.browser.close()
        self.context.close()
        self._playwright.stop()
        
    def save_reviews(self, reviews: list[dict], batch_name: str, output_dir: str) -> str:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{batch_name}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(reviews, f, indent=2, ensure_ascii=False)
        return output_path

    def scrape_lowest_reviews(
        self, place_id: str, min_text_len: int = 20
    ) -> list[dict]:

        # open url
        url = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
        self.page.goto(url)
        self.page.wait_for_timeout(1000)
        print("Went to url")

        # reload page to fix reviews tab not showing up sometimes
        self.page.reload()
        self.page.wait_for_timeout(400)

        # navigate to reviews section and click review tab
        reviews_tab = self.page.locator('button[role="tab"]:has-text("Reviews")').first
        reviews_tab.click()
        self.page.wait_for_timeout(500)

        # click the sort button 
        sort_button = self.page.get_by_role("button", name="Sort reviews")
        sort_button.click()
        self.page.wait_for_timeout(500)

        # select "Lowest rating" from the menu
        lowest_option = self.page.get_by_role("menuitemradio", name="Lowest rating")
        lowest_option.click()
        self.page.wait_for_timeout(2000)

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
            cards = self.page.locator("div.jftiEf")
            total_cards = cards.count()

            if processed_count >= total_cards:
                # caught up to everything loaded so far -> scroll for more
                self.page.evaluate(scroll_js)
                self.page.wait_for_timeout(2000)

                new_total = self.page.locator("div.jftiEf").count()
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
                    self.page.wait_for_timeout(200)
                    if text_el.count() == 0:
                        break
                    current_text = text_el.inner_text().strip()
                    if current_text != before_text:
                        break

            text_el = card.locator("span.wiI7pd").first
            review_text = text_el.inner_text().strip() if text_el.count() > 0 else ""

            status = "kept"
            if len(review_text) < min_text_len:
                status = "skip text too short"
            else:
                extracted_reviews.append({"place_id": place_id, "text": review_text})

            print(f"card {card_index}: rating = {rating}, chars={len(review_text)} -> {status}")

        print(f"Processed {processed_count} reviews, kept {len(extracted_reviews)}")
        return extracted_reviews

if __name__ == "__main__":
    # ChIJ04BEo86eToYRqwz0Zes0tuk long reviews
    # ChIJu-ibN-ggTIYRzjdBjsZXpZM short reviews
    place_ids = [
        "ChIJu-ibN-ggTIYRzjdBjsZXpZM"
    ]

    scraper = Scraper(headless=True)
    ### testing #####  ### testing #####  ### testing #####
    all_reviews = []
    for place_id in place_ids:
        reviews = scraper.scrape_lowest_reviews(place_id)
        all_reviews.extend(reviews)

    zipcode = "75080"
    business_type = "law firm"

    batch_name = f"{zipcode}_{business_type}".replace(" ", "_")
    
    saved = clean_reviews(reviews, "cleaned_data", batch_name)
    print("Saved reviews to: " + saved)
    ### testing #####  ### testing #####  ### testing #####

    scraper.close()