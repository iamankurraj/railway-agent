import json
from typing import Any, Dict, List
from app.state import AgentState
from app.tools.json_loader import load_json
from app.nodes import booking_node

BOOKING_KEYWORDS = {"book", "reserve", "confirm", "ticket", "booking", "seat", "reserve", "booked"}


def _find_matching_trains(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    data = load_json("trains.json")["trains"]
    train_name = params.get("train_name")
    train_number = params.get("train_number")
    origin = params.get("origin")
    destination = params.get("destination")
    class_name = params.get("class_name")

    matches = []
    for t in data:
        if train_number and str(train_number).lower() in str(t.get("train_id", "")).lower():
            matches.append(t)
            continue
        if train_name and train_name.lower() in (t.get("train_name", "").lower()):
            matches.append(t)
            continue
        if origin and destination:
            if t.get("origin", "").lower() == origin.lower() and t.get("destination", "").lower() == destination.lower():
                if class_name:
                    if any(class_name.lower() in c.get("class_name", "").lower() for c in t.get("classes", [])):
                        matches.append(t)
                else:
                    matches.append(t)

    return matches


def _redirect_to_disambiguation(state: AgentState, matches: List[Dict[str, Any]], name: str) -> AgentState:
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
        "prompt": f"I found {len(matches)} trains named '{name}'. Which one did you mean?",
        "options": options
    }]
    state.nl_output = "Disambiguation required"
    return state


def run(state: AgentState) -> AgentState:
    state_dict = state.dict()
    params = state_dict.get("params", {}) or {}
    selected_train = state_dict.get("selected_train")
    pending_booking = state_dict.get("pending_booking") or {}
    followup_stage = state_dict.get("followup_stage")

    # If we already know the train selection, keep it.
    if not selected_train:
        matches = _find_matching_trains(params)
        if not matches:
            state.result = [{"info": (
                "I couldn't find a train matching your booking request."
                " Please provide the train name, number, or route."
            )}]
            state.nl_output = "No matching train for booking"
            return state

        if len(matches) > 1:
            return _redirect_to_disambiguation(state, matches, params.get("train_name") or params.get("train_number") or "this train")

        selected_train = matches[0]
        state.selected_train = selected_train

    booking_data = {
        "train_id": selected_train.get("train_id") or selected_train.get("train_number"),
        "train_name": selected_train.get("train_name"),
        "date": params.get("date"),
        "class_name": params.get("class_name"),
        "passenger_name": params.get("passenger_name") or "Passenger"
    }

    # Default to class if only one class option exists
    if not booking_data["class_name"]:
        classes = selected_train.get("classes", [])
        if len(classes) == 1:
            booking_data["class_name"] = classes[0].get("class_name")

    missing = [k for k in ["class_name", "date", "passenger_name"] if not booking_data.get(k)]
    if missing:
        field = missing[0]
        state.pending_booking = booking_data
        state.followup_stage = field
        prompt_map = {
            "class_name": "Which class would you like to book?",
            "date": "For which date should I reserve this ticket?",
            "passenger_name": "What passenger name should I use for the booking?"
        }
        state.result = [{"info": prompt_map.get(field, "Please provide the missing booking details.") }]
        state.nl_output = f"Asked for {field}"
        return state

    # If user confirms and everything is present, create the booking
    try:
        booking = booking_node.create_booking(
            booking_data["train_id"],
            booking_data["train_name"],
            booking_data["date"],
            booking_data["class_name"],
            booking_data["passenger_name"]
        )
        state.result = {"booking": booking}
        state.nl_output = f"Booking confirmed for {booking_data['train_name']}"
        state.pending_booking = None
        state.followup_stage = None
        return state
    except Exception as e:
        state.result = [{"info": f"Could not complete booking: {str(e)}"}]
        state.nl_output = "Booking failed"
        return state
