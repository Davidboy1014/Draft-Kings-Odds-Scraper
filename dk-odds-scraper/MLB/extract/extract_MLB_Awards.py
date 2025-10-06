import os
import json
import pandas as pd

# Config
folder_path = 'D:/School/Ai sports odds better/dk-odds-scraper/MLB/data/Awards'
output_file = 'D:/School/Ai sports odds better/dk-odds-scraper/MLB/Excel_Files/MLB_Awards.xlsx'

def extract_awards(data, sheet_name):
    selections = data.get("selections", [])
    markets = {m.get("id"): m for m in data.get("markets", [])}
    events = {e.get("id"): e for e in data.get("events", [])}

    rows = []

    for selection in selections:
        market = markets.get(selection.get("marketId", ""), {})
        event = events.get(market.get("eventId", ""), {})

        player = selection.get("label", "Unknown")
        odds = selection.get("displayOdds", {}).get("american", "")
        prop_type = market.get("marketType", {}).get("name", sheet_name)
        award_title = event.get("name", "Unknown Award")

        rows.append({
            "Player": player,
            "Award Title": award_title,
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
                df = extract_awards(data, sheet_name)
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"✅ Wrote: {sheet_name}")
            except Exception as e:
                print(f"❌ Error processing {filename}: {e}")

print(f"\n✅ All awards props saved to {output_file}")
