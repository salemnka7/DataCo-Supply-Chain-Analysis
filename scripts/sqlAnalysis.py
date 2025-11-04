
import pandas as pd
import sqlite3

# Load the CSV into a DataFrame (use encoding='ISO-8859-1' because the file contains special characters)
df = pd.read_csv('DataCoSupplyChainDataset.csv', encoding='ISO-8859-1')

# Create a connection to a SQLite database (file: 'supply_chain.db')
conn = sqlite3.connect('supply_chain.db')

# Write the DataFrame to a SQL table
df.to_sql('supply_chain', conn, if_exists='replace', index=False)

# --- Cleaning with SQL ---

# 1. Handle missing values
# Fill Order_Zipcode with 0 if null
conn.execute("""
UPDATE supply_chain
SET "Order Zipcode" = 0
WHERE "Order Zipcode" IS NULL;
""")

# Delete rows with null in key fields (like Order_Id, Sales)
conn.execute("""
DELETE FROM supply_chain
WHERE "Order Id" IS NULL OR Sales IS NULL;
""")

# Set 'N/A' for description if empty
conn.execute("""
UPDATE supply_chain
SET "Product Description" = 'N/A'
WHERE "Product Description" IS NULL OR "Product Description" = '';
""")

# 2. Remove duplicates based on Order_Id
conn.execute("""
DELETE FROM supply_chain
WHERE rowid NOT IN (
    SELECT MIN(rowid)
    FROM supply_chain
    GROUP BY "Order Id"
);
""")

# 3. Fix inconsistencies
# Standardize country names (EE. UU. to USA)
conn.execute("""
UPDATE supply_chain
SET "Customer Country" = 'USA'
WHERE "Customer Country" = 'EE. UU.';
""")

conn.execute("""
UPDATE supply_chain
SET "Order Country" = 'USA'
WHERE "Order Country" = 'EE. UU.';
""")

# Convert texts to uppercase for consistency
conn.execute("""
UPDATE supply_chain
SET "Customer Segment" = UPPER("Customer Segment"),
    "Delivery Status" = UPPER("Delivery Status"),
    "Shipping Mode" = UPPER("Shipping Mode");
""")

# Handle negative profits (set to 0)
conn.execute("""
UPDATE supply_chain
SET "Order Profit Per Order" = 0
WHERE "Order Profit Per Order" < 0;
""")

# 4. Handle outliers
# Delete outlier shipments (>30 days or <0)
conn.execute("""
DELETE FROM supply_chain
WHERE "Days for shipping (real)" > 30 OR "Days for shipping (real)" < 0;
""")

# Cap product prices (above 2000 to 2000)
conn.execute("""
UPDATE supply_chain
SET "Product Price" = 2000
WHERE "Product Price" > 2000;
""")

# 5. Add derived column: Shipping_Delay
conn.execute("""
ALTER TABLE supply_chain ADD COLUMN Shipping_Delay INTEGER;
""")

conn.execute("""
UPDATE supply_chain
SET Shipping_Delay = "Days for shipping (real)" - "Days for shipment (scheduled)";
""")

# Commit changes after cleaning
conn.commit()

# Create a cleaned copy of the table
conn.execute("""
CREATE TABLE supply_chain_cleaned AS SELECT * FROM supply_chain;
""")

# --- Analysis with SQL ---

# 1. Total sales and profits by region
sales_by_region = pd.read_sql_query("""
SELECT 
    "Order Region",
    COUNT(*) AS total_orders,
    SUM(Sales) AS total_sales,
    SUM("Order Profit Per Order") AS total_profit,
    AVG("Order Profit Per Order") AS avg_profit_per_order
FROM supply_chain_cleaned
GROUP BY "Order Region"
ORDER BY total_sales DESC;
""", conn)

print("Total sales and profits by region:")
print(sales_by_region)

# 2. Late delivery rate by shipping mode
late_delivery_rate = pd.read_sql_query("""
SELECT 
    "Shipping Mode",
    COUNT(*) AS total_orders,
    SUM("Late_delivery_risk") AS late_deliveries,
    (SUM("Late_delivery_risk") / COUNT(*)) * 100 AS late_delivery_percentage
FROM supply_chain_cleaned
GROUP BY "Shipping Mode"
ORDER BY late_delivery_percentage DESC;
""", conn)

print("\nLate delivery rate by shipping mode:")
print(late_delivery_rate)

# 3. Average shipping delay by month
avg_delay_by_month = pd.read_sql_query("""
SELECT 
    strftime('%Y-%m', "order date (DateOrders)") AS order_month,
    AVG(Shipping_Delay) AS avg_delay_days,
    COUNT(*) AS total_orders
FROM supply_chain_cleaned
GROUP BY order_month
ORDER BY order_month;
""", conn)

print("\nAverage shipping delay by month:")
print(avg_delay_by_month)

# 4. Top 10 products by sales
top_products = pd.read_sql_query("""
SELECT 
    "Product Name",
    SUM("Order Item Quantity") AS total_quantity_sold,
    SUM(Sales) AS total_sales
FROM supply_chain_cleaned
GROUP BY "Product Name"
ORDER BY total_sales DESC
LIMIT 10;
""", conn)

print("\nTop 10 products by sales:")
print(top_products)

# 5. Customer segment performance
customer_segment_performance = pd.read_sql_query("""
SELECT 
    "Customer Segment",
    COUNT(DISTINCT "Customer Id") AS unique_customers,
    SUM(Sales) AS total_sales,
    AVG("Benefit per order") AS avg_benefit
FROM supply_chain_cleaned
GROUP BY "Customer Segment"
ORDER BY total_sales DESC;
""", conn)

print("\nCustomer segment performance:")
print(customer_segment_performance)

# 6. Fraud detection (suspected fraud orders)
fraud_detection = pd.read_sql_query("""
SELECT 
    "Order Region",
    COUNT(*) AS fraud_orders
FROM supply_chain_cleaned
WHERE "Order Status" = 'SUSPECTED_FRAUD'
GROUP BY "Order Region"
ORDER BY fraud_orders DESC;
""", conn)

print("\nFraud detection by region:")
print(fraud_detection)

# Additional Queries:

# 7. Total sales by year
sales_by_year = pd.read_sql_query("""
SELECT 
    strftime('%Y', "order date (DateOrders)") AS order_year,
    SUM(Sales) AS total_sales,
    COUNT(*) AS total_orders
FROM supply_chain_cleaned
GROUP BY order_year
ORDER BY order_year;
""", conn)

print("\nTotal sales by year:")
print(sales_by_year)

# 8. Average order value by customer segment
avg_order_value_by_segment = pd.read_sql_query("""
SELECT 
    "Customer Segment",
    AVG(Sales) AS avg_order_value,
    COUNT(*) AS total_orders
FROM supply_chain_cleaned
GROUP BY "Customer Segment"
ORDER BY avg_order_value DESC;
""", conn)

print("\nAverage order value by customer segment:")
print(avg_order_value_by_segment)

# 9. Top 5 customers by total spend
top_customers = pd.read_sql_query("""
SELECT 
    "Customer Id",
    "Customer Fname" || ' ' || "Customer Lname" AS customer_name,
    SUM(Sales) AS total_spend
FROM supply_chain_cleaned
GROUP BY "Customer Id"
ORDER BY total_spend DESC
LIMIT 5;
""", conn)

print("\nTop 5 customers by total spend:")
print(top_customers)

# 10. Delivery status distribution
delivery_status_dist = pd.read_sql_query("""
SELECT 
    "Delivery Status",
    COUNT(*) AS count,
    (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM supply_chain_cleaned)) AS percentage
FROM supply_chain_cleaned
GROUP BY "Delivery Status"
ORDER BY count DESC;
""", conn)

print("\nDelivery status distribution:")
print(delivery_status_dist)

# 11. Profit by department
profit_by_department = pd.read_sql_query("""
SELECT 
    "Department Name",
    SUM("Order Profit Per Order") AS total_profit,
    AVG("Order Profit Per Order") AS avg_profit
FROM supply_chain_cleaned
GROUP BY "Department Name"
ORDER BY total_profit DESC;
""", conn)

print("\nProfit by department:")
print(profit_by_department)

# 12. Sales by market
sales_by_market = pd.read_sql_query("""
SELECT 
    Market,
    SUM(Sales) AS total_sales,
    COUNT(*) AS total_orders
FROM supply_chain_cleaned
GROUP BY Market
ORDER BY total_sales DESC;
""", conn)

print("\nSales by market:")
print(sales_by_market)

# 13. Late delivery risk by region
late_risk_by_region = pd.read_sql_query("""
SELECT 
    "Order Region",
    AVG("Late_delivery_risk") * 100 AS late_risk_percentage
FROM supply_chain_cleaned
GROUP BY "Order Region"
ORDER BY late_risk_percentage DESC;
""", conn)

print("\nLate delivery risk by region:")
print(late_risk_by_region)

# 14. Quantity sold by category
quantity_by_category = pd.read_sql_query("""
SELECT 
    "Category Name",
    SUM("Order Item Quantity") AS total_quantity_sold
FROM supply_chain_cleaned
GROUP BY "Category Name"
ORDER BY total_quantity_sold DESC;
""", conn)

print("\nQuantity sold by category:")
print(quantity_by_category)

# 15. Orders by order status
orders_by_status = pd.read_sql_query("""
SELECT 
    "Order Status",
    COUNT(*) AS count
FROM supply_chain_cleaned
GROUP BY "Order Status"
ORDER BY count DESC;
""", conn)

print("\nOrders by order status:")
print(orders_by_status)

# 16. Shipping mode usage
shipping_mode_usage = pd.read_sql_query("""
SELECT 
    "Shipping Mode",
    COUNT(*) AS usage_count,
    (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM supply_chain_cleaned)) AS percentage
FROM supply_chain_cleaned
GROUP BY "Shipping Mode"
ORDER BY usage_count DESC;
""", conn)

print("\nShipping mode usage:")
print(shipping_mode_usage)

# Close the connection when done
conn.close()
