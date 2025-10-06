"""
NHL Data Collection Script

LEGAL DISCLAIMER:
This script is for educational and research purposes only.
Users are responsible for complying with all applicable terms of service.
The authors are not affiliated with DraftKings or any sportsbook.
Use at your own risk and ensure compliance with local laws.
"""

import requests

# API URL removed for safety - users must provide their own endpoint
url = "YOUR_API_ENDPOINT_HERE"  # Replace with your own endpoint

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

# Optional: Replace this with real cookies if needed for access
cookies = {
    # "key": "value",
}

response = requests.get(url, headers=headers, cookies=cookies)

if response.status_code == 200:
    data = response.json()
    # Save the response
    import json
    with open("nhl_api_response.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("✅ Data saved to nhl_api_response.json")
else:
    print(f"❌ Failed to fetch data: {response.status_code}")

