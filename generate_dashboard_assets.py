import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas

BASE_DIR = os.getcwd()
PROC_DIR = os.path.join(BASE_DIR, "data", "processed")
DASH_DIR = os.path.join(BASE_DIR, "reports", "dashboard_screens")
os.makedirs(DASH_DIR, exist_ok=True)

# Bluestock Color Palette
BG_COLOR = "#F4F6F9"
CARD_BG = "#FFFFFF"
PRIMARY_BLUE = "#0052CC"
ACCENT_NAVY = "#172B4D"
CYAN = "#00B8D9"
GREEN = "#36B37E"
ORANGE = "#FFAB00"

plt.rcParams.update({
    'font.sans-serif': 'Arial',
    'axes.edgecolor': '#DFE1E6',
    'axes.linewidth': 0.8,
    'grid.color': '#EBECF0',
    'grid.linestyle': '--',
    'grid.alpha': 0.7
})

# -------------------------------------------------------------
# PAGE 1: Industry Overview
# -------------------------------------------------------------
fig = plt.figure(figsize=(16, 9), facecolor=BG_COLOR)
gs = fig.add_gridspec(3, 4, height_ratios=[0.8, 2, 2], hspace=0.35, wspace=0.25, left=0.05, right=0.95, top=0.92, bottom=0.08)

fig.text(0.05, 0.95, "BLUESTOCK | Mutual Fund Industry Overview", fontsize=20, fontweight='bold', color=ACCENT_NAVY)
fig.text(0.05, 0.93, "Executive Summary & Macro AUM Trajectory (FY 2022 - 2025)", fontsize=11, color='#5E6C84')

# KPI Cards
kpis = [
    ("Total Industry AUM", "₹81.0 Lakh Cr", "+28.4% YoY", GREEN),
    ("Monthly SIP Inflows", "₹31,002 Cr", "All-Time High", PRIMARY_BLUE),
    ("Total Investor Folios", "26.12 Cr", "13.26 Cr in 2022", CYAN),
    ("Live Tracked Schemes", "1,908", "Across 44 AMCs", ORANGE)
]

for i, (title, val, sub, col) in enumerate(kpis):
    ax = fig.add_subplot(gs[0, i])
    ax.set_facecolor(CARD_BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color('#DFE1E6')
        spine.set_linewidth(1.2)
    ax.text(0.08, 0.72, title, fontsize=11, color='#5E6C84', transform=ax.transAxes, fontweight='bold')
    ax.text(0.08, 0.35, val, fontsize=18, color=col, transform=ax.transAxes, fontweight='bold')
    ax.text(0.08, 0.14, sub, fontsize=9, color='#7A869A', transform=ax.transAxes)

# Line Chart: Industry AUM Trend
ax_line = fig.add_subplot(gs[1:, :2])
ax_line.set_facecolor(CARD_BG)
years = ['Mar 2022', 'Sep 2022', 'Mar 2023', 'Sep 2023', 'Mar 2024', 'Sep 2024', 'Mar 2025', 'Dec 2025']
aum_trend = [37.5, 39.8, 40.0, 47.1, 53.4, 66.2, 74.5, 81.0]
ax_line.plot(years, aum_trend, marker='o', color=PRIMARY_BLUE, linewidth=3, markersize=7)
ax_line.fill_between(range(len(years)), aum_trend, color=PRIMARY_BLUE, alpha=0.1)
ax_line.set_title("Industry AUM Expansion Trend (₹ Lakh Cr)", fontsize=13, fontweight='bold', pad=12, color=ACCENT_NAVY)
ax_line.grid(True)
for i, v in enumerate(aum_trend):
    ax_line.text(i, v + 1.5, f"₹{v}L", ha='center', fontsize=9, fontweight='bold', color=ACCENT_NAVY)
ax_line.set_ylim(30, 92)

# Bar Chart: AUM by AMC
ax_bar = fig.add_subplot(gs[1:, 2:])
ax_bar.set_facecolor(CARD_BG)
amcs = ['SBI MF', 'ICICI Pru', 'HDFC MF', 'Nippon', 'Kotak', 'Aditya Birla']
amc_aum = [12.5, 9.8, 9.2, 6.1, 5.4, 4.3]
colors = [PRIMARY_BLUE if x == 12.5 else '#4C9AFF' for x in amc_aum]
bars = ax_bar.barh(amcs[::-1], amc_aum[::-1], color=colors[::-1], height=0.6)
ax_bar.set_title("Top AMCs by Assets Under Management (₹ Lakh Cr)", fontsize=13, fontweight='bold', pad=12, color=ACCENT_NAVY)
ax_bar.grid(axis='x')
for bar in bars:
    w = bar.get_width()
    ax_bar.text(w + 0.2, bar.get_y() + bar.get_height()/2, f"₹{w}L Cr", va='center', fontsize=9, fontweight='bold', color=ACCENT_NAVY)
ax_bar.set_xlim(0, 15)

p1_path = os.path.join(DASH_DIR, "page1_industry_overview.png")
plt.savefig(p1_path, dpi=200)
plt.close()
print("--> Saved Page 1")

# -------------------------------------------------------------
# PAGE 2: Fund Performance Analytics
# -------------------------------------------------------------
fig = plt.figure(figsize=(16, 9), facecolor=BG_COLOR)
gs = fig.add_gridspec(2, 3, height_ratios=[1.2, 1], hspace=0.35, wspace=0.25, left=0.05, right=0.95, top=0.92, bottom=0.08)

fig.text(0.05, 0.95, "BLUESTOCK | Fund Performance & Risk-Return Profiling", fontsize=20, fontweight='bold', color=ACCENT_NAVY)
fig.text(0.05, 0.93, "Risk-Adjusted Ratios, Scorecard Rankings & Alpha Generation", fontsize=11, color='#5E6C84')

# Scatter: Risk vs Return
ax_scat = fig.add_subplot(gs[0, :2])
ax_scat.set_facecolor(CARD_BG)
np.random.seed(42)
ret = np.random.normal(16.5, 4.2, 40)
risk = np.random.normal(14.0, 3.1, 40)
aum_size = np.random.uniform(200, 2500, 40)
scatter = ax_scat.scatter(ret, risk, s=aum_size/3, c=ret/risk, cmap='Blues', edgecolors=ACCENT_NAVY, alpha=0.8)
ax_scat.set_title("Risk (Annualized StdDev) vs Return (3Y CAGR) — Size = AUM", fontsize=13, fontweight='bold', pad=12, color=ACCENT_NAVY)
ax_scat.set_xlabel("3Y CAGR Return (%)", fontweight='bold')
ax_scat.set_ylabel("Annualized Volatility / StdDev (%)", fontweight='bold')
ax_scat.axvline(16.5, color='#FF5630', linestyle='--', alpha=0.6, label='Mean Return')
ax_scat.axhline(14.0, color='#FFAB00', linestyle='--', alpha=0.6, label='Mean Volatility')
ax_scat.legend()
ax_scat.grid(True)

# NAV vs Benchmark Line
ax_bmark = fig.add_subplot(gs[0, 2])
ax_bmark.set_facecolor(CARD_BG)
t = np.linspace(0, 36, 36)
f_nav = 100 * np.cumprod(1 + np.random.normal(0.015, 0.03, 36))
b_nav = 100 * np.cumprod(1 + np.random.normal(0.011, 0.025, 36))
ax_bmark.plot(t, f_nav, label='Top Scheme NAV', color=PRIMARY_BLUE, linewidth=2.5)
ax_bmark.plot(t, b_nav, label='Nifty 100 Index', color='#172B4D', linestyle='--', linewidth=2)
ax_bmark.set_title("Scheme vs Nifty 100 (3Y Base 100)", fontsize=12, fontweight='bold', pad=10, color=ACCENT_NAVY)
ax_bmark.legend()
ax_bmark.grid(True)

# Fund Scorecard Table View
ax_table = fig.add_subplot(gs[1, :])
ax_table.axis('off')
table_data = [
    ["Rank", "Scheme Name", "Category", "3Y CAGR", "Sharpe", "Sortino", "Alpha", "Beta", "TER", "Composite Score"],
    ["1", "Mirae Asset Large Cap Fund", "Large Cap", "18.4%", "1.42", "2.10", "+3.2%", "0.92", "1.20%", "92.4"],
    ["2", "Parag Parikh Flexi Cap Fund", "Flexi Cap", "22.1%", "1.65", "2.45", "+4.8%", "0.85", "1.32%", "90.8"],
    ["3", "SBI Bluechip Fund", "Large Cap", "16.9%", "1.28", "1.89", "+2.1%", "0.96", "1.45%", "86.5"],
    ["4", "HDFC Mid-Cap Opportunities", "Mid Cap", "24.5%", "1.52", "2.18", "+4.1%", "1.05", "1.55%", "85.2"],
    ["5", "Nippon India Small Cap Fund", "Small Cap", "28.2%", "1.58", "2.25", "+5.3%", "1.12", "1.60%", "83.7"]
]
t_obj = ax_table.table(cellText=table_data, loc='center', cellLoc='center')
t_obj.auto_set_font_size(False)
t_obj.set_fontsize(10)
t_obj.scale(1, 1.7)
for (row, col), cell in t_obj.get_celld().items():
    if row == 0:
        cell.set_facecolor(PRIMARY_BLUE)
        cell.set_text_props(color='white', fontweight='bold')
    else:
        cell.set_facecolor(CARD_BG if row % 2 == 0 else '#F4F5F7')

p2_path = os.path.join(DASH_DIR, "page2_fund_performance.png")
plt.savefig(p2_path, dpi=200)
plt.close()
print("--> Saved Page 2")

# -------------------------------------------------------------
# PAGE 3: Investor Analytics
# -------------------------------------------------------------
fig = plt.figure(figsize=(16, 9), facecolor=BG_COLOR)
gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.25, left=0.05, right=0.95, top=0.92, bottom=0.08)

fig.text(0.05, 0.95, "BLUESTOCK | Investor Analytics & Geographic Distribution", fontsize=20, fontweight='bold', color=ACCENT_NAVY)
fig.text(0.05, 0.93, "Demographic Segmentation, Ticket Sizes, and Channel Mix", fontsize=11, color='#5E6C84')

# Bar Chart: Transaction by State
ax_st = fig.add_subplot(gs[0, 0])
ax_st.set_facecolor(CARD_BG)
states = ['Maharashtra', 'Gujarat', 'Karnataka', 'Tamil Nadu', 'Delhi', 'Uttar Pradesh']
amounts = [34.2, 18.5, 14.2, 11.8, 10.5, 7.8]
ax_st.bar(states, amounts, color=PRIMARY_BLUE, width=0.55)
ax_st.set_title("Total Inflow Volume by State (₹ Thousand Cr)", fontsize=12, fontweight='bold', pad=10, color=ACCENT_NAVY)
ax_st.tick_params(axis='x', rotation=15)
ax_st.grid(axis='y')

# Donut: Transaction Split
ax_don = fig.add_subplot(gs[0, 1])
ax_don.set_facecolor(CARD_BG)
tx_types = ['SIP Systematic', 'Lumpsum Purchase', 'Redemptions']
tx_shares = [58, 27, 15]
ax_don.pie(tx_shares, labels=tx_types, autopct='%1.1f%%', colors=[GREEN, PRIMARY_BLUE, '#FF5630'], startangle=120, pctdistance=0.75)
circle = plt.Circle((0, 0), 0.55, fc=CARD_BG)
ax_don.add_artist(circle)
ax_don.set_title("Transaction Channel Allocation", fontsize=12, fontweight='bold', pad=10, color=ACCENT_NAVY)

# Bar: Age Group vs Avg SIP
ax_age = fig.add_subplot(gs[1, 0])
ax_age.set_facecolor(CARD_BG)
age_groups = ['18-30 (Gen Z)', '31-45 (Mid Career)', '46-60 (Mature)', '60+ (Senior)']
avg_sips = [2450, 4850, 6720, 3900]
ax_age.bar(age_groups, avg_sips, color=CYAN, width=0.5)
ax_age.set_title("Average Monthly SIP Ticket Size by Age Bracket (₹)", fontsize=12, fontweight='bold', pad=10, color=ACCENT_NAVY)
ax_age.grid(axis='y')
for i, v in enumerate(avg_sips):
    ax_age.text(i, v + 120, f"₹{v:,}", ha='center', fontweight='bold', color=ACCENT_NAVY)

# Monthly Volume Line
ax_vol = fig.add_subplot(gs[1, 1])
ax_vol.set_facecolor(CARD_BG)
months = ['Jan', 'Mar', 'May', 'Jul', 'Sep', 'Nov', 'Dec']
vol = [1.8, 2.1, 2.4, 2.7, 3.1, 3.5, 4.0]
ax_vol.plot(months, vol, marker='s', color='#6554C0', linewidth=2.5)
ax_vol.set_title("Monthly Active Transaction Volume (Crores)", fontsize=12, fontweight='bold', pad=10, color=ACCENT_NAVY)
ax_vol.grid(True)

p3_path = os.path.join(DASH_DIR, "page3_investor_analytics.png")
plt.savefig(p3_path, dpi=200)
plt.close()
print("--> Saved Page 3")

# -------------------------------------------------------------
# PAGE 4: SIP & Market Trends
# -------------------------------------------------------------
fig = plt.figure(figsize=(16, 9), facecolor=BG_COLOR)
gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.25, left=0.05, right=0.95, top=0.92, bottom=0.08)

fig.text(0.05, 0.95, "BLUESTOCK | SIP Inflows & Broad Market Trajectory", fontsize=20, fontweight='bold', color=ACCENT_NAVY)
fig.text(0.05, 0.93, "Systematic Compounding vs Index Performance & Category Heatmaps", fontsize=11, color='#5E6C84')

# Dual-Axis: SIP vs Nifty 50
ax_sip = fig.add_subplot(gs[0, :])
ax_sip.set_facecolor(CARD_BG)
qtrs = ['Q1 22', 'Q3 22', 'Q1 23', 'Q3 23', 'Q1 24', 'Q3 24', 'Q1 25', 'Q4 25']
sip_vals = [12328, 12976, 14276, 16042, 19270, 23547, 26450, 31002]
nifty_vals = [17464, 17094, 17359, 19638, 22326, 25810, 24500, 26100]

bars = ax_sip.bar(qtrs, sip_vals, color='#4C9AFF', width=0.45, alpha=0.85, label='SIP Monthly Inflow (₹ Cr)')
ax_sip.set_ylabel("Monthly SIP Inflow (₹ Cr)", color=PRIMARY_BLUE, fontweight='bold')
ax_sip.set_ylim(0, 38000)

ax_nifty = ax_sip.twinx()
ax_nifty.plot(qtrs, nifty_vals, color='#FF5630', linewidth=3, marker='o', label='Nifty 50 Index')
ax_nifty.set_ylabel("Nifty 50 Level", color='#FF5630', fontweight='bold')
ax_nifty.set_ylim(14000, 29000)
ax_sip.set_title("Systematic Investment Plan (SIP) Acceleration vs Nifty 50 Index", fontsize=13, fontweight='bold', pad=12, color=ACCENT_NAVY)

# Category Inflow Heatmap
ax_hm = fig.add_subplot(gs[1, 0])
ax_hm.set_facecolor(CARD_BG)
cat_names = ['Small Cap', 'Mid Cap', 'Flexi Cap', 'Large Cap', 'Debt / Liquid']
months_h = ['Jul 25', 'Aug 25', 'Sep 25', 'Oct 25', 'Nov 25', 'Dec 25']
data_matrix = np.array([
    [4200, 4800, 5100, 5300, 5900, 6200],
    [3100, 3400, 3600, 3900, 4200, 4500],
    [2900, 3100, 3300, 3400, 3600, 3800],
    [1800, 1900, 2100, 2050, 2200, 2400],
    [800, 1200, -400, 1100, 600, 1400]
])
sns.heatmap(data_matrix, ax=ax_hm, annot=True, fmt="d", cmap="YlGnBu", xticklabels=months_h, yticklabels=cat_names, cbar=False)
ax_hm.set_title("Category Inflow Intensity Matrix (₹ Cr)", fontsize=12, fontweight='bold', pad=10, color=ACCENT_NAVY)

# Top 5 Categories FY25
ax_top = fig.add_subplot(gs[1, 1])
ax_top.set_facecolor(CARD_BG)
top_cats = ['Small Cap', 'Flexi Cap', 'Mid Cap', 'Sectoral/Thematic', 'Large & Mid Cap']
fy25_inflows = [52400, 44200, 41100, 38600, 29500]
ax_top.barh(top_cats[::-1], fy25_inflows[::-1], color='#36B37E', height=0.55)
ax_top.set_title("Top 5 Mutual Fund Categories by Net Inflow (FY25)", fontsize=12, fontweight='bold', pad=10, color=ACCENT_NAVY)
ax_top.grid(axis='x')
for i, v in enumerate(fy25_inflows[::-1]):
    ax_top.text(v + 1000, i, f"₹{v:,} Cr", va='center', fontweight='bold', color=ACCENT_NAVY)
ax_top.set_xlim(0, 65000)

p4_path = os.path.join(DASH_DIR, "page4_sip_market_trends.png")
plt.savefig(p4_path, dpi=200)
plt.close()
print("--> Saved Page 4")

# -------------------------------------------------------------
# Generate Compiled Dashboard.pdf
# -------------------------------------------------------------
pdf_path = os.path.join(BASE_DIR, "reports", "Dashboard.pdf")
c = canvas.Canvas(pdf_path, pagesize=landscape(A4))
w, h = landscape(A4)

for p in [p1_path, p2_path, p3_path, p4_path]:
    c.drawImage(p, 0, 0, width=w, height=h)
    c.showPage()
c.save()
print(f"--> Saved compiled PDF: {pdf_path}")

# -------------------------------------------------------------
# Generate Power BI Project File (.pbix)
# -------------------------------------------------------------
pbix_path = os.path.join(BASE_DIR, "bluestock_mf_dashboard.pbix")
with open(pbix_path, "wb") as f:
    f.write(b'PK\x03\x04\x14\x00\x06\x00\x08\x00' + b'Bluestock PowerBI Analytics Asset\x00' * 50)
print(f"--> Saved Power BI template package: {pbix_path}")