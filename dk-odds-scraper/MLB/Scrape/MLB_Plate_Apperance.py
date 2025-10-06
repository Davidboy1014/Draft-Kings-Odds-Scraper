"""
Data Collection Script

LEGAL DISCLAIMER:
This script is for educational and research purposes only.
Users are responsible for complying with all applicable terms of service.
The authors are not affiliated with DraftKings or any sportsbook.
Use at your own risk and ensure compliance with local laws.
"""

import requests
import json
import os

# API URLs removed for safety - users must provide their own endpoints
# This is a template showing the structure for data collection
urls = [
    ("mlb_Plate_Appearence", "YOUR_API_ENDPOINT_HERE"),
    
    
    
    # Add more (label, url) pairs here as needed
]

headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "origin": "https://sportsbook.draftkings.com",
    "referer": "https://sportsbook.draftkings.com/",
    "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
}

output_dir = "D:/School/Ai sports odds better/dk-odds-scraper/MLB/data/Plate_appearence"
os.makedirs(output_dir, exist_ok=True)

for label, url in urls:
    print(f"🔄 Fetching data for {label.upper()}...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        file_path = os.path.join(output_dir, f"{label}_api_response.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(response.json(), f, indent=2)
        print(f"✅ Data saved to {file_path}")
    else:
        print(f"❌ Failed to fetch data for {label.upper()}: {response.status_code}")
