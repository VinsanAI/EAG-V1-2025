import numpy as np
import requests

# Helper: Get Ollama embeddings for a text 
def get_embeddings(text: str) -> np.ndarray:
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={
            "model": "nomic-embed-text", 
            "prompt": text
        }
    )
    response.raise_for_status()
    return np.array(response.json()["embedding"], dtype=np.float32)

print(get_embeddings("Hello, world!")[:5])