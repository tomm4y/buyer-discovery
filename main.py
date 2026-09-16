import os
from dotenv import load_dotenv
from anthropic import Anthropic
from scraper import Scraper
from clean_reviews import clean_reviews
from discover import discover, filter_top_25
from embed_reviews import load_json, embed_texts, upsert_index

load_dotenv()

# import api keys
claude_key = os.getenv("ANTHROPIC_API_KEY")

# testing 
if __name__ == "__main__":
    
    zipcode = "75080"
    business_type = "lawyer"

    potential = discover(zipcode, business_type)
    top_businesses = filter_top_25(potential) # this is list dict

    scraper = Scraper(headless=True)
    all_reviews = []
    
    # for b in top_businesses:
    #     reviews = scraper.scrape_lowest_reviews(b['place_id'])
    #     for r in reviews:
    #         r["zipcode"] = zipcode
    #         r["business_type"] = business_type
    #     all_reviews.extend(reviews)

    # for b in top_businesses:
    #     reviews = scraper.scrape_lowest_reviews(b['place_id'])
    #     all_reviews.extend(reviews)
    
    # ChIJ04BEo86eToYRqwz0Zes0tuk long reviews
    # ChIJu-ibN-ggTIYRzjdBjsZXpZM short reviews
    
    reviews = scraper.scrape_lowest_reviews('ChIJ04BEo86eToYRqwz0Zes0tuk') # temp
    all_reviews.extend(reviews) # temp
    scraper.close()
    
    batch_name = f"{zipcode}_{business_type}".replace(" ", "_")
    
    saved_file_path = clean_reviews(reviews, "cleaned_data", batch_name, zipcode, business_type)
    print("Saved reviews to: " + saved_file_path)
    
    reviews_to_embed = load_json(saved_file_path)
    texts = [review['text'] for review in reviews]
    embedded = embed_texts(texts)
    upsert_index(reviews, embedded, zipcode, business_type)
    print("sucessfully upserted")