import os
import json
import pandas as pd
from datetime import datetime
import pytz

# Config
folder_path = 'D:/School/Ai sports odds better/dk-odds-scraper/MLB/data/1st_Inning'
output_file = 'D:/School/Ai sports odds better/dk-odds-scraper/MLB/Excel_Files/MLB_1st_Inning_Props.xlsx'

def convert_to_central_time(utc_time_str):
    if "." in utc_time_str:
        utc_time_str = utc_time_str.split(".")[0] + "Z"
    try:
        utc_dt = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
        central = pytz.timezone("US/Central")
        return utc_dt.replace(tzinfo=pytz.utc).astimezone(central).strftime("%Y-%m-%d %I:%M %p %Z")
    except:
        return utc_time_str

def extract_inning_props(data, sheet_name):
    events = {e["id"]: e for e in data.get("events", [])}
    markets = {m["id"]: m for m in data.get("markets", [])}
    selections = data.get("selections", [])

    rows = []

    for selection in selections:
        market = markets.get(selection.get("marketId", ""), {})
        event = events.get(market.get("eventId", ""), {})

        matchup = event.get("name", "Unknown")
        start_time = convert_to_central_time(event.get("startEventDate", ""))
        team = "Unknown"
        for p in selection.get("participants", []):
            if p.get("type") == "Team":
                team = p.get("name")

        rows.append({
            "Team": team,
            "Matchup": matchup,
            "Start Time": start_time,
            "Prop Type": market.get("marketType", {}).get("name", sheet_name),
            "Label": selection.get("label", ""),
            "Line": selection.get("points", ""),
            "Outcome": selection.get("outcomeType", ""),
            "Odds": selection.get("displayOdds", {}).get("american", "")
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
                sheet_name = filename.replace('.json', '')[:31]
                df = extract_inning_props(data, sheet_name)
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"✅ Wrote: {sheet_name}")
            except Exception as e:
                print(f"❌ Error processing {filename}: {e}")

print(f"\n✅ All 1st inning props saved to {output_file}")
