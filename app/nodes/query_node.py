from typing import Any, Dict
from app.state import AgentState
from app.tools.json_loader import load_json
from app.tools.filters import trains_between, filter_by_min_price, filter_by_class_name


def run(state: AgentState) -> AgentState:
    # Convert Pydantic model -> normal dict for safe access
    state_dict = state.dict()

    # Extract intent and params safely
    intent = state_dict.get("intent", "search_trains")
    params: Dict[str, Any] = state_dict.get("params", {}) or {}

    origin = params.get("origin")
    destination = params.get("destination")
    class_name = params.get("class_name")
    min_price = params.get("min_price")

    print(f"Params → Origin: {origin}, Dest: {destination}, Class: {class_name}, MinPrice: {min_price}")

    # Load JSON dataset
    data = load_json("trains.json")["trains"]

    # 🧠 1️⃣ Handle General "Introduction" Queries
    if intent == "general_query":
        state.result = [{
            "info": (
                "To overcome traditional data access challenges, the **Smart Railway Query System** "
                "introduces an intelligent solution capable of understanding natural, human-like queries. "
                "Instead of typing rigid commands such as *'Trains between Pune and Mumbai on 5th November'*, "
                "you can simply ask things like:\n\n"
                "🚆 *'Show me trains from Pune to Mumbai tomorrow morning.'*\n"
                "🕓 *'Find AC 2-tier trains from Delhi to Jaipur.'*\n"
                "💰 *'List trains above 2000 rupees.'*\n\n"
                "This system interprets your question and provides structured, accurate, and context-aware results — "
                "making travel information smarter and easier to access."
            )
        }]
        state.nl_output = "Displayed introduction message."
        return state

    # Block Unknown / Irrelevant Queries
    if intent not in ["search_trains", "get_train_details"]:
        state.result = [{
            "info": (
                "🤖 I’m your **Smart Railway Assistant!** I can help you find trains, routes, and fares — "
                "but I’m not built for general questions or math yet.\n\n"
                "Try asking me:\n"
                "🚆 'Trains from Pune to Mumbai'\n"
                "💺 'Find AC 3-tier trains above 2000'\n"
                "💰 'Show sleeper trains to Delhi'"
            )
        }]
        state.nl_output = "Out-of-domain query handled."
        return state

    # Missing route info check
    if not origin and not destination:
        state.result = [{
            "info": (
                "Please specify at least one route.\n\n"
                "Example queries:\n"
                "➡️ 'Show me trains from Pune to Delhi'\n"
                "➡️ 'Find trains to Mumbai'\n"
            )
        }]
        state.nl_output = "Route missing warning displayed."
        return state

    # Apply filters
    results = data
    if origin and destination:
        results = trains_between(results, origin, destination)
    if class_name:
        results = filter_by_class_name(results, class_name)
    if min_price:
        results = filter_by_min_price(results, min_price)

    # Limit results to 10 for UI sanity
    results = results[:10]

    # Handle no results case
    if not results:
        state.result = [{
            "info": "🚫 No trains found matching your filters."
        }]
        state.nl_output = "No trains found."
        return state

    # Assign results to AgentState
    state.result = results
    state.nl_output = (
        f"Found {len(results)} train(s)"
        + (f" from {origin} to {destination}" if origin and destination else "")
        + (f" in class {class_name}" if class_name else "")
        + (f" above {min_price} INR" if min_price else "")
        + "."
    )

    return state
