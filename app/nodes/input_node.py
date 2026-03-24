# app/nodes/input_node.py
import re
from app.state import AgentState

print("USING UPDATED input_node.py")

# Known city/station names to help with multi-word matching
# Add more as needed for your dataset
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
    origin, destination, class_name, min_price, max_price = None, None, None, None, None

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

    return {
        "origin": origin,
        "destination": destination,
        "class_name": class_name,
        "min_price": min_price,
        "max_price": max_price,
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
    print(f"⚙️ [input_node] Extracted params: {params}")

    # Set a lightweight intent hint — LLM node will refine this
    # We only do a rough split here; the LLM has the final say
    railway_keywords = [
        "train", "trains", "from", "to", "between", "depart", "arrive",
        "ticket", "fare", "class", "sleeper", "ac", "seat", "route",
        "book", "schedule", "timing", "coach", "station"
    ]
    has_railway_kw = any(kw in text.lower() for kw in railway_keywords)
    state.intent = "search_trains" if has_railway_kw else "general_info"

    state.params = params
    return state