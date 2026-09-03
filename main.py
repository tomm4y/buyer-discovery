import os
from anthropic import Anthropic
import requests
from dotenv import load_dotenv

load_dotenv()

print("All libraries imported successfully")

client = Anthropic()

# response = client.messages.create(
#     model="claude-sonnet-5",
#     max_tokens=100,
#     messages=[{
#         "role": "user",
#         "content": "respond with only 'hi3'"
#     }]
# )

# print(response.content[0].text)

url = "https://api.github.com"
resp = requests.get(url)
print({resp.status_code})