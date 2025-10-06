import os
import json
import pandas as pd
from datetime import datetime
import pytz

# Config
folder_path = 'D:/School/Ai sports odds better/dk-odds-scraper/MLB/data/1st_of_Game'
output_file = 'D:/School/Ai sports odds better/dk-odds-scraper/MLB/Excel_Files/MLB_1st_of_Game_Props.xlsx'

def convert_to_central_time(utc_time_str):
    if "." in utc_time_str:
        utc_time_str = utc_time_str.split(".")[0] + "Z"
    utc_dt = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
    central = pytz.timezone("US/Central")
    return utc_dt.replace(tzinfo=pytz.utc).astimezone(central).strftime("%Y-%m-%d %I:%M %p %Z")

def extract_1st_of_game_data(data, prop_type):
    events = {e["id"]: e for e in data.get("events", [])}
    markets = {m["id"]: m for m in data.get("markets", [])}
    selections = data.get("selections", [])

    rows = []

    for selection in selections:
        market = markets.get(selection.get("marketId", ""), {})
        event = events.get(market.get("eventId", ""), {})

        label = selection.get("label", "")
        outcome = selection.get("outcomeType", "")
        odds = selection.get("displayOdds", {}).get("american", "")
        

        matchup = event.get("name", "Unknown")
        start_time = convert_to_central_time(event.get("startEventDate", "Unknown"))

        rows.append({
            "Label": label,
            "Matchup": matchup,
            "Start Time": start_time,
            "Prop Type": prop_type,
            "Team": outcome,
            "Odds": odds
        })

    return pd.DataFrame(rows)

# Write to Excel
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    for file in os.listdir(folder_path):
        if file.endswith('.json'):
            file_path = os.path.join(folder_path, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    prop_type = file.replace("_api_response.json", "").replace("1st_", "1st ").replace("_", " ").title()
                    sheet_name = file.replace(".json", "")[:31]

                    df = extract_1st_of_game_data(data, prop_type)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    print(f"✅ Wrote: {sheet_name}")
                except Exception as e:
                    print(f"❌ Error in {file}: {e}")

print(f"\n✅ All 1st of Game props saved to {output_file}")
