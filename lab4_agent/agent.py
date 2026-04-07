from typing import Annotated
from typing_extensions import TypedDict

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from tools import search_flights, search_hotels, calculate_budget

import os
load_dotenv()

# 1. Đọc system prompt
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "system_prompt.txt"), "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

# 2. Khai báo state
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# 3. Khởi tạo model và tools
tools_list = [search_flights, search_hotels, calculate_budget]

llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools_list)

# 4. Agent node
def agent_node(state: AgentState):
    messages = state["messages"]

    if not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    import time
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = llm_with_tools.invoke(messages)
            break
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Lỗi API OpenAI: {str(e)[:100]}. Đang retry lần {attempt + 1}...")
                time.sleep(2)
            else:
                raise e

    # logging
    if response.tool_calls:
        for tc in response.tool_calls:
            print(f"Gọi tool: {tc['name']}({tc['args']})")
    else:
        print("Trả lời trực tiếp")

    return {"messages": [response]}

# 5. Build graph
builder = StateGraph(AgentState)

builder.add_node("agent", agent_node)

tool_node = ToolNode(tools_list)
builder.add_node("tools", tool_node)

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")

graph = builder.compile()

# 6. Chat loop
if __name__ == "__main__":
    print("=" * 60)
    print("TravelBuddy — Trợ lý Du lịch Thông minh")
    print("Gõ 'quit' để thoát")
    print("=" * 60)

    while True:
        user_input = input("\nBạn: ").strip()

        if user_input.lower() in ("quit", "exit", "q"):
            break

        print("\nTravelBuddy đang suy nghĩ...")

        result = graph.invoke({"messages": [("human", user_input)]})
        final = result["messages"][-1]

        print(f"\nTravelBuddy: {final.content}")