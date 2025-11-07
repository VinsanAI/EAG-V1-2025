# This contains all the exhaustive tools for the agent

import markitdown
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent
from mcp import types
from PIL import Image as PILImage
import math
import sys
import os
import faiss
import json
import numpy as np
from pathlib import Path
import requests
from markitdown import MarkItDown
import time
from models import (AddInput, AddOutput, SqrtInput, SqrtOutput, 
            StringsToIntsInput, StringsToIntsOutput, ExpSumInput, 
            ExpSumOutput, TwoFloatInputs, OneFloatOutput, 
            OneFloatInput, ScheduleMeetingInput)
from tqdm import tqdm
import hashlib
# from pdb import set_trace

mcp = FastMCP("MCP Server - Custom Agentic Flow")

EMBED_URL = "http://localhost:11434/api/embeddings"
# EMBED_MODEL = "nomic-embed-text"
EMBED_MODEL = "bge-m3"
CHUNK_SIZE = 180
CHUNK_OVERLAP = 40
ROOT = Path(__file__).parent.resolve()
print(f"Root folder identified: \"{ROOT}\"")

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

def file_hash(path):
        return hashlib.md5(Path(path).read_bytes()).hexdigest()

def process_documents():
    """Process documents and create FAISS index"""
    mcp_log("INFO", "Indexing documents with MarkItDown...")
    ROOT = Path(__file__).parent.resolve()
    DOC_PATH = ROOT / "documents"
    INDEX_CACHE = ROOT / "faiss_index"
    INDEX_CACHE.mkdir(exist_ok=True)
    INDEX_FILE = INDEX_CACHE / "index.bin"
    METADATA_FILE = INDEX_CACHE / "metadata.json"
    CACHE_FILE = INDEX_CACHE / "doc_index_cache.json"

    index = faiss.read_index(str(INDEX_FILE)) if INDEX_FILE.exists() else None
    metadata = json.loads(METADATA_FILE.read_text()) if METADATA_FILE.exists() else []
    CACHE_META = json.loads(CACHE_FILE.read_text()) if CACHE_FILE.exists() else {}
    all_embeddings = []
    converter = MarkItDown()

    for file in DOC_PATH.glob("*.*"):
        fhash = file_hash(file)
        if file.name in CACHE_META and CACHE_META[file.name]==fhash:
            mcp_log("SKIP", f"Skipping unchanged file: \"{file.name}\"")
            continue
        
        mcp_log("PROC", f"Processing: \"{file.name}\"")
        try:
            result = converter.convert(str(file))
            markdown = result.text_content
            chunks = list(chunk_text(markdown))
            embeddings_for_file = []
            new_metadata = []
            for i, chunk in enumerate(tqdm(chunks, desc=f"Embedding: \"{file.name}\"")):
                embedding = get_embedding(chunk)
                embeddings_for_file.append(embedding)
                new_metadata.append({"doc":file.name, "chunk":chunk, "chunk_id":f"{file.stem}_{i}"})
            if embeddings_for_file:
                if index is None:
                    dim = len(embeddings_for_file[0])
                    index = faiss.IndexFlatL2(dim)
                index.add(np.stack(embeddings_for_file))
                metadata.extend(new_metadata)
            CACHE_META[file.name] = fhash
        except Exception as e:
            mcp_log("ERROR", f"Failed to process \"{file.name}\"")

    CACHE_FILE.write_text(json.dumps(CACHE_META, indent=2))
    METADATA_FILE.write_text(json.dumps(metadata, indent=2))
    if index and index.ntotal>0:
        faiss.write_index(index, str(INDEX_FILE))
        mcp_log("SUCCESS", f"Saved FAISS Index and Metadata")
    else:
        mcp_log("WARN", "No new documents or updates to process")

def ensure_faiss_ready():
    index_path = ROOT / "faiss_index" / "index.bin"
    meta_path = ROOT / "faiss_index" / "metadata.json"
    cache_path = ROOT / "faiss_index" / "doc_index_cache.json"
    doc_path = ROOT / "documents"

    if not(index_path.exists() and meta_path.exists() and cache_path.exists()):
        mcp_log("INFO", "Index not found - running process_documents()...")
        process_documents()
    elif cache_path.exists() and doc_path.exists():
        cache_meta = json.loads(cache_path.read_text())
        flag_indexing_req=False
        for file in doc_path.glob("*.*"):
            fhash = file_hash(file)
            if file.name in cache_meta and cache_meta[file.name] == fhash:
                pass
            else:
                flag_indexing_req=True
                continue
        if flag_indexing_req:
            mcp_log("INFO", "Document updates found - running process_documents()...")
            process_documents()
    else:
        mcp_log("INFO", "Index already exists. Skipping regeneration.")

@mcp.tool()
def search_documents(query: str) -> list[str]:
    """Search for relevant content from uploaded documents."""
    ensure_faiss_ready()
    mcp_log("SEARCH", f"Query: \"{query}\"")
    try:
        index = faiss.read_index(str(ROOT / "faiss_index" / "index.bin"))
        metadata = json.loads((ROOT / "faiss_index" / "metadata.json").read_text())
        query_vec = get_embedding(query).reshape(1,-1)
        D, I = index.search(query_vec, k=1)
        results=[]
        for idx in I[0]:
            data = metadata[idx]
            results.append(f"{data['chunk']}\n [Source: {data['doc']}, ID: {data['chunk_id']}]")
        return results
    except Exception as e:
        return [f"Error - Failed to search: {str(e)}"]

@mcp.tool()
def add(input: AddInput) -> AddOutput:
    """Add two numbers"""
    print("CALLED: add(AddInput) -> AddOutput")
    return AddOutput(result=input.a + input.b)

@mcp.tool()
def sqrt(input: SqrtInput) -> SqrtOutput:
    """Square root of a number"""
    print("CALLED: sqrt(SqrtInput) -> SqrtOutput")
    return SqrtOutput(result=input.a ** 0.5)

@mcp.tool()
def subtract(input: TwoFloatInputs) -> OneFloatOutput:
    """Subtract two numbers"""
    print("CALLED: subtract(TwoFloatInputs) -> inOneFloatOutput")
    return OneFloatOutput(result=input.a - input.b)

@mcp.tool()
def multiply(input: TwoFloatInputs) -> OneFloatOutput:
    """Multiply two numbers"""
    print("CALLED: multiply(TwoFloatInputs) -> inOneFloatOutput")
    return OneFloatOutput(result=input.a * input.b)

@mcp.tool()
def divide(input: TwoFloatInputs) -> OneFloatOutput:
    """Multiply two numbers"""
    print("CALLED: divide(TwoFloatInputs) -> inOneFloatOutput")
    return OneFloatOutput(result=input.a / input.b)

# power tool
@mcp.tool()
def power(a: int, b: int) -> int:
    """Power of two numbers"""
    print("CALLED: power(a: int, b: int) -> int:")
    return int(a ** b)


# cube root tool
@mcp.tool()
def cbrt(a: int) -> float:
    """Cube root of a number"""
    print("CALLED: cbrt(a: int) -> float:")
    return float(a ** (1/3))

# factorial tool
@mcp.tool()
def factorial(a: int) -> int:
    """factorial of a number"""
    print("CALLED: factorial(a: int) -> int:")
    return int(math.factorial(a))

# log tool
@mcp.tool()
def log(a: int) -> float:
    """log of a number, Inputs required 'a' as integer input"""
    print("CALLED: log(a: int) -> float:")
    return float(math.log(a))

# remainder tool
@mcp.tool()
def remainder(a: int, b: int) -> int:
    """remainder of two numbers divison"""
    print("CALLED: remainder(a: int, b: int) -> int:")
    return int(a % b)

# sin tool
@mcp.tool()
def sin(a: int) -> float:
    """sin of a number"""
    print("CALLED: sin(a: int) -> float:")
    return float(math.sin(a))

# cos tool
@mcp.tool()
def cos(a: int) -> float:
    """cos of a number"""
    print("CALLED: cos(a: int) -> float:")
    return float(math.cos(a))

# tan tool
@mcp.tool()
def tan(a: int) -> float:
    """tan of a number"""
    print("CALLED: tan(a: int) -> float:")
    return float(math.tan(a))

# mine tool
@mcp.tool()
def mine(a: int, b: int) -> int:
    """special mining tool"""
    print("CALLED: mine(a: int, b: int) -> int:")
    return int(a - b - b)

@mcp.tool()
def create_thumbnail(image_path: str) -> Image:
    """Create a thumbnail from an image"""
    print("CALLED: create_thumbnail(image_path: str) -> Image:")
    img = PILImage.open(image_path)
    img.thumbnail((100, 100))
    return Image(data=img.tobytes(), format="png")

@mcp.tool()
def strings_to_chars_to_int(input: StringsToIntsInput) -> StringsToIntsOutput:
    """Return the ASCII values of the characters in a word"""
    print("CALLED: strings_to_chars_to_int(StringsToIntsInput) -> StringsToIntsOutput")
    ascii_values = [ord(char) for char in input.string]
    return StringsToIntsOutput(ascii_values=ascii_values)

@mcp.tool()
def int_list_to_exponential_sum(input: ExpSumInput) -> ExpSumOutput:
    """Return sum of exponentials of numbers in a list"""
    print("CALLED: int_list_to_exponential_sum(ExpSumInput) -> ExpSumOutput")
    result = sum(math.exp(i) for i in input.int_list)
    return ExpSumOutput(result=result)

@mcp.tool()
def fibonacci_numbers(n: int) -> list:
    """Return the first n Fibonacci Numbers"""
    print("CALLED: fibonacci_numbers(n: int) -> list:")
    if n <= 0:
        return []
    fib_sequence = [0, 1]
    for _ in range(2, n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence[:n]

# DEFINE RESOURCES

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    print("CALLED: get_greeting(name: str) -> str:")
    return f"Hello, {name}!"


# DEFINE AVAILABLE PROMPTS
@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"
    print("CALLED: review_code(code: str) -> str:")


@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]

# @mcp.tool()
# def schedule_meeting(input: ScheduleMeetingInput) -> str:
#     """Schedule a meeting and send the Google Calendar invite.

#     Expected Inputs:
#     - audience_email_dl (str): Email address or distribution list to invite (e.g., "team@company.com").
#     - meeting_date (str): Meeting date in YYYY-MM-DD format (e.g., "2025-11-07").
#     - meeting_duration (str): Duration of the meeting in minutes (e.g., "30").
#     - start_time (str): Start time in HH:MM 24-hour format (e.g., "14:30").
#     """
#     print(f"\n\"Scheduled a meeting with email: '{ScheduleMeetingInput.audience_email_dl}' on \
#         '{ScheduleMeetingInput.meeting_date}' for duration of '{ScheduleMeetingInput.meeting_duration}' \
#             minutes at '{ScheduleMeetingInput.start_time}'\"")

@mcp.tool()
def schedule_meeting(audience_email_dl,
                    meeting_date,
                    meeting_duration,
                    start_time) -> str:
    """Schedule a meeting and send the Google Calendar invite.

    Required Inputs:
    - audience_email_dl (str): Email address or distribution list to invite (e.g., "team@company.com").
    - meeting_date (str): Meeting date in YYYY-MM-DD format (e.g., "2025-11-07").
    - meeting_duration (str): Duration of the meeting in minutes (e.g., "30").
    - start_time (str): Start time in HH:MM 24-hour format (e.g., "14:30").
    """
    return f"\n\n\"Scheduled a meeting with email: '{audience_email_dl}' on \
        '{meeting_date}' for duration of '{meeting_duration}' \
            minutes at '{start_time}'\"\n\n"

if __name__ == "__main__":
    print("Starting MCP Server - Custom Agentic Flow")

    if len(sys.argv)>1 and sys.argv[1] == "dev":
        mcp.run() # Run without transport for dev server
    else:
        # Start the server in a separate thread
        import threading
        server_thread = threading.Thread(target=lambda: mcp.run(transport="stdio"))
        server_thread.daemon = True
        server_thread.start()

        # Wait a moment for the server to start
        time.sleep(2)
        
        # Process documents after server is running
        ensure_faiss_ready()

        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting Down....")



    # Practice and Validation aspects
    # query = "When will Dhoni retire? Can an AI predict this?"
    # query = input(f"What would you like me to fetch today?\n>>")
    # results = search_documents(query)
    # print(results)

    # result1 = add(AddInput(a="6", b="25"))
    # print(result1.result)

    # # This is how mcp call_tool function calls this function
    # args = {"a": 6, "b": 25}
    # print(add(AddInput(**args)))

    # result2 = sqrt(SqrtInput(a="8"))
    # print(result2.result)

    # result3 = subtract(TwoFloatInputs(a=65.36, b="85.36"))
    # print(result3.result)

    # result4 = multiply(TwoFloatInputs(a=65.36, b="85.36"))
    # print(result4.result)

    # result5 = divide(TwoFloatInputs(a=65.36, b="85.36"))
    # print(result5.result)

    
