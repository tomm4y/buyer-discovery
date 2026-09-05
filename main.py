import os
import math
import googlemaps
from anthropic import Anthropic
import requests
from dotenv import load_dotenv
import json
import time

load_dotenv()

# import api keys
maps_key = os.getenv("GOOGLE_API_KEY")
claude_key = os.getenv("ANTHROPIC_API_KEY")
hunter_key = os.getenv("HUNTER_API_KEY")

gmaps = googlemaps.Client(key=maps_key)

# weighted scoring model using logarithmic review scaling to dynamically rank and extract the top 25% highest-quality business leads.
# returns list of dictionary of top 25% of businesses 
def filter_top_25(businesses: list[dict]) -> list[dict]:

    def scoring(biz: dict):
        rating = biz.get('rating', 0)
        reviews = biz.get('review_count', 0)

        review_weight = math.log10(reviews + 1)

        if rating >= 3.5:
            return rating * (1 + review_weight)
        else:
            return rating / (1 + review_weight)
         
    sorted_businesses = sorted(businesses, key=scoring, reverse=True)

    cutoff_count = math.ceil(len(sorted_businesses) * 0.25)
    return sorted_businesses[:cutoff_count]


def discover(zipcode: str, business_type: str) -> list[dict]:
    # using geocode to translate zip code to lat and lng
    geocode_result = gmaps.geocode(zipcode)
    lat_lng = geocode_result[0]["geometry"]["location"]
    # Returns: {'lat': some number, 'lng': some number}

    results = gmaps.places_nearby(
        location=lat_lng,
        radius=10000, 
        keyword=business_type
    )

    businesses = []
    # Only keep operational businesses
    while True:
        for place in results.get("results", []):
            status = place.get("business_status", "OPERATIONAL")
            # skip closed businesses
            if status != "OPERATIONAL":
                continue
            businesses.append({
                "name": place.get("name"),
                "place_id": place.get("place_id"),
                "rating": place.get("rating", 0),
                "review_count": place.get("user_ratings_total", 0),
                # "map_url": f"https://www.google.com/maps/place/?q=place_id:{place.get('place_id')}",
            })
        # Check if a next page exists
        next_page_token = results.get("next_page_token")

        if not next_page_token:
            break  # No more results

        time.sleep(2)

        # Fetch the next 20 results using the token
        results = gmaps.places_nearby(page_token=next_page_token)

    print(f"{len(businesses)} businesses found")
    return businesses

if __name__ == "__main__":
      potential = discover("75080", "law firm")
      top_businesses = filter_top_25(potential) # this is list dict

      for b in top_businesses:
        print(
            f"Name: {b['name']} | Rating: {b['rating']:.1f} | Reviews: {b['review_count']}"
        )
        print(f"https://www.google.com/maps/place/?q=place_id:{b['place_id']}")
        print("-" * 40)