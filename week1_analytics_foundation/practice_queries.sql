-- ====================================================================
-- Week 1: SQL Practice Queries for Data Analysis
-- Objective: Customer Orders, Revenue, and Product Performance Analysis
-- ====================================================================

-- 1. SELECT, WHERE, ORDER BY
-- Retrieve top 10 highest value completed transactions in the South region
SELECT 
    Order_ID, 
    Date, 
    Customer_Name, 
    Product_Category, 
    Net_Revenue 
FROM sales_transactions
WHERE Region = 'South' AND Net_Revenue > 50000
ORDER BY Net_Revenue DESC
LIMIT 10;

-- 2. GROUP BY, HAVING, and Aggregate Functions
-- Category level performance with total revenue exceeding 2,000,000
SELECT 
    Product_Category,
    COUNT(Order_ID) AS Total_Orders,
    SUM(Units_Sold) AS Total_Units,
    SUM(Net_Revenue) AS Total_Net_Revenue,
    ROUND(AVG(Net_Revenue), 2) AS Avg_Order_Value,
    ROUND(SUM(Profit) / SUM(Net_Revenue) * 100, 2) AS Profit_Margin_Pct
FROM sales_transactions
GROUP BY Product_Category
HAVING SUM(Net_Revenue) >= 2000000
ORDER BY Total_Net_Revenue DESC;

-- 3. Multi-table JOINs (Customers & Orders)
SELECT 
    c.Customer_ID,
    c.Customer_Name,
    c.Segment,
    COUNT(o.Order_ID) AS Lifetime_Orders,
    SUM(o.Net_Revenue) AS Lifetime_Spend
FROM customers c
INNER JOIN orders o ON c.Customer_ID = o.Customer_ID
GROUP BY c.Customer_ID, c.Customer_Name, c.Segment
ORDER BY Lifetime_Spend DESC;

-- 4. Subquery: Find customers generating above-average net revenue
SELECT 
    Customer_Name, 
    Region, 
    Net_Revenue
FROM sales_transactions
WHERE Net_Revenue > (
    SELECT AVG(Net_Revenue) FROM sales_transactions
)
ORDER BY Net_Revenue DESC;

-- 5. Window Functions: Revenue Ranking & Running Totals
SELECT 
    Date,
    Region,
    Sales_Rep,
    Net_Revenue,
    RANK() OVER (PARTITION BY Region ORDER BY Net_Revenue DESC) AS Regional_Rank,
    SUM(Net_Revenue) OVER (PARTITION BY Region ORDER BY Date) AS Cumulative_Regional_Revenue,
    ROUND(Net_Revenue / SUM(Net_Revenue) OVER (PARTITION BY Region) * 100, 2) AS Regional_Revenue_Contribution_Pct
FROM sales_transactions
ORDER BY Region, Regional_Rank;
