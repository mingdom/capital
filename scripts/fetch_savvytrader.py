import json
import os
import shutil
import sys
from datetime import datetime

import requests

# Reference: docs/savvytrader-api.md for more endpoint details and discovery notes.

def fetch_savvytrader_data(token):
    portfolio_id = "4737"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d_%H%M%S')

    # Save a permanent record in data/savvytrader/
    archive_dir = f"data/savvytrader/{timestamp}"
    os.makedirs(archive_dir, exist_ok=True)

    endpoints = {
        "valuations": f"https://api.savvytrader.com/core/portfolios/{portfolio_id}/valuations?range=all",
        "holdings_prices": f"https://api.savvytrader.com/core/portfolios/{portfolio_id}/holdings/prices",
        "holdings_cost": f"https://api.savvytrader.com/core/portfolios/{portfolio_id}/holdings?range=all",
        "metadata": f"https://api.savvytrader.com/core/portfolios/{portfolio_id}"
    }

    print(f"Starting full data capture to {archive_dir}...")

    captured_files = {}
    for name, url in endpoints.items():
        print(f"  Fetching {name}...")
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            filename = f"{archive_dir}/{name}.json"
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
            captured_files[name] = filename
        except Exception as e:
            print(f"  Error fetching {name}: {e}")

    # Stage the primary ones in data/import for 'make import'
    # Use the timestamp in the filename so the importer picks up the absolute latest
    os.makedirs("data/import", exist_ok=True)
    if "valuations" in captured_files:
        shutil.copy(captured_files["valuations"], f"data/import/valuations-{timestamp}.json")
    if "holdings_prices" in captured_files:
        shutil.copy(captured_files["holdings_prices"], f"data/import/holdings-{timestamp}.json")

    print(f"\nCapture complete. All data stored in {archive_dir}")
    print("Staged valuations and holdings in data/import/ for 'make import'.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/fetch_savvytrader.py <id_token>")
        sys.exit(1)

    fetch_savvytrader_data(sys.argv[1])
