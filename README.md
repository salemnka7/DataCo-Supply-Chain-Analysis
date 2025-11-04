# DataCo Smart Supply Chain Analysis & Predictive Modeling

A complete end-to-end AI and data analytics project combining Data Engineering, Machine Learning, and Business Intelligence to optimize the DataCo Supply Chain dataset.  
This project delivers actionable insights, predictive models, and interactive dashboards to support data-driven business decisions.

---

## Table of Contents

1. [Project Structure](#project-structure)  
2. [Objectives](#objectives)  
3. [Jupyter Notebook (main.ipynb)](#1-jupyter-notebook--mainipynb)  
4. [SQL Analysis (sqlAnalysis.py)](#2-sql-analysis--sqlanalysispy)  
5. [Data Cleaning Script (dataCleaning.py)](#3-data-cleaning-script--datacleaningpy)  
6. [Streamlit App (stremlitApp.py)](#4-streamlit-app--stremlitapppy)  
7. [Power BI Dashboard](#5-power-bi-dashboard)  
8. [Technologies Used](#6-technologies-used)  
9. [Setup Instructions](#7-setup-instructions)  
10. [Key Insights](#8-key-insights)  
11. [Conclusion](#9-conclusion)

---

## Project Structure

```
DataCo-Supply-Chain-Analysis
│
├── data
│ ├── raw/ → Original dataset (.csv)
│ └── processed/ → Cleaned dataset used in modeling
│
├── models/ → Trained & serialized ML models (.pkl)
│
├── notebooks/
│ └── main.ipynb → Core EDA, modeling, and evaluation notebook
│
├── scripts/
│ ├── dataCleaning.py → Python-based preprocessing
│ ├── sqlAnalysis.py → SQL data cleaning & aggregation
│ └── stremlitApp.py → Streamlit web app for real-time testing
│
├── dashboard/ → Power BI visuals and report (.pbix)
│
└── requirements.txt → Dependencies list
```

---

## Objectives

- Analyze supply chain data to uncover inefficiencies and performance patterns.  
- Build machine learning models for sales forecasting, fraud detection, and late delivery prediction.  
- Integrate insights into interactive dashboards and a deployable web app.  
- Enable data-driven decisions for logistics, finance, and customer operations.

---

## 1. Jupyter Notebook — main.ipynb

The main notebook performs the entire data science pipeline: data cleaning, analysis, model training, and evaluation.

### Step 1: Data Exploration
- Loaded and inspected `DataCoSupplyChainDataset.csv`.  
- Handled missing values, inconsistent data types, and irrelevant features.  
- Conducted initial visualizations for:  
  - Sales distribution  
  - Late delivery risk  
  - Profit per order  
  - Regional and segment-level performance  

### Step 2: Data Cleaning & Feature Engineering
- Created new features such as:  
  - `Shipping_Delay = Days for shipping (real) - Days for shipment (scheduled)`  
  - `Profit Margin (%) = (Order Profit Per Order / Sales) × 100`  
- Encoded categorical variables and scaled numeric ones using `StandardScaler`.

### Step 3: Exploratory Data Analysis (EDA)
- Examined seasonal sales trends and customer segmentation.  
- Identified performance differences between regions and markets.  
- Visualized correlations using `Matplotlib` and `Seaborn`.

### Step 4: Machine Learning Modeling
Three XGBoost models were trained:  

| Model | Task | Target | Type | Metric |  
|--------|------|---------|-------|---------|  
| xgb_sales_model | Predict Sales | Sales | Regression | R² = 0.91 |  
| xgb_fraud_model | Detect Fraud | Order Status | Classification | F1 = 0.88 |  
| xgb_late_model | Predict Late Delivery | Late_delivery_risk | Classification | ROC-AUC = 0.93 |  

### Step 5: Model Export
```python
joblib.dump(xgb_sales_model, 'models/xgboost_regressor_sales.pkl')
joblib.dump(xgb_fraud_model, 'models/xgboost_fraud.pkl')
joblib.dump(xgb_late_model, 'models/xgboost_late.pkl')
joblib.dump(scaler, 'models/scaler.pkl')
joblib.dump(label_encoders, 'models/label_encoders.pkl')
```

### Step 6: Insights
- Higher shipping delays in "Same Day" and "Second Class" shipping modes.  
- Certain regions exhibit higher fraud risk.  
- Profitability correlates strongly with "Customer Segment" and "Department Name".  

The notebook acts as the central pipeline that generates cleaned data, trains models, and powers both the Streamlit app and Power BI dashboard.

---

## 2. SQL Analysis — sqlAnalysis.py

Performs SQL-based data analysis using SQLite.  

Main operations:  
- Removal of duplicates and invalid entries.  
- Standardization of country and region names.  
- Aggregations for:  
  - Total Sales & Profit per Region  
  - Late Delivery Rate by Shipping Mode  
  - Customer Segment performance  
  - Fraud detection by Region  

Results are printed in structured tables and exported for Power BI visualization.

---

## 3. Data Cleaning Script — dataCleaning.py

Automates the preprocessing and feature engineering pipeline:  
- Handles missing and inconsistent data.  
- Renames columns to standardized format.  
- Performs scaling and encoding using saved encoders and scalers.  
- Outputs final cleaned datasets into `/data/processed/`.

---

## 4. Streamlit App — stremlitApp.py

An interactive web app built with Streamlit for real-time analytics and model prediction.  

### Features
- **Overview Page**:  
  Displays KPIs, distributions, and interactive summary charts.  
- **Model Testing Page**:  
  Allows users to input order details and instantly:  
  - Predict expected Sales  
  - Detect potential Fraud  
  - Predict Late Delivery Risk  

### Run Command
```bash
streamlit run scripts/stremlitApp.py
```

The app loads pre-trained XGBoost models and applies consistent preprocessing for reliable predictions.

---

## 5. Power BI Dashboard

The Power BI report (`supply chain.pbix`) consists of four professional pages built using the processed dataset.  

- **Page 1: Overview**  
  - KPIs: Total Sales, Profit, Margin %, On-Time Rate  
  - Sales by Market, Segment, and Over Time  
  - Geographic Sales Map  

- **Page 2: Delivery Performance**  
  - Late Deliveries by Shipping Mode  
  - Delivery Status Breakdown  
  - Delay Trend Analysis  

- **Page 3: Sales and Profit Analysis**  
  - Profit vs Sales by Segment  
  - Top Products and Departments  
  - Tree Map Visualization  

- **Page 4: Regional Insights**  
  - Regional Profitability Map  
  - KPI Table for Sales, Margin, and Delivery Rates  
  - Profit Margin Gauge  

---

## 6. Technologies Used

| Category | Tools |  
|----------|-------|  
| Programming | Python, SQL |  
| Libraries | Pandas, NumPy, Scikit-learn, XGBoost, Matplotlib, Seaborn, Joblib |  
| Visualization | Power BI, Streamlit |  
| Database | SQLite |  
| Environment | Virtualenv / Conda |  

---

## 7. Setup Instructions

```bash
# Clone the repository
git clone https://github.com/ahmed-salem-ai/DataCo-Supply-Chain.git

# Navigate to project directory
cd DataCo-Supply-Chain

# Create a virtual environment
python -m venv dataco_env
dataco_env\Scripts\activate

# Install required libraries
pip install -r requirements.txt

# Run the Streamlit app
streamlit run scripts/stremlitApp.py
```

---

## 8. Key Insights

- On-Time Delivery Rate: 84% overall  
- Most Profitable Market: Europe  
- Top Product Category: Technology Accessories  
- Highest Risk Region: LATAM  
- Best Model Accuracy: 91% (Sales Regression)  

---

## 9. Conclusion

This project demonstrates a complete data-to-decision workflow:  
- Data Cleaning and Preparation  
- Exploratory Analysis and Visualization  
- Predictive Modeling  
- Business Intelligence Dashboard  
- Interactive Deployment via Streamlit  

By integrating Python, SQL, Power BI, and Streamlit, this project transforms raw data into actionable business intelligence and predictive analytics.  

Developed by: Ahmed Salem  
Role: AI & Data Science Engineer
