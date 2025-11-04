import pandas as pd

# Load the dataset (replace with your file path)
df = pd.read_csv('DataCoSupplyChain_cleaned.csv', encoding='ISO-8859-1')  # Use 'latin-1' if there are encoding issues; otherwise, default to 'utf-8'

# Preview the data
print(df.head())  # First 5 rows
print(df.info())  # Data types and non-null counts
print(df.shape)   # Rows and columns

# Step 2.1: Standardize column names (lowercase, replace spaces/special chars with underscores)
df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('-', '_')

# Step 2.2: Remove irrelevant or anonymized columns (based on dataset analysis)
irrelevant_cols = ['customer_email', 'customer_password', 'product_description', 'product_image', 'customer_fname', 'customer_lname']
df = df.drop(columns=irrelevant_cols, errors='ignore')  # 'errors=ignore' skips if columns don't exist

# Step 2.3: Handle missing values (e.g., drop rows with missing critical data or fill with defaults)
df = df.dropna(subset=['order_id', 'sales'])  # Drop rows missing key columns
df['customer_zipcode'] = df['customer_zipcode'].fillna(0)  # Fill numeric NaNs with 0 or mean/median as needed

# Step 2.4: Convert data types
# Dates (assuming columns like 'order_date_dateorders' and 'shipping_date_dateorders')
df['order_date_dateorders'] = pd.to_datetime(df['order_date_dateorders'], errors='coerce')
df['shipping_date_dateorders'] = pd.to_datetime(df['shipping_date_dateorders'], errors='coerce')

# Ensure numeric columns
numeric_cols = ['days_for_shipping_real', 'days_for_shipment_scheduled', 'benefit_per_order', 'sales_per_customer',
                'late_delivery_risk', 'order_item_discount', 'order_item_discount_rate', 'order_item_product_price',
                'order_item_profit_ratio', 'order_item_quantity', 'sales', 'order_item_total', 'order_profit_per_order',
                'product_price']
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')

# Step 2.5: Remove duplicates based on unique identifier (e.g., order_id)
df = df.drop_duplicates(subset=['order_id'])

# Step 2.6: Engineer new features (e.g., for supply chain analysis)
df['shipping_lead_time_variance'] = df['days_for_shipping_real'] - df['days_for_shipment_scheduled']
df['is_late'] = (df['shipping_lead_time_variance'] > 0).astype(int)
df['order_processing_time_days'] = (df['shipping_date_dateorders'] - df['order_date_dateorders']).dt.days

# Step 2.7: Handle outliers (optional: e.g., cap extreme values in sales)
q1 = df['sales'].quantile(0.25)
q3 = df['sales'].quantile(0.75)
iqr = q3 - q1
df['sales'] = df['sales'].clip(lower=q1 - 1.5 * iqr, upper=q3 + 1.5 * iqr)  # Winsorize outliers

# Final preview after cleaning
print(df.info())
print(df.describe())  # Summary stats

# Save as CSV (lightweight, fast import in Power BI)
cleaned_file_path = 'path/to/save/cleaned_data.csv'  # e.g., 'C:/Downloads/cleaned_DataCoSupplyChainDataset.csv'
df.to_csv(cleaned_file_path, index=False)  # index=False avoids adding an extra row index column

# Alternatively, save as Excel (if you need sheets or formatting)
df.to_excel('path/to/save/cleaned_data.xlsx', index=False)