import os
import json
import pandas as pd
from datetime import datetime
import pytz
from collections import defaultdict

# Config
folder_path = 'D:/School/Ai sports odds better/dk-odds-scraper/MLB/data/Pitcher_Props'
output_file = 'D:/School/Ai sports odds better/dk-odds-scraper/MLB/Excel_Files/Pitcher_Props_Excel.xlsx'

def convert_to_central_time(utc_time_str):
    if "." in utc_time_str:
        utc_time_str = utc_time_str.split(".")[0] + "Z"
    utc_dt = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
    central = pytz.timezone("US/Central")
    return utc_dt.replace(tzinfo=pytz.utc).astimezone(central).strftime("%Y-%m-%d %I:%M %p %Z")

def extract_pitcher_props(data, sheet_name):
    events = {e['id']: e for e in data.get("events", [])}
    markets = {m['id']: m for m in data.get("markets", [])}
    selections = data.get("selections", [])

    # Build pitcher lookup from participants
    pitcher_lookup = {}
    for event in events.values():
        for participant in event.get("participants", []):
            pitcher_name = participant.get("metadata", {}).get("startingPitcherPlayerName", "").strip()
            if pitcher_name:
                pitcher_lookup[pitcher_name.lower()] = {
                    "team": participant.get("name", "Unknown"),
                    "matchup": event.get("name", "Unknown"),
                    "start": convert_to_central_time(event.get("startEventDate", "Unknown"))
                }

    rows = []
    for selection in selections:
        market = markets.get(selection.get("marketId", ""), {})
        market_name = market.get("name", "")
        prop_type = market.get("marketType", {}).get("name", sheet_name)
        odds = selection.get("displayOdds", {}).get("american", "")
        label = selection.get("label", "")
        if label.endswith("+"):
            outcome = "Over"
            line = label.replace("+", "")
        else:
            outcome = selection.get("outcomeType", "")
            line = selection.get("points", "")


        # Try to get player name from selection["participants"]
        player_name = "Unknown"
        if "participants" in selection and selection["participants"]:
            player_name = selection["participants"][0].get("name", "Unknown")
        else:
            # Fallback to parsing market name (e.g., "Aaron Nola - Walks Allowed")
            if " - " in market_name:
                player_name = market_name.split(" - ")[0].strip()
            else:
                player_name = market_name.split(" ")[0].strip()  # crude fallback

        # Lookup pitcher info
        pitcher_info = pitcher_lookup.get(player_name.lower(), {
            "team": "Unknown",
            "matchup": "Unknown",
            "start": "Unknown"
        })

        rows.append({
            "Player": player_name,
            "Team": pitcher_info["team"],
            "Matchup": pitcher_info["matchup"],
            "Start Time": pitcher_info["start"],
            "Prop Type": prop_type,
            "Line": line,
            "Outcome": outcome,
            "Odds": odds
        })

    return pd.DataFrame(rows)

# Write each JSON to its own sheet
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    for file in os.listdir(folder_path):
        if file.endswith('.json'):
            file_path = os.path.join(folder_path, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    sheet_name = file.replace('.json', '')[:31]
                    df = extract_pitcher_props(data, sheet_name)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    print(f"✅ Wrote: {sheet_name}")
                except Exception as e:
                    print(f"❌ Error in {file}: {e}")

print(f"\n✅ All pitcher props saved to {output_file}")
