import os
import json
import pandas as pd

# Config
folder_path = 'D:/School/Ai sports odds better/dk-odds-scraper/MLB/data/Champion'
output_file = 'D:/School/Ai sports odds better/dk-odds-scraper/MLB/Excel_Files/MLB_Champion.xlsx'

def extract_champion_props(data, sheet_name):
    selections = data.get("selections", [])
    markets = {m["id"]: m for m in data.get("markets", [])}
    events = {e["id"]: e for e in data.get("events", [])}

    rows = []

    for selection in selections:
        market = markets.get(selection.get("marketId", ""), {})
        event = events.get(market.get("eventId", ""), {})

        team = selection.get("label", "Unknown")
        odds = selection.get("displayOdds", {}).get("american", "")
        prop_type = market.get("marketType", {}).get("name", sheet_name)
        matchup = event.get("name", "N/A")

        rows.append({
            "Team": team,
            "Matchup": matchup,
            "Prop Type": prop_type,
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
                sheet_name = filename.replace('.json', '')[:31]
                df = extract_champion_props(data, sheet_name)
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"✅ Wrote: {sheet_name}")
            except Exception as e:
                print(f"❌ Error processing {filename}: {e}")

print(f"\n✅ All champion/special props saved to {output_file}")
