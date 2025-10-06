import os
import json
import pandas as pd
from datetime import datetime
import pytz
from collections import defaultdict

folder_path = "D:/School/Ai sports odds better/dk-odds-scraper/MLB/data/Game_Lines"
output_file = 'D:/School/Ai sports odds better/dk-odds-scraper/MLB/Excel_Files/MLB_Odds_Output.xlsx'

def convert_time(utc_str):
    try:
        utc_time = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
        central_time = utc_time.astimezone(pytz.timezone("US/Central"))
        return central_time.strftime("%Y-%m-%d %I:%M %p %Z")
    except:
        return utc_str

def process_game_file(data):
    rows = []
    events = {e['id']: e for e in data['events']}
    markets = defaultdict(list)
    selections = defaultdict(list)

    for m in data['markets']:
        markets[m['eventId']].append(m)
    for s in data['selections']:
        selections[s['marketId']].append(s)

    for eid, event in events.items():
        game_name = event['name']
        start_time = convert_time(event['startEventDate'])

        # Spread, Moneyline, Total containers
        spread_data, ml_data, total_data = {}, {}, {}

        for market in markets[eid]:
            mid = market['id']
            mname = market['name']

            for sel in selections[mid]:
                label = sel.get('label')
                odds = sel.get('displayOdds', {}).get('american')
                points = sel.get('points')
                outcome = sel.get('outcomeType')

                if mname in ['Point Spread', 'Run Line', 'Puck Line']:
                    spread_data[label] = (points, odds)
                elif mname == 'Moneyline':
                    ml_data[label] = odds
                elif mname == 'Total':
                    total_data[outcome] = (points, odds)

        # Build formatted rows
        rows.append({"Game": game_name, "Start Time": start_time})
        rows.append({"Game": "--- Spread ---"})
        for team, (pts, odds) in spread_data.items():
            rows.append({ "Game": team, "Start Time": f"{pts:+} pts / {odds}" })
        rows.append({"Game": "--- Moneyline ---"})
        for team, odds in ml_data.items():
            rows.append({ "Game": team, "Start Time": odds })
        rows.append({"Game": "--- Total Points ---"})
        for outcome, (pts, odds) in total_data.items():
            rows.append({ "Game": outcome, "Start Time": f"{pts} / {odds}" })
        rows.append({})  # Blank line
    return pd.DataFrame(rows)

def process_alt_run_line_file(data):
    rows = []
    events = {e['id']: e['name'] for e in data['events']}
    markets = defaultdict(list)
    selections = defaultdict(list)

    for m in data['markets']:
        markets[m['eventId']].append(m)
    for s in data['selections']:
        selections[s['marketId']].append(s)

    for eid, game_name in events.items():
        rows.append({"Game": game_name})
        for market in markets[eid]:
            for sel in selections[market['id']]:
                label = sel.get('label')
                points = sel.get('points')
                odds = sel.get('displayOdds', {}).get('american')
                rows.append({ "Game": f"{label} {points:+}", "Start Time": odds })
        rows.append({})
    return pd.DataFrame(rows)

def process_alt_total_file(data):
    rows = []
    events = {e['id']: e['name'] for e in data['events']}
    markets = defaultdict(list)
    selections = defaultdict(list)

    for m in data['markets']:
        markets[m['eventId']].append(m)
    for s in data['selections']:
        selections[s['marketId']].append(s)

    for eid, game_name in events.items():
        rows.append({"Game": game_name})
        for market in markets[eid]:
            for sel in selections[market['id']]:
                outcome = sel.get('outcomeType')
                points = sel.get('points')
                odds = sel.get('displayOdds', {}).get('american')
                rows.append({ "Game": f"{outcome} {points}", "Start Time": odds })
        rows.append({})
    return pd.DataFrame(rows)

# Main writer
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    for filename in os.listdir(folder_path):
        if not filename.endswith('.json'):
            continue
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if "Game" in filename:
            df = process_game_file(data)
            df.to_excel(writer, sheet_name='Game', index=False)
        elif "ALT_Run_Line" in filename:
            df = process_alt_run_line_file(data)
            df.to_excel(writer, sheet_name='ALT_Run_Line', index=False)
        elif "ALT_Total" in filename:
            df = process_alt_total_file(data)
            df.to_excel(writer, sheet_name='ALT_Total', index=False)

print("✅ All data written to MLB_Odds_Output.xlsx")
