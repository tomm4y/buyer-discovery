import os
from dotenv import load_dotenv
from pinecone import Pinecone
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

load_dotenv()

pinecone_key = os.getenv("PINECONE_API_KEY")

pc = Pinecone(api_key=pinecone_key)

index = pc.Index("reviews")

def fetch_reviews(zipcode: str, business_type: str) -> list[dict]:
    dummy_vector = [0.0] * 1536
    response = index.query(
        vector=dummy_vector,
        filter={
            "zipcode": zipcode,
            "business_type": business_type
        },
        top_k=1000,
        include_values=True,
        include_metadata=True
    )
    reviews = []
    for match in response.matches:
        reviews.append({
            'embedding': match.values,
            "text": match.metadata["text"]
        })
    return reviews

def cluster_reviews(reviews: list[dict]) -> list[list]:
    embeddings = [review["embedding"] for review in reviews]
    '''
        kmeans.fit_predict(embeddings) takes the list of review embeddings,
        runs K-means using the configuration we set (n_clusters, etc.), 
        and returns a label for each embedding.
        The returned labels array has the same number of items as there are reviews. 
        Each index corresponds to the review/embedding at
        that same index, and the value tells us which cluster that review belongs to.
    '''
    
    for k in range(2, 7):
        kmeans = KMeans(n_clusters=k, random_state=42) # configure K-means with k clusters
        labels = kmeans.fit_predict(embeddings) # labels
        score = silhouette_score(embeddings, labels)
        print(k)
        print(score)

if __name__ == "__main__":
    fetched_reviews = fetch_reviews('75080', 'lawyer')
    cluster_reviews(fetched_reviews)
    