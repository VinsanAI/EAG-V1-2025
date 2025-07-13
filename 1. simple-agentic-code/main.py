import os
from dotenv import load_dotenv
from google import genai
import math

def strings_to_chars_to_int(string):
    return [ord(char) for char in string]

def int_list_to_exponential_sum(int_list):
    int_list = eval(int_list)
    return sum(math.exp(i) for i in int_list)

def fibonacci_numbers(n):
    if n <= 0:
        return []
    fib_sequence = [0, 1]
    for _ in range(2, n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence[:n]

def function_caller(func_name, params):
    """Simple function caller that maps function names to actual functions"""
    function_map = {
        "strings_to_chars_to_int": strings_to_chars_to_int,
        "int_list_to_exponential_sum": int_list_to_exponential_sum,
        "fibonacci_numbers": fibonacci_numbers
    }
    
    if func_name in function_map:
        return function_map[func_name](params)
    else:
        return f"Function {func_name} not found"

def main():
    # print("Hello from session-3-simple-agent!")
    # Load environment variables from .env file
    load_dotenv()

    # Access your API key
    api_key = os.getenv("GEMINI_API_KEY")
    max_iterations = 3
    client = genai.Client(api_key=api_key)
    last_response = None
    iteration = 0
    iteration_response = []

    system_prompt = """You are a math agent solving problems in iterations. Respond with EXACTLY ONE of these formats:
    1. FUNCTION_CALL: python_function_name|input
    2. FINAL_ANSWER: [number]

    where python_function_name is one of the followin:
    1. strings_to_chars_to_int(string) It takes a word as input, and returns the ASCII INT values of characters in the word as a list
    2. int_list_to_exponential_sum(list) It takes a list of integers and returns the sum of exponentials of those integers
    3. fibonacci_numbers(int) It takes an integer, like 6, and returns first 6 integers in a fibonacci series as a list.
    DO NOT include multiple responses. Give ONE response at a time."""

    query= """Calculate the sum of exponentials of word "TSAI"""

    while iteration < max_iterations:
        print(f"\n--- Iteration {iteration + 1} ---")
        if last_response == None:
            current_query = query
        else:
            current_query = current_query + "\n\n" + " ".join(iteration_response)
            current_query = current_query + "  What should I do next?"

        # Get model's response
        prompt = f"{system_prompt}\n\nQuery: {current_query}"
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
        response_text = response.text.strip()
        print(f"LLM Response: {response_text}")

        
        if response_text.startswith("FUNCTION_CALL:"):
            response_text = response.text.strip()
            _, function_info = response_text.split(":", 1)
            func_name, params = [x.strip() for x in function_info.split("|", 1)]
            iteration_result = function_caller(func_name, params)

        # Check if it's the final answer
        elif response_text.startswith("FINAL_ANSWER:"):
            print("\n=== Agent Execution Complete ===")
            break
            

        print(f"  Result: {iteration_result}")
        last_response = iteration_result
        iteration_response.append(f"In the {iteration + 1} iteration you called {func_name} with {params} parameters, and the function returned {iteration_result}.")

        iteration += 1

if __name__ == "__main__":
    main()
