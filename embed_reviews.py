import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone
import json

load_dotenv()

pinecone_key = os.getenv("PINECONE_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")

openai_client = OpenAI(api_key=openai_key)
pc = Pinecone(api_key=pinecone_key)

index = pc.Index("reviews")

def load_json(file_path: str) -> list[str]:
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def embed_texts(texts: list[str]) -> list[list[float]]:
    objects = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    # for item in objects.data, -> item.embedding
    return [item.embedding for item in objects.data]

def upsert_index(reviews: list[dict], embeddings: list[list[float]], zipcode: str, business_type: str):
    vectors_to_upsert = []
    for i, (review, vector) in enumerate(zip(reviews, embeddings)):
        vectors_to_upsert.append({
            'id': f"{review['place_id']}_{i}",
            'values': vector,
            'metadata': {
                'place_id': review['place_id'],
                "zipcode": zipcode,
                "business_type": business_type,
                'text': review['text']
            }
        })
    index.upsert(vectors=vectors_to_upsert)

if __name__ == "__main__":
    path = "cleaned_data/75080_lawyer.json"
    
    reviews = load_json(path)
    texts = [review['text'] for review in reviews]
    embedded = embed_texts(texts)
    upsert_index(reviews, embedded, '75080', 'lawyer')