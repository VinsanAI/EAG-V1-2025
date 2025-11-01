import os
from pathlib import Path
import faiss
import numpy as np
import requests
import json
import time

# Config
CHUNK_SIZE = 40
CHUNK_OVERLAP = 10
DOC_PATH = Path("documents")

print(DOC_PATH)
print(list(DOC_PATH.glob("*.txt")))

# Helpers
def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    words = text.split()
    chunks = []
    for i in range(0, len(words), size-overlap):
        chunk = " ".join(words[i:i+size])
        if chunk:
            chunks.append(chunk)
    return chunks

# Example to understand the logic
# string = """This program reads text files, chops them into small pieces, 
# turns each piece into a special number "fingerprint", saves those fingerprints into a fast search shelf, 
# and then finds the pieces that are most like a question you ask."""
# print(len(string.split()))
# print(list(range(0, len(string.split()), 8-4)))
# print(chunk_text(string, 8, 4))

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

# Load docs & chunks
all_chunks = []
metadata = []

for file in DOC_PATH.glob("*.txt"):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
        chunks = chunk_text(content)
        for idx, chunk in enumerate(chunks):
            all_chunks.append(get_embedding(chunk))
            metadata.append({
                "doc_name": file.name,
                "chunk": chunk,
                "chunk_id": f"{file.stem}_{idx}"
            })
    print(f"Processing {file.name}....")
    time.sleep(1)

print(metadata)

# Create FAISS index
dimension = len(all_chunks[0])
index = faiss.IndexFlatL2(dimension)
index.add(np.stack(all_chunks))

# Print the index completion
print(f"Completed {len(all_chunks)} chunks from {len(list(DOC_PATH.glob("*.txt")))} documents")

# Search
query = "when will dhoni retire?"
query_vector = get_embedding(query).reshape(1,-1)
D, I = index.search(query_vector, k=3)

print(f"\n🔍 Query: {query}\n\n📚 Top Matches:")
for rank, idx in enumerate(I[0]):
    data = metadata[idx]
    print(f"Rank: {rank+1}: From {data['doc_name']} | {data['chunk_id']}")
    print(f">> \"{data["chunk"]}\"")