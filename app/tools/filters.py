from typing import Any, Dict, List, Optional
import re

def _to_lower(s: Optional[str]) -> str:
    return (s or "").strip().lower()

def trains_between(data, origin, destination):
    return [
        t for t in data
        if t["origin"].lower() == origin.lower() and t["destination"].lower() == destination.lower()
    ]

def filter_by_class_name(data, class_name):
    return [
        t for t in data
        if any(class_name.lower() in c["class_name"].lower() for c in t["classes"])
    ]

def filter_by_min_price(data, min_price):
    return [
        t for t in data
        if any(c["price"] >= min_price for c in t["classes"])
    ]
