import os
import json
import pandas as pd
from datetime import datetime
import pytz
from collections import defaultdict

# Set the folder and output path
folder_path = 'D:/School/Ai sports odds better/dk-odds-scraper/MLB/data/Batter_Props'
output_file = 'D:/School/Ai sports odds better/dk-odds-scraper/MLB/Excel_Files/MLB_Batter_Props.xlsx'

def convert_to_central_time(utc_time_str):
    try:
        if "." in utc_time_str:
            utc_time_str = utc_time_str.split(".")[0] + "Z"
        utc_dt = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
        central = pytz.timezone("US/Central")
        return utc_dt.replace(tzinfo=pytz.utc).astimezone(central).strftime("%Y-%m-%d %I:%M %p %Z")
    except:
        return utc_time_str

def extract_player_and_prop(market_name):
    # Example market_name: "Aaron Judge - Runs" or "Aaron Judge Runs"
    for sep in [" - ", " – ", " — "]:
        if sep in market_name:
            return market_name.split(sep)[0].strip(), market_name.split(sep)[-1].strip()
    # fallback: assume last word is the stat
    parts = market_name.strip().rsplit(" ", 1)
    return (parts[0], parts[1]) if len(parts) == 2 else ("Unknown", "Unknown")


def extract_batter_props(data, prop_type):
    events = {e["id"]: e for e in data.get("events", [])}
    markets = {m["id"]: m for m in data.get("markets", [])}
    selections = data.get("selections", [])

    rows = []

    for selection in selections:
        market_id = selection.get("marketId")
        market = markets.get(market_id, {})
        event_id = market.get("eventId")
        event = events.get(event_id, {})

        # Extract matchup info
        matchup = event.get("name", "Unknown")
        start = convert_to_central_time(event.get("startEventDate", ""))
        outcome = selection.get("outcomeType", "")
        odds = selection.get("displayOdds", {}).get("american", "")
        line = selection.get("points", "")

        market_name = market.get("name", "")
        player, prop = extract_player_and_prop(market_name)
        

        rows.append({
            "Player": player,
            "Matchup": matchup,
            "Start Time": start,
            "Prop Type": prop_type or prop,
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

                sheet_name = filename[:31].replace('.json', '')
                prop_type = filename.replace("mlb_", "").replace("_O_U", "").replace("_api_response.json", "").replace("_", " ").title()

                df = extract_batter_props(data, prop_type)
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"✅ Wrote: {sheet_name}")

            except Exception as e:
                print(f"❌ Error in {filename}: {e}")

print(f"\n✅ All batter props saved to {output_file}")