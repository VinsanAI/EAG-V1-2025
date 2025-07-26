from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
# import os
import math

# Creating the mcp server instance
mcp = FastMCP("Simple math solver")

@mcp.tool()
def strings_to_chars_to_int(string: str) -> list:
    """It takes a word as input, and returns the ASCII INT values of characters in the word as a list"""
    return [ord(char) for char in string]

@mcp.tool()
def int_list_to_exponential_sum(int_list: list) -> float:
    """It takes a list of integers and returns the sum of exponentials of those integers"""
    int_list = eval(int_list)
    return sum(math.exp(i) for i in int_list)

@mcp.tool()
def fibonacci_numbers(n: int) -> list:
    """It takes an integer, like 6, and returns first 6 integers in a fibonacci series as a list."""
    if n <= 0:
        return []
    fib_sequence = [0, 1]
    for _ in range(2, n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence[:n]

if __name__ == "__main__":
    print("Starting MCP Simple math solver Server...")
    mcp.run()