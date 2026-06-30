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

    print(f"Query -> intent={intent} origin={origin} dest={destination} "
          f"class={class_name} min={min_price} max={max_price}")

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
    # If user provided train_name or train_number, return matching train(s)
    params_train_name = params.get("train_name")
    params_train_number = params.get("train_number")
    if (params_train_name or params_train_number) and intent in SEARCH_INTENTS:
        data = load_json("trains.json")["trains"]
        matches = []
        for t in data:
            if params_train_number and str(params_train_number).lower() in str(t.get("train_id", "")).lower():
                matches.append(t)
                continue
            if params_train_name and params_train_name.lower() in (t.get("train_name", "").lower()):
                matches.append(t)

        if not matches:
            state.result = [{"info": ("🚫 Couldn't find that train in the dataset. Try full name or check spelling.") }]
            state.nl_output = "Train not found"
            return state

        # If multiple matches, prompt for disambiguation
        if len(matches) > 1:
            options = []
            for i, t in enumerate(matches[:50], start=1):
                options.append({
                    "index": i,
                    "train_id": t.get("train_id") or t.get("train_number"),
                    "train_name": t.get("train_name"),
                    "origin": t.get("origin"),
                    "destination": t.get("destination"),
                    "date": t.get("date"),
                    "departure_time": t.get("departure_time"),
                })

            state.result = [{
                "disambiguation": True,
                "prompt": f"I found {len(matches)} trains named '{params_train_name}'. Which one did you mean?",
                "options": options
            }]
            state.nl_output = "Disambiguation required"
            return state

        state.selected_train = matches[0] if len(matches) == 1 else None
        state.result = matches
        state.nl_output = f"Found {len(matches)} matching train(s) for '{params_train_name or params_train_number}'."
        return state

    if not origin and not destination and intent in SEARCH_INTENTS:
        state.result = [{"info": (
            "Please mention at least one city or station.\n\n"
            "Examples:\n"
            "➡️ *'Trains from Pune to Delhi'*\n"
            "➡️ *'Sleeper trains to Mumbai'*\n"
            "➡️ *'AC 2-tier trains from Chennai'"
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

    # If user asked for a specific class or price range, return class-level matches
    wants_class_level = bool(class_name) or (min_price is not None) or (max_price is not None)

    if wants_class_level:
        class_matches = []
        for t in results:
            for c in t.get("classes", []):
                price = c.get("price")
                cname = c.get("class_name", "")

                # apply class filter
                if class_name and class_name.lower() not in cname.lower():
                    continue

                # apply price filters
                if min_price is not None and (price is None or price < min_price):
                    continue
                if max_price is not None and (price is None or price > max_price):
                    continue

                class_matches.append({
                    "train_id": t.get("train_id") or t.get("train_number"),
                    "train_name": t.get("train_name"),
                    "origin": t.get("origin"),
                    "destination": t.get("destination"),
                    "date": t.get("date"),
                    "class_name": cname,
                    "price": price,
                    "seats_available": c.get("seats_available", 0),
                })

        # Limit for UI
        class_matches = class_matches[:50]

        if not class_matches:
            state.result = [{"info": (
                "🚫 No classes found matching your filters.\n\n"
                "Try relaxing the class or price filters."
            )}]
            state.nl_output = "No matching classes found."
            return state

        if len(class_matches) == 1:
            state.selected_train = class_matches[0]
        state.result = class_matches
        state.nl_output = f"Found {len(class_matches)} matching class(es)."
        return state

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