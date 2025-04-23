import requests

# Make a GET request to the API
response1 = requests.get(
    "http://localhost:8000/rag/",
    params={"question": "tell me about generative computer vision"}
)
response2 = requests.get(
    "http://localhost:8000/search/",
    params={"query": "generative computer vision"}
)



# Print the response
print(response1.json()["answer"])
print(response2.json()["results"][0])