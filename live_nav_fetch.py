import os
import requests
import pandas as pd

SCHEMES = {
    "hdfc_top_100": 125497,
    "sbi_bluechip": 119551,
    "icici_bluechip": 120503,
    "nippon_large_cap": 118632,
    "axis_bluechip": 119092,
    "kotak_bluechip": 120841
}

os.makedirs(os.path.join("data", "raw"), exist_ok=True)

for name, code in SCHEMES.items():
    print(f"Fetching NAV data for {name} ({code})...")
    url = f"https://api.mfapi.in/mf/{code}"
    
    response = requests.get(url)
    if response.status_code == 200:
        payload = response.json()
        nav_records = payload.get("data", [])
        
        df = pd.DataFrame(nav_records)
        df["scheme_code"] = code
        df["scheme_name"] = payload.get("meta", {}).get("scheme_name", name)
        
        output_path = os.path.join("data", "raw", f"{name}_{code}.csv")
        df.to_csv(output_path, index=False)
        print(f" Saved: {output_path} ({len(df)} rows)")
    else:
        print(f" Failed to fetch {name} (Status code: {response.status_code})")

print("\nLive NAV fetch completed.")