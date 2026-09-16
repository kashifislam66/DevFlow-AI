import os
from dotenv import load_dotenv
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
    max_tokens=500
)


async def main():
    # Initialize the MCP client.
    client = MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "args": ["src/devflow/mcp_servers/math_server.py"],  # Sahi path confirm kar lein
                "transport": "stdio",
            }
        }
    )

    # Load tools from the MCP server.
    tools = await client.get_tools()

    # Bind the tools to the LLM.
    llm_with_tools = llm.bind_tools(tools)

    # Define the agent node that calls the LLM.
    async def agent_node(state: MessagesState):
        response = await llm_with_tools.ainvoke(state["messages"])
        return {"messages": [response]}

    # Initialize the tool node and graph builder.
    tool_node = ToolNode(tools)
    builder = StateGraph(MessagesState)

    # Add nodes.
    builder.add_node("agent", agent_node)
    builder.add_node("tools", tool_node)

    # Configure ReAct graph edges.
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")

    # Compile the graph.
    graph = builder.compile()

    # Run a simple asynchronous test.
    initial_input = {"messages": [HumanMessage(content="What is 12 multiplied by 8?")]}
    result = await graph.ainvoke(initial_input)

    # Print the final output.
    print("\n--- Final Answer ---")
    print(result["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())
