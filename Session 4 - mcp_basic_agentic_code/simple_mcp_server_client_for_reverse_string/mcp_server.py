from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

# Creating the mcp server instance
mcp = FastMCP("Text Reverser")

@mcp.tool()
async def reverse_string(text: str) -> dict:
    """"Reverse the input text"""
    return {
        "content": [
            TextContent(
                type="text",
                text=text[::-1]
            )
        ]
    }

if __name__ == "__main__":
    print("Starting MCP Text Reverser Server...")
    mcp.run()