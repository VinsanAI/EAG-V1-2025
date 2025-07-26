from ast import arguments
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
from pdb import set_trace
import code

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
            
            tools_result = await session.list_tools()
            tools = tools_result.tools
            print(tools)

            code.interact(local=locals())
            print("Something")

if __name__ == "__main__":
    asyncio.run(main())