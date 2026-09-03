import os
import googlemaps
from anthropic import Anthropic
import requests
from dotenv import load_dotenv
import json


load_dotenv()

print("All libraries imported successfully")

# api keys
maps_key = os.getenv("GOOGLE_API_KEY")
claude_key = os.getenv("ANTHROPIC_API_KEY")
hunter_key = os.getenv("HUNTER_API_KEY")

gmaps = googlemaps.Client(key=maps_key)

def discover(zipcode: str, business_type: str) -> list[dict]:
    geocode_result = gmaps.geocode(zipcode)
    lat_lng = geocode_result[0]["geometry"]["location"]
    # Returns: {'lat': some number, 'lng': some number}

    results = gmaps.places_nearby(
        location=lat_lng,
        radius=5000,
        keyword=business_type
    )

    businesses = []
    for place in results.get("results"):
            businesses.append({
                'name': place.get('name'),
                'address': place.get('vicinity'),
                'rating': place.get('rating'),
                'review_count': place.get('user_ratings_total', 0)
            })
    
    print(f"{len(businesses)} businesses found")
    return businesses

if __name__ == "__main__":
      potential = discover("78717", "law firm")

      for b in potential[:3]:
        print(
            f"Name: {b['name']} | Rating: {b['rating']} | Reviews: {b['review_count']}"
        )
        print(f"Address: {b['address']}")
        print("-" * 40)


# print(json.dumps(result, indent=3))

# client = Anthropic()
# response = client.messages.create(
#     model="claude-sonnet-5",
#     max_tokens=100,
#     messages=[{
#         "role": "user",
#         "content": "respond with only 'hi3'"
#     }]
# )

# print(response.content[0].text)
