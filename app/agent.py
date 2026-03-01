from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from app.state import AgentState
from app.nodes import input_node, llm_node, query_node, response_node   # 🧠 added llm_node
from app.audio_search import listen_once
def build_graph():
    graph = StateGraph(AgentState)

    # Register nodes
    graph.add_node("input", input_node.run)
    graph.add_node("llm", llm_node.run)            
    graph.add_node("query", query_node.run)
    graph.add_node("respond", response_node.run)

    # Define flow
    graph.set_entry_point("input")
    graph.add_edge("input", "llm")                 
    graph.add_edge("llm", "query")                 
    graph.add_edge("query", "respond")
    graph.add_edge("respond", END)

    return graph.compile()

app = build_graph()

# Optional: visualizing flow
# mermaid_png = app.get_graph().draw_mermaid_png()
# with open("graph.png", "wb") as f:
#     f.write(mermaid_png)
# print("Graph image saved as 'graph.png' (open it to view).")

def invoke_text(user_text: str) -> str:
    init: AgentState = {"messages": [HumanMessage(content=user_text)]}
    out = app.invoke(init)
    return out.get("nl_output", "")

def invoke_speech() -> str:
    spoken_text = listen_once()
    print("🎙 You said:", spoken_text)
    return invoke_text(spoken_text)