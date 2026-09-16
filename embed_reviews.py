import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

load_dotenv()

pinecone_key = os.getenv("PINECONE_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")

openai = OpenAI(api_key=openai_key)
pc = Pinecone(api_key=pinecone_key)

index = pc.Index("reviews")

def embed_texts()