import faiss
import numpy as np
import requests
import json

# Helper: Get Ollama embedding for a text
def get_embedding(text: str) -> np.ndarray:
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={
            "model": "nomic-embed-text",
            "prompt": text
        }
    )
    response.raise_for_status()
    return np.array(response.json()["embedding"], dtype=np.float32)

# 🎭 Corpus of jokes with metadata
jokes = [
    {"id": 1, "category": "animals", "text": "Why don't cows have any money? Because farmers milk them dry."},
    {"id": 2, "category": "tech", "text": "Why do programmers prefer dark mode? Because light attracts bugs."},
    {"id": 3, "category": "school", "text": "Why did the student eat his homework? Because the teacher said it was a piece of cake."},
    {"id": 4, "category": "classic", "text": "I told my wife she was drawing her eyebrows too high. She looked surprised."},
    {"id": 5, "category": "tech", "text": "How do you comfort a JavaScript bug? You console it."}
]

# ✨ Create FAISS index
embeddings = [get_embedding(j['text']) for j in jokes]
dimension = len(embeddings[0])
index = faiss.IndexFlatL2(dimension)
index.add(np.stack(embeddings))

print(embeddings[0][:5])
print(len(embeddings))
print(len(embeddings[0]))
print(np.stack(embeddings).shape)

# 🧠 Store joke metadata by index
metadata_lookup = {i: jokes[i] for i in range(len(jokes))}
print(metadata_lookup)

# 🧐 Query
query = "Something about software engineers and debugging."
query_vector = get_embedding(query).reshape(1,-1)

# 🔍 Top-3 search
D, I = index.search(query_vector, k=3)
print(D)
print(I)

# 🎉 Results
print(f"Query: {query}")
print("\nTop Joke Matches:")
for rank, idx in enumerate(I[0]):
    joke = metadata_lookup[idx]
    print(f"#{rank+1}")
    print(f"Joke id: {joke['id']}")
    print(f"Joke Category: {joke['category']}")
    print(f"Joke text: {joke['text']}")