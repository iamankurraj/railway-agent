from app.tools.filters import trains_between
from app.tools.json_loader import load_json

data = load_json("data/trains.json")
trains = data.get("trains", data)

filtered = trains_between(trains, "pune", "mumbai")
print(len(filtered), "matching trains")
