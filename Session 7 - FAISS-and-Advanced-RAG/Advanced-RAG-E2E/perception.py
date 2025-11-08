from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv
from google import genai
import re
import datetime
import ollama
import requests

def log(stage: str, msg: str):
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] [{stage}] {msg}")

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class PerceptionResult(BaseModel):
    user_input: str
    intent: Optional[str]
    entities: List[str] = []
    tool_hint: Optional[str] = None

def generate_with_phi4(user_input: str) -> str:
    local_llm_url = "http://localhost:11434/api/generate"
    local_llm_model = "phi4"
    response = requests.post(
            local_llm_url,
            json={"model": local_llm_model, "prompt": user_input, "stream": False}
        )
    response.raise_for_status()
    return(response.json()['response'])

def extract_perception(user_input: str) -> PerceptionResult:
    """Extracts intent, entities and tool hints using LLM"""

#     prompt = f"""
# You are an AI that extracts structured facts from user input.

# Input: "{user_input}"

# Return the response as Python dictionary with keys:
# - intent: (brief phrase about what user wants)
# - entities: a list of strings representing keywords or values (e.g., ["INDIA", "ASCII"])
# - tool_hint: (name of the MCP tool that might be useful, if any)

# Output only dictionary as a single line. Do NOT wrap it in ```json or other formatting. Ensure `entities` is a list of strings, not a dictionary.
#     """

    prompt = f"""
**<|im_start|>system**
You are a highly efficient fact extractor and intent classifier. Your only task is to analyze the user's request and immediately output a Python dictionary containing the exact structured facts requested, strictly following all formatting rules.

**ABSOLUTELY DO NOT GENERATE ANY REASONING, THOUGHT PROCESS, OR INTERMEDIATE TEXT.**
**DO NOT OUTPUT THE <think> BLOCK.**
**OUTPUT ONLY THE FINAL DICTIONARY.**

**<|im_end|>**
**<|im_start|>user**
Input: "{user_input}"

Return the response as a single-line Python dictionary with the following keys:
- **intent**: (brief phrase about what user wants)
- **entities**: (a list of strings representing keywords or values, e.g., ["DataScience team", "November 5, 2025"])
- **tool_hint**: (name of the hypothetical MCP tool that might have capability to perform this action, simple name)

**STRICTY produce dictionary output aloneand nothing else. Do NOT wrap it in ```json or other formatting.**
**<|im_end|>**
**<|im_start|>assistant**
    """

    try:
        # print(prompt)

        # Google Gemini - Gemini 2.0 Flash
        # response = client.models.generate_content(
        #     model="gemini-2.0-flash",
        #     contents=prompt
        # )
        # raw = response.text.strip()

        response = generate_with_phi4(user_input=prompt)
        # print(response['message']['content'])
        
        raw = response.strip()
        log("perception", f"LLM output: {raw}")

        clean = re.sub(r"^```json|```$", "", raw.strip(), flags=re.MULTILINE).strip()
        clean = re.sub(r"^```python|```$", "", raw.strip(), flags=re.MULTILINE).strip()

        try:
            parsed = eval(clean)
        except Exception as e:
            log("perception", f"⚠️ Failed to parse cleaned output: {e}")
            raise

        if isinstance(parsed['entities'], dict):
            parsed['entities'] = list(parsed['entities'].values())

        return PerceptionResult(user_input=user_input, **parsed)

    except Exception as e:
        log("perception", f"Extraction Failed: {e}")
        return PerceptionResult(user_input=user_input)

# if __name__=="__main__":
#     user_input = input("Provide the input to process:\n>>")
#     result = extract_perception(user_input=user_input)
#     print(result)
    # result = generate_with_phi4("Respond with any random number between 1 to 1000, STRICTLY respond with only a number")
    # print(result)

# Schedule a meeting with my internal DataScience team on November 5, 2025 regarding immediate analysis on customer service agents performance
# What is the sum of 5 and 6?