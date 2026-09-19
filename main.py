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
    
    # initial search parameters
    zipcode = "75080"
    business_type = "lawyer"

    # step 1 discovering businesses + filtering
    potential = discover(zipcode, business_type)
    top_businesses = filter_top_25(potential) # this is list dict

    max_businesses = int(os.getenv("MAX_BUSINESSES", "0"))
    if max_businesses > 0:
        top_businesses = top_businesses[:max_businesses]

    # initialize scraper
    scraper = Scraper(headless=True)
    all_reviews = []
    
    # Print/list businesses found
    for business in top_businesses:
        print(
            business["name"],
            business["rating"],
            business["review_count"]
        )

    # Actually scrape reviews
    for business in top_businesses:
        reviews = scraper.scrape_lowest_reviews(business["place_id"])
        all_reviews.extend(reviews)
    
    # for testing only 1 business
    # ChIJ04BEo86eToYRqwz0Zes0tuk long reviews 
    # ChIJu-ibN-ggTIYRzjdBjsZXpZM short reviews
    # reviews = scraper.scrape_lowest_reviews('ChIJ04BEo86eToYRqwz0Zes0tuk') # temp
    # all_reviews.extend(reviews) # temp
    scraper.close()
    
    
    batch_name = f"{zipcode}_{business_type}".replace(" ", "_")
    
    # cleaning data clean_reviews.py
    saved_file_path = clean_reviews(
        all_reviews, "cleaned_data", batch_name, zipcode, business_type
    )
    print("Saved reviews to: " + saved_file_path)
    
    # embed_reviews.py loading data from cleaned_data and getting texts 
    reviews_to_embed = load_json(saved_file_path)
    texts = [review["text"] for review in reviews_to_embed]
    
    # using openai to embed texts and upserting into pinecone
    embedded = embed_texts(texts)
    upsert_index(reviews_to_embed, embedded, zipcode, business_type)
    print("Successfully upserted")