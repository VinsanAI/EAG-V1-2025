# from pathlib import Path

# if __name__ == "__main__":
#     ROOT = Path(__file__).parent.resolve()    
#     print(ROOT)

#     index_path = ROOT / "faiss_index" / "index.bin"
#     meta_path = ROOT / "faiss_index" / "metadata.json"

#     print(index_path.exists())
#     print(meta_path.exists())


# import ollama 
# print(ollama.embeddings(model="mxbai-embed-large", prompt="This is Santosh Kumar"))


from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent
from mcp import types
from PIL import Image as PILImage
import math
import sys
import os
import json
import faiss
import numpy as np
from pathlib import Path
import requests
from markitdown import MarkItDown
import time
from models import AddInput, AddOutput, SqrtInput, SqrtOutput, StringsToIntsInput, StringsToIntsOutput, ExpSumInput, ExpSumOutput
from PIL import Image as PILImage
from tqdm import tqdm
import hashlib
from pdb import set_trace

mcp = FastMCP("Calculator")

EMBED_URL = "http://localhost:11434/api/embeddings"
# EMBED_MODEL = "nomic-embed-text"
EMBED_MODEL = "bge-m3"
CHUNK_SIZE = 128
CHUNK_OVERLAP = 40
ROOT = Path(__file__).parent.resolve()

def get_embedding(text: str) -> np.ndarray:
    response = requests.post(EMBED_URL, json={"model": EMBED_MODEL, "prompt": text})
    response.raise_for_status()
    return np.array(response.json()["embedding"], dtype=np.float32)

def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    words = text.split()
    for i in range(0, len(words), size - overlap):
        yield " ".join(words[i:i+size])

def mcp_log(level: str, message: str) -> None:
    """Log a message to stderr to avoid interfering with JSON communication"""
    sys.stderr.write(f"{level}: {message}\n")
    sys.stderr.flush()

"""Process documents and create FAISS index"""
mcp_log("INFO", "Indexing documents with MarkItDown...")
ROOT = Path(__file__).parent.resolve()
DOC_PATH = ROOT / "documents"
INDEX_CACHE = ROOT / "faiss_index"
INDEX_CACHE.mkdir(exist_ok=True)
INDEX_FILE = INDEX_CACHE / "index.bin"
METADATA_FILE = INDEX_CACHE / "metadata.json"
CACHE_FILE = INDEX_CACHE / "doc_index_cache.json"

def file_hash(path):
    return hashlib.md5(Path(path).read_bytes()).hexdigest()

CACHE_META = json.loads(CACHE_FILE.read_text()) if CACHE_FILE.exists() else {}
metadata = json.loads(METADATA_FILE.read_text()) if METADATA_FILE.exists() else []
index = faiss.read_index(str(INDEX_FILE)) if INDEX_FILE.exists() else None
all_embeddings = []
converter = MarkItDown()

# set_trace()

for file in DOC_PATH.glob("*.*"):
    fhash = file_hash(file)
    # set_trace()
    if file.name in CACHE_META and CACHE_META[file.name] == fhash:
        mcp_log("SKIP", f"Skipping unchanged file: {file.name}")
        continue

    mcp_log("PROC", f"Processing: {file.name}")
    try:
        # set_trace()
        result = converter.convert(str(file))
        markdown = result.text_content
        chunks = list(chunk_text(markdown))
        embeddings_for_file = []
        new_metadata = []
        # set_trace()
        for i, chunk in enumerate(tqdm(chunks, desc=f"Embedding {file.name}")):
            # set_trace()
            embedding = get_embedding(chunk)
            embeddings_for_file.append(embedding)
            new_metadata.append({"doc": file.name, "chunk": chunk, "chunk_id": f"{file.stem}_{i}"})
        if embeddings_for_file:
            if index is None:
                dim = len(embeddings_for_file[0])
                index = faiss.IndexFlatL2(dim)
            index.add(np.stack(embeddings_for_file))
            metadata.extend(new_metadata)
        CACHE_META[file.name] = fhash
        # set_trace()
    except Exception as e:
        mcp_log("ERROR", f"Failed to process {file.name}: {e}")

CACHE_FILE.write_text(json.dumps(CACHE_META, indent=2))
METADATA_FILE.write_text(json.dumps(metadata, indent=2))

# set_trace()

if index and index.ntotal > 0:
    faiss.write_index(index, str(INDEX_FILE))
    mcp_log("SUCCESS", "Saved FAISS index and metadata")
else:
    mcp_log("WARN", "No new documents or updates to process.")