import streamlit as st
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------------
# Load dataset
# -------------------------
@st.cache_data
def load_data():
    return pd.read_csv('G:\Projects\Analyzing the DataCo Smart Supply Chain Dataset\data\processed\DataCoSupplyChain_cleaned.csv', encoding='ISO-8859-1')

df = load_data()

# -------------------------
# Load saved objects
# -------------------------
scaler = joblib.load(r'G:\Projects\Analyzing the DataCo Smart Supply Chain Dataset\models\scaler.pkl')  # StandardScaler
xgb_sales_model = joblib.load(r'G:\Projects\Analyzing the DataCo Smart Supply Chain Dataset\models\xgboost_regressor_sales.pkl')
xgb_fraud_model = joblib.load(r'G:\Projects\Analyzing the DataCo Smart Supply Chain Dataset\models\xgboost_fraud.pkl')
xgb_late_model = joblib.load(r'G:\Projects\Analyzing the DataCo Smart Supply Chain Dataset\models\xgboost_late.pkl')
le_dict = joblib.load(r'G:\Projects\Analyzing the DataCo Smart Supply Chain Dataset\models\label_encoders.pkl')  # Dictionary of LabelEncoders

# -------------------------
# Sidebar navigation
# -------------------------
st.sidebar.title("Supply Chain Dashboard")
page = st.sidebar.selectbox("Select Page", ["Overview", "Model Testing"])

# -------------------------
# Overview Page (Enhanced)
# -------------------------
if page == "Overview":
    st.title("DataCo Supply Chain Overview")
    
    st.subheader("Data Sample")
    st.dataframe(df.head(10))
    
    st.subheader("Distribution of Late Delivery Risk")
    fig, ax = plt.subplots()
    sns.countplot(x='Late_delivery_risk', data=df, palette='Set2', ax=ax)
    ax.set_title("Number of Late vs On-Time Deliveries")
    st.pyplot(fig)
    
    st.subheader("Delivery Status Breakdown")
    fig, ax = plt.subplots(figsize=(8,5))
    sns.countplot(x='Delivery Status', data=df, order=df['Delivery Status'].value_counts().index, palette='Set1', ax=ax)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    st.pyplot(fig)
    
    st.subheader("Shipping Mode vs Late Risk")
    fig, ax = plt.subplots(figsize=(6,4))
    sns.barplot(x='Shipping Mode', y='Late_delivery_risk', data=df, palette='coolwarm', ax=ax)
    ax.set_title("Average Late Risk by Shipping Mode")
    st.pyplot(fig)
    
    st.subheader("Sales by Market")
    fig, ax = plt.subplots(figsize=(8,4))
    sns.boxplot(x='Market', y='Sales', data=df, palette='Set3', ax=ax)
    ax.set_title("Sales Distribution by Market")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    st.pyplot(fig)
    
    st.subheader("Top 10 City by Total Sales")
    top_customers = df.groupby('Customer City')['Sales'].sum().sort_values(ascending=False).head(10)
    st.bar_chart(top_customers)
    
    st.subheader("Correlation Heatmap of Numeric Features")
    numeric_df = df.select_dtypes(include=['float64','int64'])
    corr = numeric_df.corr()
    fig, ax = plt.subplots(figsize=(10,8))
    sns.heatmap(corr, annot=False, cmap='coolwarm', ax=ax)
    st.pyplot(fig)
    
    st.subheader("Sales Trend Over Time")
    df['order date (DateOrders)'] = pd.to_datetime(df['order date (DateOrders)'])
    sales_over_time = df.groupby(df['order date (DateOrders)'].dt.to_period('M'))['Sales'].sum()
    sales_over_time.index = sales_over_time.index.to_timestamp()
    st.line_chart(sales_over_time)
    
    st.subheader("Top 10 Products by Sales")
    top_products = df.groupby('Product Name')['Sales'].sum().sort_values(ascending=False).head(10)
    st.bar_chart(top_products)
    
    st.subheader("Late Delivery Risk by Region")
    late_by_region = df.groupby('Order Region')['Late_delivery_risk'].mean().sort_values(ascending=False)
    st.bar_chart(late_by_region)
    
    st.subheader("Interactive Scatter: Sales vs. Order Item Total")
    fig, ax = plt.subplots()
    sns.scatterplot(x='Order Item Total', y='Sales', hue='Late_delivery_risk', data=df.sample(1000), ax=ax)
    st.pyplot(fig)


# -------------------------
# Model Testing
# -------------------------
elif page == "Model Testing":
    st.title("Test Models with Custom Input (Simplified)")
    task = st.selectbox("Select Task", ["Sales Forecasting", "Fraud Prediction", "Late Delivery Prediction"])
    
    st.subheader("Enter Key Feature Values (Other features are set to default)")
    
    # --- Key categorical inputs ---
    type_input_raw = st.selectbox("Type", le_dict['Type'].classes_)
    shipping_mode_raw = st.selectbox("Shipping Mode", le_dict['Shipping Mode'].classes_)
    
    type_input = le_dict['Type'].transform([type_input_raw])[0]
    shipping_mode = le_dict['Shipping Mode'].transform([shipping_mode_raw])[0]
    
    # --- Key numeric inputs ---
    days_shipping_real = st.number_input("Days for shipping (real)", 0)
    days_shipping_sched = st.number_input("Days for shipment (scheduled)", 0)
    sales_per_customer = st.number_input("Sales per customer", 0.0)
    
    # --- Default values for other features ---
    category_id = 0
    customer_id = 0
    department_id = 0
    latitude = 0.0
    longitude = 0.0
    order_id = 0
    order_item_discount = 0.0
    order_item_discount_rate = 0.0
    order_item_product_price = 0.0
    order_item_quantity = 0
    product_card_id = 0
    product_category_id = 0
    product_price = 0.0
    order_year = 2023
    order_month = 1
    processing_time = days_shipping_real  # تقريبي
    
    # --- Arrange all features in correct order ---
    input_data = np.array([[type_input, days_shipping_real, days_shipping_sched, sales_per_customer,
                            category_id, customer_id, department_id, latitude, longitude, order_id,
                            order_item_discount, order_item_discount_rate, order_item_product_price,
                            order_item_quantity, product_card_id, product_category_id, product_price,
                            shipping_mode, order_year, order_month, processing_time]])
    
    scaled_input = scaler.transform(input_data)
    
    if st.button("Predict"):
        if task == "Sales Forecasting":
            pred = xgb_sales_model.predict(scaled_input)
            st.success(f"Predicted Sales: ${pred[0]:.2f}")
        elif task == "Fraud Prediction":
            pred = xgb_fraud_model.predict(scaled_input)
            st.success(f"Fraud Prediction: {'Yes' if pred[0]==1 else 'No'}")
        elif task == "Late Delivery Prediction":
            pred = xgb_late_model.predict(scaled_input)
            st.success(f"Late Delivery Prediction: {'Yes' if pred[0]==1 else 'No'}")

