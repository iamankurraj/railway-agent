import json
import uuid
from datetime import datetime
from pathlib import Path
from app.utils import get_base_dir


DATA_DIR = get_base_dir() / "data"
BOOKINGS_PATH = DATA_DIR / "bookings.json"
TRAINS_PATH = DATA_DIR / "trains.json"


def _ensure_bookings_file():
    if not BOOKINGS_PATH.exists():
        with open(BOOKINGS_PATH, "w", encoding="utf-8") as f:
            json.dump({"bookings": []}, f, indent=2)


def _load_bookings():
    _ensure_bookings_file()
    with open(BOOKINGS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_bookings(data):
    with open(BOOKINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def generate_pnr() -> str:
    return uuid.uuid4().hex[:10].upper()


def create_booking(train_id: str, train_name: str, date: str, class_name: str, passenger_name: str = "Passenger") -> dict:
    # Load trains to find class price and update seats
    if not TRAINS_PATH.exists():
        raise ValueError("Trains data not available")

    with open(TRAINS_PATH, "r", encoding="utf-8") as f:
        trains_data = json.load(f)
    trains = trains_data.get("trains", trains_data)

    # find train by train_id or train_no
    matched = None
    for t in trains:
        if str(t.get("train_id", "")).lower() == str(train_id).lower() or str(t.get("train_id", "")).endswith(train_id):
            matched = t
            break

    if not matched:
        raise ValueError("Train not found")

    # find class
    cls = None
    for c in matched.get("classes", []):
        if c.get("class_name", "").lower() == class_name.lower() or class_name.lower() in c.get("class_name", "").lower():
            cls = c
            break

    if not cls:
        raise ValueError("Class not found on selected train")

    seats = int(cls.get("seats_available", 0) or 0)
    if seats <= 0:
        raise ValueError("No seats available in selected class")

    # decrement one seat
    cls["seats_available"] = seats - 1

    # save updated trains data back to file
    # preserve original structure if top-level key was 'trains'
    if isinstance(trains_data, dict) and "trains" in trains_data:
        trains_data["trains"] = trains
    else:
        trains_data = trains

    with open(TRAINS_PATH, "w", encoding="utf-8") as f:
        json.dump(trains_data, f, indent=2, ensure_ascii=False)

    bookings = _load_bookings()
    pnr = generate_pnr()
    now = datetime.utcnow().isoformat() + "Z"
    record = {
        "pnr": pnr,
        "train_id": train_id,
        "train_name": train_name,
        "date": date,
        "class": class_name,
        "price": int(cls.get("price", 0) or 0),
        "passenger": passenger_name,
        "created_at": now
    }
    bookings.setdefault("bookings", []).append(record)
    _save_bookings(bookings)
    return record


def get_booking(pnr: str) -> dict | None:
    bookings = _load_bookings()
    for b in bookings.get("bookings", []):
        if b.get("pnr") == pnr:
            return b
    return None
