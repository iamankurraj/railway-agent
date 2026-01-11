import json
import os
from typing import Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.state import AgentState
from app.prompts import SYSTEM_SUMMARY, USER_SUMMARY_TEMPLATE

def _summarize_locally(user_query: str, data: Any) -> str:
    if isinstance(data, list):
        n = len(data)
        preview = data[:5]
        return f"Found {n} item(s).\n" + "\n".join(f"- {json.dumps(x, ensure_ascii=False)}" for x in preview)
    return json.dumps(data, ensure_ascii=False, indent=2)

def run(state: AgentState) -> AgentState:
    # 🩹 Convert Pydantic model → dict for safe access
    state_dict = state.dict()

    messages = state_dict.get("messages", [])
    result = state_dict.get("result", [])
    nl_output = state_dict.get("nl_output", "")

    # 🧠 Build a natural language response if not already provided
    if not nl_output:
        if not result:
            nl_output = "No results found for your query."
        elif isinstance(result, list):
            nl_output = f"Found {len(result)} matching item(s)."
        else:
            nl_output = "Got some results."

    # ✅ Assign back to AgentState attributes (not dict indexing)
    state.nl_output = nl_output
    state.result = result
    return state