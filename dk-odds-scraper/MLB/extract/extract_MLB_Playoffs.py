import os
import json
import pandas as pd

# Config
folder_path = 'D:/School/Ai sports odds better/dk-odds-scraper/MLB/data/Playoffs'
output_file = 'D:/School/Ai sports odds better/dk-odds-scraper/MLB/Excel_Files/MLB_Playoff.xlsx'

def extract_playoff_props(data, sheet_name):
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
        market_name = market.get("name", "")
        playoff_type = event.get("name", "Unknown Playoff Market")

        rows.append({
            "Team": team,
            "Playoff Market": playoff_type,
            "Prop Type": prop_type,
            "Label": selection.get("label", ""),
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
                df = extract_playoff_props(data, sheet_name)
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"✅ Wrote: {sheet_name}")
            except Exception as e:
                print(f"❌ Error processing {filename}: {e}")

print(f"\n✅ All playoff props saved to {output_file}")
