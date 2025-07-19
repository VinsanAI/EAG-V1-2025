from dotenv import load_dotenv
import os

def add(a:int, b:int) -> int:
    """add two numbers"""
    return a+b

def subtract(a:int, b:int) -> int:
    """subtract two numbers"""
    return a-b

function_map = {
    'add': add,
    'subtract': subtract
}

if __name__ == "__main__":
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    print(api_key)

    print("Method 1: Using dictionary access")
    results1 = function_map['add'](1,2)
    print(f"1 + 2 = {results1}")

    results2 = function_map['subtract'](5,3)
    print(f"5 - 2 = {results2}")