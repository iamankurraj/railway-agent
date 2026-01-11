
print("USING FINALIZED input_node.py VERSION")

import re
from app.state import AgentState


def extract_params(user_input: str):
    user_input = user_input.lower().strip()
    origin, destination, class_name, min_price = None, None, None, None

    route_match = re.search(
        r"(?:from\s+)?([a-z]+)\s+(?:to|and)\s+([a-z]+)", user_input
    )
    if route_match:
        origin, destination = route_match.groups()
        origin, destination = origin.strip(), destination.strip()

    # Match train classes
    class_match = re.search(
        r"\b(ac\s?[123]?-?tier|ac\s?chair\s?car|sleeper|second\s?sitting)\b",
        user_input,
    )
    if class_match:
        class_name = class_match.group(1).replace("-", " ").strip()

    # Match price filters
    price_match = re.search(r"(?:above|over|greater\s?than)\s?(\d+)", user_input)
    if price_match:
        min_price = int(price_match.group(1))

    return {
        "origin": origin,
        "destination": destination,
        "class_name": class_name,
        "min_price": min_price,
    }


def run(state: AgentState) -> AgentState:
    text = getattr(state, "input", "") or ""
    if not text and "messages" in state.dict():
        text = state.dict()["messages"][-1].content

    text = text.strip()
    params = extract_params(text)
    print(f"⚙️ [DEBUG] Extracted params: {params}")

    # Determine if user wants to search trains or general info
    if any(kw in text for kw in ["train", "from", "to", "between"]):
        state.intent = "search_trains"
    else:
        state.intent = "general_query"

    state.params = params
    return state
