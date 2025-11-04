import asyncio
import time
import os
import datetime
from pathlib import Path
from perception import extract_perception
from memory import MemoryManager, MemoryItem
# from decision import generate_plan
# from action import execute_tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
 # use this to connect to running server

import shutil
import sys
from pdb import set_trace

def log(stage: str, msg: str):
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] [{stage}] {msg}")

max_steps = 3
ROOT = Path(__file__).parent.resolve()
# ROOT = "/Volumes/SSD-Santosh/Santosh Code Files/EAG-V1-2025/Session 7 - FAISS-and-Advanced-RAG/Advanced-RAG-E2E"

async def main(user_input: str):
    try:
        print("[agent] Starting agent...")
        print(f"[agent] Current working directory: {os.getcwd()}")
        
        server_params = StdioServerParameters(
            command="python",
            args=["tools_mcp_server.py"],
            cwd=str(ROOT)
        )

        try:
            async with stdio_client(server_params) as (read, write):
                print("Connection established, creating session...")
                try:
                    async with ClientSession(read, write) as session:
                        print("[agent] Session created, initializing...")
 
                        try:
                            await session.initialize()
                            print("[agent] MCP session initialized")

                            # Your reasoning, planning, perception etc. would go here
                            tools = await session.list_tools()
                            print("Available tools:", [t.name for t in tools.tools])

                            # Get available tools
                            print("Requesting tool list...")
                            tools_result = await session.list_tools()
                            tools = tools_result.tools
                            tool_descriptions = "\n".join(
                                f"- {tool.name}: {getattr(tool, 'description', 'No description')}" 
                                for tool in tools
                            )
                            print(tool_descriptions)

                            log("agent", f"{len(tools)} tools loaded")

                            memory = MemoryManager()
                            session_id = f"session-{int(time.time())}"
                            query = user_input  # Store original intent
                            step = 0

                            synthetic_memories = [
                                MemoryItem(
                                    text="The distribution list for the internal Data Science team is 'data-science-team@vinsan-ai.com'.",
                                    type="preference",
                                    tags=["scheduling", "datascience", "info"],
                                    session_id="00000" # General system preference
                                ),
                                MemoryItem(
                                    text="The user prefers all internal meetings to be scheduled between 9:30 AM and 11:30 AM IST to accommodate early-morning priorities.",
                                    type="preference",
                                    tags=["scheduling", "availability"],
                                    session_id="00000"
                                ),
                                MemoryItem(
                                    text="TOOL_CALL: 'get_agent_metrics' returned key finding: 'Agent-AHT increased by 20% in the last 72 hours, potentially due to new CRM patch deployment.'",
                                    type="tool_output",
                                    tool_name="get_agent_metrics",
                                    tags=["agents", "performance", "recent"],
                                    session_id="98765" # A recent, related session
                                ),
                                MemoryItem(
                                    text="The current priority of the customer service director is to resolve the spike in Average Handle Time (AHT) which is impacting customer satisfaction (CSAT).",
                                    type="fact",
                                    tags=["priority", "customer-service", "urgency"],
                                    session_id="00000"
                                ),
                                MemoryItem(
                                    text="For analysis-focused meetings, the user generally prefers a meeting duration of 45 minutes to maintain focus.",
                                    type="preference",
                                    tags=["scheduling", "duration"],
                                    session_id="00000"
                                ),
                                MemoryItem(
                                    text="The company phased out the 'Bronze Tier' billing package for all new customers as of Q2 2024.",
                                    type="fact",
                                    tags=["billing", "legacy"],
                                    session_id="00000"
                                ),
                                MemoryItem(
                                    text="The user requires all travel bookings to prioritize non-stop flights and use the 'Premium Economy' fare class.",
                                    type="preference",
                                    tags=["travel", "expense"],
                                    session_id="00000"
                                ),
                                MemoryItem(
                                    text="We currently have a surplus stock of 'Model X-23' routers due to a recent supplier overshipment.",
                                    type="fact",
                                    tags=["hardware", "inventory"],
                                    session_id="77777"
                                ),
                                MemoryItem(
                                    text="If a meeting extends past 12:30 PM, the user prefers a vegetarian option for lunch to be provided.",
                                    type="preference",
                                    tags=["lunch", "meeting"],
                                    session_id="00000"
                                ),
                                MemoryItem(
                                    text="All internal documentation regarding customer data must be reviewed by the Legal team before external publication.",
                                    type="fact",
                                    tags=["legal", "compliance"],
                                    session_id="00000"
                                ),
                            ]
                            
                            memory.bulk_add(synthetic_memories)
                            print(f"Successfully add all synthetic memories: {len(memory.data)}")

                            perception = extract_perception(user_input)
                            log("perception", f"Intent: {perception.intent}, Tool hint: {perception.tool_hint}")

                            retrieved = memory.retrieve(query=user_input, top_k=3, type_filter="preference")
                            log("memory", f"Retrieved {len(retrieved)} relevant memories")

                            if retrieved:
                                for i, item in enumerate(retrieved):
                                    print(f"  Result {i+1}:")
                                    print(f"    Text: {item.text}")
                                    print(f"    Type: {item.type}, Tags: {item.tags}, Session: {item.session_id}")
                            else:
                                print("  No results found.")

                            # while step < max_steps:
                            #     log("loop", f"Step {step + 1} started")

                            #     perception = extract_perception(user_input)
                            #     log("perception", f"Intent: {perception.intent}, Tool hint: {perception.tool_hint}")

                            #     retrieved = memory.retrieve(query=user_input, top_k=3, session_filter=session_id)
                            #     log("memory", f"Retrieved {len(retrieved)} relevant memories")

                            #     plan = generate_plan(perception, retrieved, tool_descriptions=tool_descriptions)
                            #     log("plan", f"Plan generated: {plan}")

                            #     if plan.startswith("FINAL_ANSWER:"):
                            #         log("agent", f"✅ FINAL RESULT: {plan}")
                            #         break

                            #     try:
                            #         result = await execute_tool(session, tools, plan)
                            #         log("tool", f"{result.tool_name} returned: {result.result}")

                            #         memory.add(MemoryItem(
                            #             text=f"Tool call: {result.tool_name} with {result.arguments}, got: {result.result}",
                            #             type="tool_output",
                            #             tool_name=result.tool_name,
                            #             user_query=user_input,
                            #             tags=[result.tool_name],
                            #             session_id=session_id
                            #         ))

                            #         user_input = f"Original task: {query}\nPrevious output: {result.result}\nWhat should I do next?"

                            #     except Exception as e:
                            #         log("error", f"Tool execution failed: {e}")
                            #         break

                                # step += 1
                        except Exception as e:
                            print(f"[agent] Session initialization error: {str(e)}")
                except Exception as e:
                    print(f"[agent] Session creation error: {str(e)}")
        except Exception as e:
            print(f"[agent] Connection error: {str(e)}")
    except Exception as e:
        print(f"[agent] Overall error: {str(e)}")

    log("agent", "Agent session complete.")

if __name__ == "__main__":
    query = input("🧑 What do you want to solve today? → ")
    asyncio.run(main(query))