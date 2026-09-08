import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import nbformat as nbf

# -------------------------------------------------------------
# Paths
# -------------------------------------------------------------
BASE_DIR = os.getcwd()
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
NOTEBOOKS_DIR = os.path.join(BASE_DIR, "notebooks")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(NOTEBOOKS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. Load Cleaned Datasets
# -------------------------------------------------------------
nav_file = os.path.join(PROCESSED_DIR, "nav_history_cleaned.csv")
fund_file = os.path.join(PROCESSED_DIR, "fund_master_cleaned.csv")
bmark_file = os.path.join(PROCESSED_DIR, "benchmark_indices_cleaned.csv")

df_nav = pd.read_csv(nav_file)
df_funds = pd.read_csv(fund_file)
df_bmark = pd.read_csv(bmark_file) if os.path.exists(bmark_file) else None

# Clean column headers
df_nav.columns = [c.lower().strip() for c in df_nav.columns]
df_funds.columns = [c.lower().strip() for c in df_funds.columns]
if df_bmark is not None:
    df_bmark.columns = [c.lower().strip() for c in df_bmark.columns]

# Detect columns
date_col = [c for c in df_nav.columns if 'date' in c][0]
nav_col = [c for c in df_nav.columns if 'nav' in c][0]
scheme_col = [c for c in df_nav.columns if 'code' in c or 'scheme' in c][0]

df_nav[date_col] = pd.to_datetime(df_nav[date_col])
df_nav = df_nav.sort_values([scheme_col, date_col]).reset_index(drop=True)

# -------------------------------------------------------------
# 2. Daily Returns & Benchmark Alignment
# -------------------------------------------------------------
df_nav['daily_return'] = df_nav.groupby(scheme_col)[nav_col].pct_change()

# Create pivot table for NAV and returns
nav_pivot = df_nav.pivot(index=date_col, columns=scheme_col, values=nav_col).dropna(how='all')
return_pivot = nav_pivot.pct_change()

# Setup Nifty 100 / Nifty 50 benchmark returns
bmark_ret = None
bmark_50_ret = None
if df_bmark is not None:
    b_date_col = [c for c in df_bmark.columns if 'date' in c][0]
    df_bmark[b_date_col] = pd.to_datetime(df_bmark[b_date_col])
    
    # Check for nifty 100 column
    n100_cols = [c for c in df_bmark.columns if '100' in c]
    n50_cols = [c for c in df_bmark.columns if '50' in c]
    
    if n100_cols:
        bmark_series = df_bmark.set_index(b_date_col)[n100_cols[0]].sort_index()
        bmark_ret = bmark_series.pct_change()
    if n50_cols:
        bmark_50_series = df_bmark.set_index(b_date_col)[n50_cols[0]].sort_index()
        bmark_50_ret = bmark_50_series.pct_change()

# Fallback proxy if benchmark CSV has different column names
if bmark_ret is None:
    bmark_ret = return_pivot.mean(axis=1)

# -------------------------------------------------------------
# 3. Metrics Calculation: CAGR, Sharpe, Sortino, Alpha, Beta, Max DD
# -------------------------------------------------------------
Rf = 0.065  # 6.5% RBI repo rate proxy
trading_days = 252
metrics = []

for scheme in nav_pivot.columns:
    s_nav = nav_pivot[scheme].dropna()
    s_ret = return_pivot[scheme].dropna()
    
    if len(s_nav) < 20:
        continue
        
    days = (s_nav.index[-1] - s_nav.index[0]).days
    n_years = max(days / 365.25, 0.1)
    
    # CAGR helper
    def calc_cagr(series, yrs):
        cutoff = series.index[-1] - pd.DateOffset(years=yrs)
        sub = series[series.index >= cutoff]
        if len(sub) > 1:
            return ((sub.iloc[-1] / sub.iloc[0]) ** (1 / yrs)) - 1
        return np.nan

    cagr_1y = calc_cagr(s_nav, 1)
    cagr_3y = calc_cagr(s_nav, 3)
    cagr_5y = calc_cagr(s_nav, 5)
    total_cagr = ((s_nav.iloc[-1] / s_nav.iloc[0]) ** (1 / n_years)) - 1

    # Annualized Return & Std
    ann_ret = s_ret.mean() * trading_days
    ann_std = s_ret.std() * np.sqrt(trading_days)
    
    # Sharpe Ratio
    sharpe = (ann_ret - Rf) / ann_std if ann_std > 0 else np.nan

    # Sortino Ratio (downside std only)
    neg_ret = s_ret[s_ret < 0]
    downside_std = neg_ret.std() * np.sqrt(trading_days) if len(neg_ret) > 1 else np.nan
    sortino = (ann_ret - Rf) / downside_std if downside_std and downside_std > 0 else np.nan

    # Maximum Drawdown & Date Range
    running_max = s_nav.cummax()
    dd_series = (s_nav / running_max) - 1
    max_dd = dd_series.min()
    worst_dd_end = dd_series.idxmin()
    peak_date = s_nav.loc[:worst_dd_end].idxmax()

    # Alpha & Beta (OLS regression vs Nifty 100)
    aligned = pd.concat([s_ret.rename('fund'), bmark_ret.rename('bmark')], axis=1, join='inner').dropna()
    if len(aligned) > 20:
        slope, intercept, r_val, p_val, std_err = stats.linregress(aligned['bmark'], aligned['fund'])
        beta = slope
        alpha = intercept * trading_days
        tracking_error = (aligned['fund'] - aligned['bmark']).std() * np.sqrt(trading_days)
    else:
        alpha, beta, tracking_error = np.nan, np.nan, np.nan

    metrics.append({
        'scheme_code': scheme,
        'cagr_1yr': cagr_1y,
        'cagr_3yr': cagr_3y if not np.isnan(cagr_3y) else total_cagr,
        'cagr_5yr': cagr_5y,
        'sharpe_ratio': sharpe,
        'sortino_ratio': sortino,
        'alpha': alpha,
        'beta': beta,
        'max_drawdown': max_dd,
        'drawdown_peak_date': str(peak_date.date()) if pd.notna(peak_date) else None,
        'drawdown_trough_date': str(worst_dd_end.date()) if pd.notna(worst_dd_end) else None,
        'tracking_error': tracking_error
    })

df_metrics = pd.DataFrame(metrics)

# -------------------------------------------------------------
# 4. Merge Metadata (Scheme Name, Expense Ratio)
# -------------------------------------------------------------
f_code = [c for c in df_funds.columns if 'code' in c or 'scheme' in c][0]
f_name = [c for c in df_funds.columns if 'name' in c][0]
ter_cols = [c for c in df_funds.columns if 'ter' in c or 'expense' in c or 'ratio' in c]
ter_col = ter_cols[0] if ter_cols else None

df_merged = pd.merge(df_metrics, df_funds, left_on='scheme_code', right_on=f_code, how='left')

if ter_col:
    df_merged['expense_ratio'] = pd.to_numeric(df_merged[ter_col], errors='coerce').fillna(1.5)
else:
    df_merged['expense_ratio'] = 1.5

# Export alpha_beta.csv
df_alpha_beta = df_merged[['scheme_code', f_name, 'alpha', 'beta', 'sharpe_ratio', 'sortino_ratio', 'tracking_error']].copy()
df_alpha_beta.to_csv("alpha_beta.csv", index=False)
print("--> Generated: alpha_beta.csv")

# -------------------------------------------------------------
# 5. Composite Fund Scorecard (0–100)
# Formula: 30%*3yr_rank + 25%*Sharpe_rank + 20%*Alpha_rank + 15%*TER_inv + 10%*MaxDD_inv
# -------------------------------------------------------------
n = len(df_merged)
df_merged['rank_3yr'] = df_merged['cagr_3yr'].rank(ascending=True) / n * 100
df_merged['rank_sharpe'] = df_merged['sharpe_ratio'].rank(ascending=True) / n * 100
df_merged['rank_alpha'] = df_merged['alpha'].rank(ascending=True) / n * 100
df_merged['rank_ter_inv'] = df_merged['expense_ratio'].rank(ascending=False) / n * 100
df_merged['rank_dd_inv'] = df_merged['max_drawdown'].rank(ascending=True) / n * 100

df_merged['fund_score'] = (
    0.30 * df_merged['rank_3yr'] +
    0.25 * df_merged['rank_sharpe'] +
    0.20 * df_merged['rank_alpha'] +
    0.15 * df_merged['rank_ter_inv'] +
    0.10 * df_merged['rank_dd_inv']
).round(2)

df_scorecard = df_merged[['scheme_code', f_name, 'cagr_1yr', 'cagr_3yr', 'sharpe_ratio', 'sortino_ratio', 'alpha', 'beta', 'expense_ratio', 'max_drawdown', 'fund_score']]
df_scorecard = df_scorecard.sort_values(by='fund_score', ascending=False).reset_index(drop=True)
df_scorecard.to_csv("fund_scorecard.csv", index=False)
print("--> Generated: fund_scorecard.csv")

# -------------------------------------------------------------
# 6. Benchmark Comparison Chart PNG
# -------------------------------------------------------------
top_5_schemes = df_scorecard['scheme_code'].head(5).values

plt.figure(figsize=(12, 6))
for s_code in top_5_schemes:
    if s_code in nav_pivot.columns:
        s_series = nav_pivot[s_code].dropna()
        # Normalized to 100
        norm_series = (s_series / s_series.iloc[0]) * 100
        scheme_label = df_scorecard.loc[df_scorecard['scheme_code'] == s_code, f_name].values[0]
        plt.plot(norm_series.index, norm_series, label=str(scheme_label)[:25], alpha=0.85)

# Benchmark line
norm_bmark = ((1 + bmark_ret.fillna(0)).cumprod())
norm_bmark = (norm_bmark / norm_bmark.iloc[0]) * 100
plt.plot(norm_bmark.index, norm_bmark, label="Nifty 100 Benchmark", color="black", linewidth=2.2, linestyle="--")

plt.title("Top 5 Funds vs Benchmark (Normalized Performance)", fontsize=13, fontweight='bold')
plt.xlabel("Date")
plt.ylabel("Normalized Growth (Base = 100)")
plt.legend(loc="upper left", fontsize=9)
plt.grid(True, linestyle=":", alpha=0.6)
plt.tight_layout()
plt.savefig("benchmark_comparison_chart.png", dpi=300)
plt.close()
print("--> Generated: benchmark_comparison_chart.png")

# -------------------------------------------------------------
# 7. Generate Performance_Analytics.ipynb
# -------------------------------------------------------------
nb = nbf.v4.new_notebook()
nb.cells = [
    nbf.v4.new_markdown_cell("# Performance Analytics - Mutual Fund Capstone\n### Milestone: Fund Performance Analytics"),
    nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

scorecard = pd.read_csv('fund_scorecard.csv')
alpha_beta = pd.read_csv('alpha_beta.csv')
scorecard.head(10)"""),
    nbf.v4.new_markdown_cell("## 1. Top 5 Funds Comparison Table (by Composite Score)"),
    nbf.v4.new_code_cell("scorecard.head(5)"),
    nbf.v4.new_markdown_cell("## 2. Risk vs Return Profile (Alpha & Beta Summary)"),
    nbf.v4.new_code_cell("alpha_beta.describe()"),
    nbf.v4.new_markdown_cell("## 3. Benchmark Comparison Visualization"),
    nbf.v4.new_code_cell("""from IPython.display import Image
Image('benchmark_comparison_chart.png')""")
]

with open(os.path.join(NOTEBOOKS_DIR, "Performance_Analytics.ipynb"), "w", encoding="utf-8") as f:
    nbf.write(nb, f)
print("--> Generated: notebooks/Performance_Analytics.ipynb")
print("\nAll deliverables generated successfully!")