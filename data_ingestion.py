import os
import glob
import pandas as pd

raw_dir = os.path.join("data", "raw")
csv_files = glob.glob(os.path.join(raw_dir, "*.csv"))

print(f"Found {len(csv_files)} datasets in {raw_dir}\n")
print("=== 1. LOADING & INSPECTING CSV DATASETS ===")
dfs = {}

for file in sorted(csv_files):
    filename = os.path.basename(file)
    try:
        df = pd.read_csv(file)
        dfs[filename] = df
        print(f"-> File: {filename}")
        print(f"   Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        print(f"   Dtypes preview: {list(df.dtypes.to_dict().items())[:2]}")
    except Exception as e:
        print(f"Error reading {filename}: {e}")

print("\n=== 2. FUND MASTER EXPLORATION ===")
fund_master_key = next((k for k in dfs.keys() if "fund_master" in k.lower()), None)

if fund_master_key:
    fm = dfs[fund_master_key]
    print(f"Exploring: {fund_master_key}")
    for col in ["fund_house", "category", "sub_category", "risk_category"]:
        matches = [c for c in fm.columns if col in c.lower()]
        if matches:
            col_name = matches[0]
            uniques = fm[col_name].dropna().unique()
            print(f"  * Unique {col_name} ({len(uniques)}): {list(uniques[:4])}")
else:
    print("Notice: fund_master dataset not found.")

print("\n=== 3. AMFI CODE VALIDATION ===")
nav_history_key = next((k for k in dfs.keys() if "nav_history" in k.lower()), None)

if fund_master_key and nav_history_key:
    fm = dfs[fund_master_key]
    nav = dfs[nav_history_key]
    
    fm_col = [c for c in fm.columns if "amfi" in c.lower() or "code" in c.lower()][0]
    nav_col = [c for c in nav.columns if "amfi" in c.lower() or "code" in c.lower()][0]
    
    fm_codes = set(fm[fm_col].dropna().unique())
    nav_codes = set(nav[nav_col].dropna().unique())
    
    missing = fm_codes - nav_codes
    print(f"Fund Master AMFI Codes count: {len(fm_codes)}")
    print(f"NAV History AMFI Codes count: {len(nav_codes)}")
    
    print("\n--- DATA QUALITY REPORT ---")
    if len(missing) == 0:
        print("PASS: All codes in fund_master exist in nav_history.")
    else:
        print(f"NOTE: {len(missing)} codes from fund_master missing in nav_history: {missing}")