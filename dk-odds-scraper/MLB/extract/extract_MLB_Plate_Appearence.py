import os
import json
import pandas as pd
from datetime import datetime
import pytz
from collections import defaultdict

# Config
input_file = 'D:/School/Ai sports odds better/dk-odds-scraper/MLB/data/Plate_appearence/mlb_Plate_Appearence_api_response.json'
output_file = 'D:/School/Ai sports odds better/dk-odds-scraper/MLB/Excel_Files/Plate_Appearance_Props.xlsx'

def convert_to_central_time(utc_time_str):
    if "." in utc_time_str:
        utc_time_str = utc_time_str.split(".")[0] + "Z"
    utc_dt = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
    central = pytz.timezone("US/Central")
    return utc_dt.replace(tzinfo=pytz.utc).astimezone(central).strftime("%Y-%m-%d %I:%M %p %Z")

def extract_player_name(market_name):
    if " - " in market_name:
        return market_name.split(" - ")[0].strip()
    return "Unknown"

def extract_plate_appearance_props(data):
    events = {e['id']: e for e in data.get("events", [])}
    markets = {m['id']: m for m in data.get("markets", [])}
    selections = data.get("selections", [])

    rows = []

    for selection in selections:
        market_id = selection.get("marketId")
        market = markets.get(market_id, {})
        event = events.get(market.get("eventId", ""), {})

        player = extract_player_name(market.get("name", ""))
        matchup = event.get("name", "Unknown")
        start_time = convert_to_central_time(event.get("startEventDate", ""))
        prop_type = market.get("marketType", {}).get("name", "Plate Appearance Result")
        result = selection.get("label", "")
        odds = selection.get("displayOdds", {}).get("american", "")

        rows.append({
            "Player": player,
            "Matchup": matchup,
            "Start Time": start_time,
            "Prop Type": prop_type,
            "Result": result,
            "Odds": odds
        })

    return pd.DataFrame(rows)

# Load and process
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)
    df = extract_plate_appearance_props(data)

# Save to Excel
df.to_excel(output_file, index=False)
print(f"✅ Plate appearance props saved to {output_file}")
