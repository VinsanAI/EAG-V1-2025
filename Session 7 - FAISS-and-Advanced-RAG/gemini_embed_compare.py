import numpy as np
from scipy.spatial.distance import cosine
import requests
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

def get_embedding(text: str) -> np.ndarray:
    load_dotenv()
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.embed_content(
        model="gemini-embedding-exp-03-07",
        contents=text,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
    )
    
    return np.array(response.embeddings[0].values, dtype=np.float32)

# 🎯 Phrases to compare
sentences = [
    "How does AlphaFold work?",
    "Can you help me with the capital of France?",
    "How do proteins fold?",
    "What is the capital of France?",
    "Explain how neural networks learn."
]

embeddings = [get_embedding(s) for s in sentences]

def cosine_similarity(v1, v2):
    return 1-cosine(v1,v2)

print("Semantc Similarity Matrix:\n")
for i in range(len(sentences)):
    for j in range(i+1, len(sentences)):
        sim = cosine_similarity(embeddings[i], embeddings[j])
        print(f"\"{sentences[i]}\" <> \"{sentences[j]}\" -> {sim:.3f}")