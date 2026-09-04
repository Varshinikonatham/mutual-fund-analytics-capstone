-- 1. Top 5 funds by AUM / Performance
SELECT df.scheme_name, fp.expense_ratio
FROM fact_performance fp
JOIN dim_fund df ON fp.amfi_code = df.amfi_code
ORDER BY fp.expense_ratio ASC LIMIT 5;

-- 2. Average NAV per month for each scheme
SELECT amfi_code, strftime('%Y-%m', nav_date) AS month, ROUND(AVG(nav), 2) AS avg_nav
FROM fact_nav
GROUP BY amfi_code, month;

-- 3. SIP YoY transaction volume growth
SELECT strftime('%Y', transaction_date) AS yr, SUM(amount) AS total_sip_amount
FROM fact_transactions
WHERE transaction_type = 'SIP'
GROUP BY yr ORDER BY yr;

-- 4. Transactions summary by type
SELECT transaction_type, COUNT(*) AS txn_count, SUM(amount) AS total_volume
FROM fact_transactions
GROUP BY transaction_type;

-- 5. Funds with expense ratio < 1.0%
SELECT df.scheme_name, fp.expense_ratio
FROM fact_performance fp
JOIN dim_fund df ON fp.amfi_code = df.amfi_code
WHERE fp.expense_ratio < 1.0;

-- 6. Total redemption volume vs SIP volume
SELECT transaction_type, SUM(amount) AS total_amount, COUNT(*) AS transactions_count
FROM fact_transactions
GROUP BY transaction_type;

-- 7. Distribution of KYC status among transacting investors
SELECT kyc_status, COUNT(*) AS total_count
FROM fact_transactions
GROUP BY kyc_status;

-- 8. Top performing funds sample
SELECT df.scheme_name, fp.expense_ratio
FROM fact_performance fp
JOIN dim_fund df ON fp.amfi_code = df.amfi_code
LIMIT 5;

-- 9. Count of funds across categories
SELECT fund_category, COUNT(*) AS fund_count
FROM dim_fund
GROUP BY fund_category;

-- 10. NAV spread and range per scheme
SELECT amfi_code, MIN(nav) AS min_nav, MAX(nav) AS max_nav, ROUND(MAX(nav) - MIN(nav), 2) AS nav_spread
FROM fact_nav
GROUP BY amfi_code;
