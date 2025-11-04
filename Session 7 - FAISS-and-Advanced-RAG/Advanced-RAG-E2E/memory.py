from textwrap import indent
import numpy as np
import faiss
import requests
from typing import List, Optional, Literal
from pydantic import BaseModel
from datetime import datetime

class MemoryItem(BaseModel):
    text: str
    type: Literal["preference", "tool_output", "fact", "query", "system"] = "fact"
    timestamp: Optional[str] = datetime.now().isoformat()
    tool_name: Optional[str] = None
    user_query: Optional[str] = None
    tags: List[str] = []
    session_id: Optional[str] = None

class MemoryManager:
    def __init__(self,
                 embedding_model_url="http://localhost:11434/api/embeddings",
                 model_name="bge-m3"):
        self.embedding_model_url = embedding_model_url
        self.model_name = model_name
        self.index = None
        self.data: List[MemoryItem] = []
        self.embeddings: List[np.ndarray] = []

    def _get_embedding(self, text: str) -> np.ndarray:
        response = requests.post(
            self.embedding_model_url,
            json={"model": self.model_name, "prompt": text}
        )
        response.raise_for_status()
        return np.array(response.json()["embedding"], dtype=np.float32)

    def add(self, item: MemoryItem):
        emb = self._get_embedding(item.text)
        self.embeddings.append(emb)
        self.data.append(item)

        # Initialize or add to index
        if self.index is None:
            self.index = faiss.IndexFlatL2(len(emb))
        self.index.add(np.stack([emb]))

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        type_filter: Optional[str] = None,
        tag_filter: Optional[List[str]] = None,
        session_filter: Optional[str] = None
    ) -> List[MemoryItem]:
        if not self.index or len(self.data)==0:
            return []

        query_vec = self._get_embedding(query).reshape(1,-1)
        D, I = self.index.search(query_vec, top_k * 2) # Overfetch to allow filtering

        results = []
        for idx in I[0]:
            if idx >= len(self.data):
                continue
            item = self.data[idx]

            if type_filter and item.type != type_filter:
                continue

            if tag_filter and not any(tag in item.tags for tag in tag_filter):
                continue

            if session_filter and item.session_id != session_filter:
                continue

            results.append(item)
            if len(results) >= top_k:
                break

        return results

    def bulk_add(self, items: List[MemoryItem]):
        for item in items:
            self.add(item)

# if __name__ == "__main__":
#     # --- 1. Setup ---
#     print("--- Initializing MemoryManager ---")
#     # Make sure Ollama is running locally with 'bge-m3' pulled!
#     # Example: ollama run bge-m3
#     try:
#         manager = MemoryManager()
#     except requests.exceptions.RequestException:
#         print("\n*** TEST ABORTED ***\nPlease ensure Ollama is running and accessible at http://localhost:11434 before running the script.")
#         exit()

#     # --- 2. Synthetic Memory Items (Real-World Agent Flow) ---
#     print("\n--- Adding Synthetic Memories (Session ID: 12345) ---")

#     memories = [
#         MemoryItem(
#             text="The user prefers concise summaries and is annoyed by lengthy explanations. Always start with the main point.",
#             type="preference",
#             tags=["communication", "tone"],
#             session_id="00000" # A general, non-session preference
#         ),
#         MemoryItem(
#             text="User's previous session (12345) was about a failed API request to retrieve customer data due to a timeout.",
#             type="query",
#             user_query="Please get me the latest billing details.",
#             session_id="12345"
#         ),
#         MemoryItem(
#             text="TOOL_CALL: 'get_customer_data' failed with error: 'Timeout after 10s. External service unreachable.'",
#             type="tool_output",
#             tool_name="get_customer_data",
#             session_id="12345"
#         ),
#         MemoryItem(
#             text="The agent successfully used the 'reset_router' tool for Session 67890 after a customer's complaint about slow Wi-Fi.",
#             type="tool_output",
#             tool_name="reset_router",
#             session_id="67890" # Different session
#         ),
#         MemoryItem(
#             text="Current customer has a VIP Platinum status and a known history of recurring network stability issues in the last 6 months.",
#             type="fact",
#             tags=["VIP", "network"],
#             session_id="12345"
#         ),
#         MemoryItem(
#             text="It is company policy that VIP customers must be offered a $50 credit for any service disruption lasting over 2 hours.",
#             type="system",
#             tags=["policy", "VIP"],
#             session_id="00000"
#         ),
#     ]

#     manager.bulk_add(memories)

#     # --- 3. User Query ---
#     USER_QUERY = "I need to know the latest status of my account, and I'm worried about connection stability like before."

#     print(f"\n--- Testing Retrieval ---")
#     print(f"QUERY: '{USER_QUERY}'")
#     TOP_K = 3

#     # --- 4. Search and Print Results ---
    
#     # Test 1: General retrieval for the current session context
#     print(f"\n[Test 1: General retrieval for query (Top {TOP_K})]")
#     results = manager.retrieve(USER_QUERY, top_k=TOP_K)
    
#     if results:
#         for i, item in enumerate(results):
#             print(f"  Result {i+1}:")
#             print(f"    Text: {item.text}")
#             print(f"    Type: {item.type}, Tags: {item.tags}, Session: {item.session_id}")
#     else:
#         print("  No results found.")

#     # Test 2: Retrieval with a type filter
#     print(f"\n[Test 2: Retrieval with type='system' filter (Policy)]")
#     policy_results = manager.retrieve("What compensation should I offer a VIP customer?", top_k=1, type_filter="system")
    
#     if policy_results:
#         for i, item in enumerate(policy_results):
#             print(f"  Result {i+1}:")
#             print(f"    Text: {item.text}")
#             print(f"    Type: {item.type}, Tags: {item.tags}, Session: {item.session_id}")
#     else:
#         print("  No policy results found.")

            

        


