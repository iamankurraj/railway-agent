#newwww
from app.state import AgentState
from app.tools.json_loader import load_json

def run(state: AgentState) -> AgentState:
    text = state.get("input", "").lower()
    params = state.get("params", {}) or {}

    # === Load fare dataset ===
    data = load_json("fares.json")["fares"]
    results = []

    class_type = None
    category = "general"  # default if not specified
    origin, destination = None, None

    # === Detect class type (1A, 2A, 3A, SL, 2S) ===
    for c in ["1a", "2a", "3a", "sl", "2s"]:
        if c in text:
            class_type = c.upper()

    # === Detect fare type ===
    if "tatkal" in text:
        category = "tatkal"
    elif "general" in text:
        category = "general"

    # === Extract origin/destination ===
    if "from" in text and "to" in text:
        parts = text.split("from")[1].strip().split("to")
        origin = parts[0].strip().upper()
        destination = parts[1].strip().upper()

    # === Filter fares ===
    for item in data:
        if origin and item.get("fromStationCode") != origin:
            continue
        if destination and item.get("toStationCode") != destination:
            continue

        fares = item["data"].get(category, [])
        for f in fares:
            if class_type and f["classType"] != class_type:
                continue

            results.append({
                "trainNo": item["trainNo"],
                "category": category.title(),
                "classType": f["classType"],
                "fare": f["fare"],
                "breakup": f["breakup"],
            })

    if not results:
        state.result = [{"info": "No matching fare data found for your query."}]
        return state

    state.result = results
    state.nl_output = f"Found {len(results)} {category} fare record(s)."
    return state
