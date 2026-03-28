import json
import os
import re
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
    # Convert Pydantic model → dict for safe access
    state_dict = state.dict()

    messages = state_dict.get("messages", [])
    result = state_dict.get("result", [])
    nl_output = state_dict.get("nl_output", "")

    # Build a natural language response if not already provided
    if not nl_output:
        if not result:
            nl_output = "No results found for your query."
        elif isinstance(result, list):
            nl_output = f"Found {len(result)} matching item(s)."
        else:
            nl_output = "Got some results."

    # Dynamic LLM Translation for Multiple Languages (Translates JSON values and nl_output)
    lang = state_dict.get("lang", "en")
    lang_names = {"hi": "Hindi", "mr": "Marathi"}  # extend as needed
    
    if lang in lang_names and result:
        lang_label = lang_names[lang]
        try:
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            translation_prompt = (
                f"You are an expert translator. The user requested {lang_label}. "
                f"1. Translate the 'nl_output' string into {lang_label}.\n"
                f"2. Translate all string values (like city names, train names, classes, info messages) "
                f"inside the 'result' JSON array into {lang_label}. DO NOT translate the JSON keys.\n"
                "Return ONLY a valid JSON object with keys 'nl_output' and 'result'."
            )
            payload = json.dumps({"nl_output": nl_output, "result": result}, ensure_ascii=False)
            
            res = llm.invoke([
                SystemMessage(content=translation_prompt),
                HumanMessage(content=payload)
            ])
            match = re.search(r"\{.*\}", res.content, re.S)
            if match:
                translated = json.loads(match.group(0))
                nl_output = translated.get("nl_output", nl_output)
                result = translated.get("result", result)
        except Exception as e:
            print(f"Translation error: {e}")

    # Assign back to AgentState attributes
    state.nl_output = nl_output
    state.result = result
    return state