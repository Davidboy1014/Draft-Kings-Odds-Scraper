import os
import json
import pandas as pd
from datetime import datetime
import pytz

# Config paths
folder_path = 'D:/School/Ai sports odds better/dk-odds-scraper/MLB/data/Inning'
output_file = 'D:/School/Ai sports odds better/dk-odds-scraper/MLB/Excel_Files/MLB_Inning_Props.xlsx'

def convert_to_central_time(utc_time_str):
    if "." in utc_time_str:
        utc_time_str = utc_time_str.split(".")[0] + "Z"
    utc_dt = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
    central = pytz.timezone("US/Central")
    return utc_dt.replace(tzinfo=pytz.utc).astimezone(central).strftime("%Y-%m-%d %I:%M %p %Z")

def extract_inning_data(data, prop_type):
    events = {e["id"]: e for e in data.get("events", [])}
    markets = {m["id"]: m for m in data.get("markets", [])}
    selections = data.get("selections", [])

    rows = []

    for selection in selections:
        market = markets.get(selection.get("marketId", ""), {})
        event = events.get(market.get("eventId", ""), {})

        matchup = event.get("name", "Unknown")
        start_time = convert_to_central_time(event.get("startEventDate", "Unknown"))
        label = selection.get("label", "")
        odds = selection.get("displayOdds", {}).get("american", "")
        line = selection.get("points", "")
        outcome = selection.get("outcomeType", "")

        # Try to extract inning info from market name (if any)
        market_name = market.get("name", "")
        inning = ""
        for i in range(1, 10):
            if f"{i}st" in market_name or f"{i}nd" in market_name or f"{i}rd" in market_name or f"{i}th" in market_name:
                inning = f"{i}"
                break

        rows.append({
            "Matchup": matchup,
            "Start Time": start_time,
            "Prop Type": prop_type,
            "Inning": inning,
            "Label": label,
            "Line": line,
            "Outcome": outcome,
            "Odds": odds
        })

    return pd.DataFrame(rows)

# Write all to Excel
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    for file in os.listdir(folder_path):
        if file.endswith('.json'):
            try:
                file_path = os.path.join(folder_path, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    sheet_name = file.replace('.json', '')[:31]
                    prop_type = file.replace("Inning_", "").replace("_api_response.json", "").replace("_", " ").title()

                    df = extract_inning_data(data, prop_type)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    print(f"✅ Wrote: {sheet_name}")
            except Exception as e:
                print(f"❌ Error in {file}: {e}")

print(f"\n✅ All inning props saved to {output_file}")
