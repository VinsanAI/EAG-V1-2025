from ast import arguments
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio

async def main():

    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            print("Connected to MCP Server")

            # Get the input from user
            inp_text = input("Enter the text to reverse: ")

            # Call the reverse_string tool
            result = await session.call_tool(
                "reverse_string",
                arguments={"text":inp_text}
            )

            # Parsing the result - accessing as object properties
            reversed_string = result.content[0].text

            print(f"Reversed String: {reversed_string}")

            result = await session.list_tools()
            print(result.tools)

if __name__ == "__main__":
    asyncio.run(main())
