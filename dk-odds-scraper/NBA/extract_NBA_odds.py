import json
from collections import defaultdict
from datetime import datetime
import pytz
from pprint import pprint

# Load your JSON file
with open("nba_api_response.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Index markets and selections by their IDs for quick lookup
markets_by_event = defaultdict(list)
for market in data["markets"]:
    markets_by_event[market["eventId"]].append(market)

selections_by_market = defaultdict(list)
for selection in data["selections"]:
    selections_by_market[selection["marketId"]].append(selection)

# Extract relevant data
games_info = []

for event in data["events"]:
    print("Market name:", market["name"])
    event_id = event["id"]
    game_name = event["name"]

    # Convert UTC time to Central Time
    utc_time = datetime.fromisoformat(event["startEventDate"].replace("Z", "+00:00"))
    central_time = utc_time.astimezone(pytz.timezone("US/Central"))
    start_time = central_time.strftime("%Y-%m-%d %I:%M %p %Z")

    game_data = {
        "Game": game_name,
        "Start Time": start_time,
        "Moneyline": {},
        "Spread": {},
        "Total": {}
    }

    for market in markets_by_event[event_id]:
        market_id = market["id"]
        market_name = market["name"]

        for selection in selections_by_market[market_id]:
            label = selection.get("label")
            odds = selection.get("displayOdds", {}).get("american")
            points = selection.get("points")

            if market_name == "Moneyline":
                game_data["Moneyline"][label] = odds
            elif market_name in ["Point Spread", "Run Line", "Puck Line"]:
                game_data["Spread"][label] = {"odds": odds, "points": points}
            elif market_name == "Total":
                outcome = selection.get("outcomeType")
                game_data["Total"][outcome] = {"odds": odds, "points": points}

    games_info.append(game_data)

pprint(games_info)
