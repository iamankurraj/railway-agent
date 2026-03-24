# app/nodes/query_node.py
from typing import Any, Dict
from app.state import AgentState
from app.tools.json_loader import load_json
from app.tools.filters import trains_between, filter_by_min_price, filter_by_class_name

# All intents that should trigger a train search
SEARCH_INTENTS = {
    "search_trains",
    "get_train_details",
    "price_query",
    "schedule_query",
    "availability_check",
    "route_info",
}

def run(state: AgentState) -> AgentState:
    state_dict = state.dict()
    intent = state_dict.get("intent", "search_trains")
    params: Dict[str, Any] = state_dict.get("params", {}) or {}

    origin      = params.get("origin")
    destination = params.get("destination")
    class_name  = params.get("class_name")
    min_price   = params.get("min_price")
    max_price   = params.get("max_price")

    print(f"🔍 Query → intent={intent} origin={origin} dest={destination} "
          f"class={class_name} min₹={min_price} max₹={max_price}")

    # ── General info / help ──────────────────────────────────────────────────
    if intent == "general_info":
        state.result = [{"info": (
            "Welcome to the **Smart Railway Query System!** 🚄\n\n"
            "You can ask me things like:\n"
            "🚆 *'Show trains from Pune to Mumbai'*\n"
            "💺 *'Find AC 2-tier trains above ₹1000'*\n"
            "🕓 *'When does the Deccan Queen depart?'*\n"
            "💰 *'What is the sleeper fare from Delhi to Jaipur?'*\n"
            "🗺️ *'Which trains go from Mumbai to Goa?'*\n\n"
            "Just ask naturally — I'll understand!"
        )}]
        state.nl_output = "Displayed help message."
        return state

    # ── Truly out-of-domain ──────────────────────────────────────────────────
    if intent == "out_of_domain":
        state.result = [{"info": (
            "🤖 I'm your **Smart Railway Assistant** — I specialise in trains!\n\n"
            "I can help with:\n"
            "🚆 Finding trains between cities\n"
            "💰 Fare and class information\n"
            "🕓 Departure and arrival timings\n"
            "💺 Seat availability\n\n"
            "Try: *'Trains from Pune to Mumbai'* or *'Sleeper class to Delhi'*"
        )}]
        state.nl_output = "Out-of-domain query handled."
        return state

    # ── All railway-related intents → search ─────────────────────────────────
    # If we have no route info at all, ask the user to be more specific
    if not origin and not destination and intent in SEARCH_INTENTS:
        state.result = [{"info": (
            "Please mention at least one city or station.\n\n"
            "Examples:\n"
            "➡️ *'Trains from Pune to Delhi'*\n"
            "➡️ *'Sleeper trains to Mumbai'*\n"
            "➡️ *'AC 2-tier trains from Chennai'*"
        )}]
        state.nl_output = "Route missing — asked user to specify."
        return state

    # Load dataset
    data = load_json("trains.json")["trains"]
    results = data

    # Apply filters — each is optional
    if origin and destination:
        results = trains_between(results, origin, destination)
    elif origin:
        # Only origin given — filter loosely
        results = [t for t in results if t.get("origin", "").lower() == origin.lower()]
    elif destination:
        # Only destination given — filter loosely
        results = [t for t in results if t.get("destination", "").lower() == destination.lower()]

    if class_name:
        results = filter_by_class_name(results, class_name)

    if min_price is not None:
        results = filter_by_min_price(results, min_price)

    # max_price filter (new — didn't exist before)
    if max_price is not None:
        results = [
            t for t in results
            if any(c["price"] <= max_price for c in t.get("classes", []))
        ]

    # Limit for UI
    results = results[:10]

    if not results:
        state.result = [{"info": (
            "🚫 No trains found matching your filters.\n\n"
            "Try relaxing your search:\n"
            "• Remove the class filter\n"
            "• Remove the price filter\n"
            "• Check the city spelling"
        )}]
        state.nl_output = "No trains found."
        return state

    state.result = results
    state.nl_output = (
        f"Found {len(results)} train(s)"
        + (f" from {origin} to {destination}" if origin and destination
           else f" from {origin}" if origin
           else f" to {destination}" if destination
           else "")
        + (f" · {class_name}" if class_name else "")
        + (f" · above ₹{min_price}" if min_price else "")
        + (f" · below ₹{max_price}" if max_price else "")
        + "."
    )
    return state