import os
from dotenv import load_dotenv
from anthropic import Anthropic
from scraper import Scraper
from clean_reviews import clean_reviews
from discover import discover, filter_top_25

load_dotenv()

# import api keys
claude_key = os.getenv("ANTHROPIC_API_KEY")
pinecone_key = os.getenv("PINECONE_API_KEY")

# testing 
if __name__ == "__main__":
    
    zipcode = "75080"
    business_type = "law firm"

    potential = discover(zipcode, business_type)
    top_businesses = filter_top_25(potential) # this is list dict

    scraper = Scraper(headless=True)
    all_reviews = []
    # for b in top_businesses:
    #     print(
    #         f"Name: {b['name']} | Rating: {b['rating']:.1f} | Reviews: {b['review_count']}"
    #     )
    #     print(f"https://www.google.com/maps/place/?q=place_id:{b['place_id']}")
    #     print("-" * 40)

    # for b in top_businesses:
    #     reviews = scraper.scrape_lowest_reviews(b['place_id'])
    #     all_reviews.extend(reviews)
    
    reviews = scraper.scrape_lowest_reviews('ChIJ04BEo86eToYRqwz0Zes0tuk') # temp
    all_reviews.extend(reviews) # temp
    scraper.close()
    
    batch_name = f"{zipcode}_{business_type}".replace(" ", "_")
    
    saved = scraper.save_reviews(all_reviews, batch_name, 'data')
    print("Saved reviews to: " + saved)
    
    output_file = clean_reviews(saved, "cleaned_data")
    print(f"Cleaned reviews saved to: {output_file}")