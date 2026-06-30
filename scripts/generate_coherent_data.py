import json
from pathlib import Path
import re

BASE = Path(__file__).resolve().parents[1] / "data"
BASE.mkdir(parents=True, exist_ok=True)

trains_path = BASE / "trains.json"
if not trains_path.exists():
    raise SystemExit("trains.json not found in data/")

with open(trains_path, "r", encoding="utf-8") as f:
    trains = json.load(f).get("trains", [])

# Normalize dates to the requested demo date
DEMO_DATE = "2026-07-01"
for t in trains:
    t["date"] = DEMO_DATE

# Write back updated trains.json so app uses latest date
with open(trains_path, "w", encoding="utf-8") as f:
    json.dump({"trains": trains}, f, indent=2, ensure_ascii=False)

# simple mapping for station codes: take first 3 consonants/letters uppercase
def code_for(name):
    s = re.sub(r"[^A-Za-z]", "", (name or "")).upper()
    if len(s) >= 3:
        return s[:3]
    return (s + 'XXX')[:3]

# map class_name to classType
def map_class(cn):
    cn_l = cn.lower()
    if "1-tier" in cn_l or "1 tier" in cn_l or "ac 1" in cn_l:
        return "1A"
    if "2-tier" in cn_l or "2 tier" in cn_l or "ac 2" in cn_l:
        return "2A"
    if "3-tier" in cn_l or "3 tier" in cn_l or "ac 3" in cn_l:
        return "3A"
    if "sleeper" in cn_l or cn_l == "sl":
        return "SL"
    if "second" in cn_l or cn_l == "2s":
        return "2S"
    if "chair" in cn_l or "cc" in cn_l:
        return "CC"
    return "GN"

getfare = {"fares": []}
searchtrain = {"status": True, "message": "Generated", "timestamp": 0, "data": []}

for t in trains:
    tid = t.get("train_id", "")
    # numeric train number fallback
    nums = re.sub(r"[^0-9]", "", tid)
    train_no = nums if nums else str(abs(hash(tid)) % 90000 + 10000)

    src = t.get("origin", "").upper()
    dst = t.get("destination", "").upper()

    # build fare entry
    fares_entry = {
        "trainNo": train_no,
        "fromStationCode": code_for(src),
        "toStationCode": code_for(dst),
        "status": True,
        "message": "Success",
        "timestamp": 0,
        "data": {"general": [], "tatkal": []},
    }

    for c in t.get("classes", []):
        class_name = c.get("class_name", ""); price = int(c.get("price", 0))
        class_code = map_class(class_name)
        base = max(1, int(price * 0.9))
        res_charges = max(10, int(price * 0.02))
        gst = int(price * 0.02)
        general_item = {
            "classType": class_code,
            "fare": price,
            "breakup": [
                {"title": "Base Charges", "key": "baseFare", "cost": base},
                {"title": "Reservation Charges", "key": "reservationCharges", "cost": res_charges},
                {"title": "GST", "key": "serviceTax", "cost": gst},
                {"title": "Total Amount", "key": "total", "cost": price}
            ]
        }
        tatkal_price = price + max(100, int(price * 0.2))
        tatkal_item = {
            "classType": class_code,
            "fare": tatkal_price,
            "breakup": [
                {"title": "Base Charges", "key": "baseFare", "cost": base},
                {"title": "Reservation Charges", "key": "reservationCharges", "cost": res_charges},
                {"title": "Tatkal Charges", "key": "tatkalCharges", "cost": tatkal_price - price},
                {"title": "Total Amount", "key": "total", "cost": tatkal_price}
            ]
        }
        fares_entry["data"]["general"].append(general_item)
        fares_entry["data"]["tatkal"].append(tatkal_item)

    getfare["fares"].append(fares_entry)

    # build searchTrain entry
    st = {
        "train_number": train_no,
        "train_name": t.get("train_name", ""),
        "eng_train_name": t.get("train_name", "").upper(),
        "new_train_number": "",
        "is_fav": False,
        "src_stn_code": code_for(src),
        "src_stn_name": src,
        "dstn_stn_code": code_for(dst),
        "dstn_stn_name": dst,
        "date": DEMO_DATE
    }
    searchtrain["data"].append(st)

# write outputs
# Overwrite the app-facing files so the system uses the coherent generated data
with open(BASE / "getFare.json", "w", encoding="utf-8") as f:
    json.dump(getfare, f, indent=2, ensure_ascii=False)

with open(BASE / "searchTrain.json", "w", encoding="utf-8") as f:
    json.dump(searchtrain, f, indent=2, ensure_ascii=False)

# create empty bookings file
with open(BASE / "bookings.json", "w", encoding="utf-8") as f:
    json.dump({"bookings": []}, f, indent=2)

print("Generated and updated: getFare.json, searchTrain.json, bookings.json")
