import os
import json
import pandas as pd
from datetime import datetime
import pytz

# Config
folder_path = 'D:/School/Ai sports odds better/dk-odds-scraper/MLB/data/Team_Totals'
output_file = 'D:/School/Ai sports odds better/dk-odds-scraper/MLB/Excel_Files/MLB_Team_Totals.xlsx'

def convert_to_central_time(utc_time_str):
    if "." in utc_time_str:
        utc_time_str = utc_time_str.split(".")[0] + "Z"
    utc_dt = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
    central = pytz.timezone("US/Central")
    return utc_dt.replace(tzinfo=pytz.utc).astimezone(central).strftime("%Y-%m-%d %I:%M %p %Z")

def extract_team_props(data, sheet_name):
    events = {e['id']: e for e in data.get("events", [])}
    markets = {m['id']: m for m in data.get("markets", [])}
    selections = data.get("selections", [])

    rows = []

    for selection in selections:
        market_id = selection.get("marketId")
        market = markets.get(market_id, {})
        event_id = market.get("eventId")
        event = events.get(event_id, {})

        matchup = event.get("name", "Unknown")
        start = convert_to_central_time(event.get("startEventDate", ""))
        prop_type = market.get("marketType", {}).get("name", sheet_name)

        label = selection.get("label", "")
        outcome = selection.get("outcomeType", "")
        odds = selection.get("displayOdds", {}).get("american", "")
        line = selection.get("points", "")

        # Get team name from participants
        participants = selection.get("participants", [])
        team_name = participants[0].get("name", "Unknown") if participants else "Unknown"

        rows.append({
            "Team": team_name,
            "Matchup": matchup,
            "Start Time": start,
            "Prop Type": prop_type,
            "Label": label,
            "Line": line,
            "Outcome": outcome,
            "Odds": odds
        })

    return pd.DataFrame(rows)

# Write to Excel
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    for filename in os.listdir(folder_path):
        if not filename.endswith('.json'):
            continue
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                sheet_name = filename.replace(".json", "")[:31]
                df = extract_team_props(data, sheet_name)
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"✅ Wrote: {sheet_name}")
            except Exception as e:
                print(f"❌ Error in {filename}: {e}")

print(f"\n✅ All team totals saved to {output_file}")
