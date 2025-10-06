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

nba_url = "YOUR_API_ENDPOINT_HERE"
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

response = requests.get(nba_url, headers=headers)

if response.status_code == 200:
    with open("nba_api_response.json", "w", encoding="utf-8") as f:
        json.dump(response.json(), f, indent=2)
    print("✅ NBA data saved to nba_api_response.json")
else:
    print(f"❌ Failed to fetch NBA data: {response.status_code}")
