# app/nodes/input_node.py
import re
from app.state import AgentState
from app.tools.json_loader import load_json

print("USING UPDATED input_node.py")

# Known city/station names to help with multi-word matching
KNOWN_CITIES = [
    "new delhi", "old delhi", "delhi", "mumbai", "pune", "chennai", "kolkata",
    "bangalore", "bengaluru", "hyderabad", "ahmedabad", "jaipur", "lucknow",
    "kanpur", "nagpur", "surat", "bhopal", "patna", "indore", "vadodara",
    "coimbatore", "agra", "varanasi", "goa", "mangalore", "mysore",
    "visakhapatnam", "vijayawada", "chandigarh", "amritsar", "jodhpur",
    "kochi", "thiruvananthapuram", "guwahati", "bhubaneswar"
]

def extract_params(user_input: str) -> dict:
    text = user_input.lower().strip()
    origin, destination, class_name, min_price, max_price, date, passenger_name = None, None, None, None, None, None, None

    # Try to detect train name/number from dataset if present
    train_name = None
    train_number = None
    try:
        data = load_json("trains.json")
        trains = data.get("trains", data) if isinstance(data, dict) else data
        # build simple mapping of lowercase train names to canonical names and numbers
        name_map = {}
        for t in trains:
            tn = (t.get("train_name") or "").lower()
            if tn:
                name_map[tn] = t
            # also index by id/number
            tid = str(t.get("train_id") or "")
            if tid:
                name_map[tid.lower()] = t

        for key in name_map:
            if key in text:
                train_name = name_map[key].get("train_name")
                train_number = name_map[key].get("train_id") or name_map[key].get("train_number")
                break
    except Exception:
        # dataset may be missing — ignore
        train_name = None
        train_number = None

    # ── Route extraction ──────────────────────────────────────────────────────
    # Try known multi-word cities first
    from_match, to_match = None, None

    # Build pattern with known cities (longest match wins)
    city_pattern = "|".join(re.escape(c) for c in sorted(KNOWN_CITIES, key=len, reverse=True))

    # "from X to Y" with known cities
    route_known = re.search(
        rf"(?:from\s+)({city_pattern})\s+(?:to|and)\s+({city_pattern})", text
    )
    if route_known:
        origin, destination = route_known.group(1), route_known.group(2)
    else:
        # Fallback: generic word-based extraction
        route_generic = re.search(
            r"(?:from\s+)([\w\s]+?)\s+(?:to|and)\s+([\w]+)", text
        )
        if route_generic:
            origin = route_generic.group(1).strip()
            destination = route_generic.group(2).strip()

    # "trains to X" (destination only)
    if not destination:
        to_only = re.search(r"\bto\s+([\w\s]+?)(?:\s+trains?|$|\?)", text)
        if to_only:
            destination = to_only.group(1).strip()

    # "trains from X" (origin only)
    if not origin:
        from_only = re.search(r"\bfrom\s+([\w\s]+?)(?:\s+trains?|$|\?)", text)
        if from_only:
            origin = from_only.group(1).strip()

    # ── Class extraction ──────────────────────────────────────────────────────
    class_match = re.search(
        r"\b(ac\s?1\s?-?\s?tier|ac\s?2\s?-?\s?tier|ac\s?3\s?-?\s?tier"
        r"|ac\s?chair\s?car|second\s?sitting|sleeper)\b",
        text,
    )
    if class_match:
        class_name = re.sub(r"\s+", " ", class_match.group(1).replace("-", " ")).strip()

    # ── Price extraction ──────────────────────────────────────────────────────
    min_match = re.search(r"(?:above|over|more\s+than|greater\s+than)\s*[₹rs\.]?\s*(\d+)", text)
    if min_match:
        min_price = int(min_match.group(1))

    max_match = re.search(r"(?:below|under|less\s+than|cheaper\s+than|within)\s*[₹rs\.]?\s*(\d+)", text)
    if max_match:
        max_price = int(max_match.group(1))

    # ── Date extraction ──────────────────────────────────────────────────────
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", text)
    if date_match:
        date = date_match.group(1)
    elif "today" in text:
        date = "today"
    elif "tomorrow" in text:
        date = "tomorrow"

    # ── Passenger name extraction ─────────────────────────────────────────────
    passenger_match = re.search(r"\bfor\s+([a-z]+(?:\s+[a-z]+){0,2})\b", text)
    if passenger_match:
        passenger_name = passenger_match.group(1).title()

    return {
        "origin": origin,
        "destination": destination,
        "class_name": class_name,
        "min_price": min_price,
        "max_price": max_price,
        "date": date,
        "train_name": train_name,
        "train_number": train_number,
        "passenger_name": passenger_name,
    }


def run(state: AgentState) -> AgentState:
    # Pull text from input field or last message
    text = getattr(state, "input", "") or ""
    if not text:
        msgs = state.dict().get("messages", [])
        if msgs:
            text = msgs[-1].content

    text = text.strip()
    params = extract_params(text)
    print(f"[input_node] Extracted params: {params}")

    state_dict = state.dict()
    selected_train = state_dict.get("selected_train")
    followup_stage = state_dict.get("followup_stage")

    booking_keywords = ["book", "reserve", "confirm", "ticket", "booking", "seat", "reserved", "booked"]
    railway_keywords = [
        "train", "trains", "from", "to", "between", "depart", "arrive",
        "ticket", "fare", "class", "sleeper", "ac", "seat", "route",
        "book", "schedule", "timing", "coach", "station"
    ]
    has_railway_kw = any(kw in text.lower() for kw in railway_keywords)
    wants_booking = any(kw in text.lower() for kw in booking_keywords)

    if selected_train or followup_stage:
        state.intent = state.intent or "book_train"
    elif wants_booking and (params.get("train_name") or params.get("train_number") or params.get("origin") or params.get("destination")):
        state.intent = "book_train"
    elif has_railway_kw:
        state.intent = "search_trains"
    else:
        state.intent = "general_info"

    state.params = params
    return state