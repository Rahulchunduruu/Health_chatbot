from typing import cast
from pydantic import SecretStr
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.checkpoint.memory import MemorySaver
from config import Config
from tools import tools_list
from prompt import prompt1, prompt2

# ── LLM ──────────────────────────────────────────────
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=SecretStr(Config.Groq_api_key)
)
llm_with_tools = llm.bind_tools(tools_list)

# ── Nodes ─────────────────────────────────────────────
def agent(state: MessagesState):
    """Main agent — decides tool calls or final answer"""
    messages = [SystemMessage(content=prompt1.replace("{query}", ""))] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def summarizer(state: MessagesState):
    """Runs after all tool loops complete — clean final response"""
    messages = [SystemMessage(content=prompt2)] + state["messages"]
    response = llm.invoke(messages)  # plain llm — no tools
    return {"messages": [response]}


# ── Routing ───────────────────────────────────────────
def route_agent(state: MessagesState):
    """
    tools_condition checks last AI message:
    - has tool_calls → 'tools'
    - no tool_calls  → 'summarizer'
    """
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and getattr(last, "tool_calls", None):
        return "tools"
    return "summarizer"


# ── Graph ─────────────────────────────────────────────
checkpointer = MemorySaver()

graph = StateGraph(MessagesState)

graph.add_node("agent", agent)
graph.add_node("tools", ToolNode(tools_list))
graph.add_node("summarizer", summarizer)

graph.set_entry_point("agent")

# agent → tools OR summarizer
graph.add_conditional_edges(
    "agent",
    route_agent,
    {
        "tools": "tools",
        "summarizer": "summarizer"
    }
)

# tools → agent (loop for chaining)
graph.add_edge("tools", "agent")

# summarizer → END
graph.add_edge("summarizer", END)

chat_workflow = graph.compile(checkpointer=checkpointer)


# ── Main Loop ─────────────────────────────────────────
if __name__ == "__main__":
    configs = cast(RunnableConfig, {"configurable": {"thread_id": "rahul_session"}})
    print("HealthBot ready. Type 'quit' to exit.")
    try:
        while True:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue
            if user_input.lower() == "quit":
                break

            result = chat_workflow.invoke(
                {"messages": [HumanMessage(content=user_input)]},
                configs
            )
            print(f"\nHealthBot: {result['messages'][-1].content}")

    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error: {e}")