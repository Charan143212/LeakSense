import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest

# --- Page Configuration ---
st.set_page_config(
    page_title="LeakSense Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# --- App Header ---
st.title("🛡️ LeakSense: Revenue Leakage Detection & Prescriptive Engine")
st.markdown("**Team Salaar** | Interactive Risk Analysis & Executive Audit Playbook")
st.markdown("---")

# --- Sidebar Input Options ---
st.sidebar.header("📥 Provide Input Data")
input_mode = st.sidebar.radio("Choose Input Method:", ["Upload Dataset (CSV)", "Live Single Transaction Input"])

# Cache data processing
@st.cache_data
def process_base_data(file):
    if file is not None:
        df_master = pd.read_csv(file)
    else:
        # Default simulated dataset if no file uploaded
        np.random.seed(42)
        n_rows = 1000
        df_master = pd.DataFrame({
            'transaction_id': [f"TX{str(i).zfill(5)}" for i in range(n_rows)],
            'customer_id': [f"CU{str(np.random.randint(1, 200)).zfill(5)}" for i in range(n_rows)],
            'product_id': [f"PR{str(np.random.randint(1, 50)).zfill(5)}" for i in range(n_rows)],
            'quantity': np.random.choice([1, 2, 3, 4, 5, 50], size=n_rows, p=[0.3, 0.3, 0.2, 0.1, 0.08, 0.02]),
            'unit_price': np.random.uniform(10, 400, size=n_rows),
            'discount_pct': np.random.choice([0.0, 0.05, 0.1, 0.15, 0.2, 0.8], size=n_rows, p=[0.5, 0.2, 0.15, 0.1, 0.03, 0.02]),
            'status': np.random.choice(['Completed', 'Returned', 'Cancelled'], size=n_rows, p=[0.7, 0.15, 0.15]),
            'category': np.random.choice(['Electronics', 'Home', 'Grocery', 'Fashion'], size=n_rows)
        })
    
    for col in ['quantity', 'unit_price', 'discount_pct']:
        if col in df_master.columns:
            df_master[col] = df_master[col].fillna(df_master[col].median())
        else:
            df_master[col] = 1.0
            
    if 'net_revenue' not in df_master.columns:
        df_master['net_revenue'] = df_master['quantity'] * df_master['unit_price'] * (1 - df_master['discount_pct'])
        
    return df_master

if input_mode == "Upload Dataset (CSV)":
    uploaded_file = st.sidebar.file_uploader("Upload your Transaction CSV file", type=["csv"])
    df = process_base_data(uploaded_file)
    
    # Model Controls
    contamination_rate = st.sidebar.slider("Select Anomaly Contamination Rate", 0.01, 0.15, 0.05, 0.01)
    
    # ML Pipeline
    features = ['quantity', 'unit_price', 'discount_pct']
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[features])
    
    iso = IsolationForest(contamination=contamination_rate, random_state=42)
    df['anomaly'] = iso.fit_predict(X_scaled)
    
    anomalies_df = df[df['anomaly'] == -1]
    total_risk_revenue = anomalies_df['net_revenue'].sum()
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Transactions Processed", f"{len(df):,}")
    col2.metric("High-Risk Leaks Flagged", f"{len(anomalies_df):,}")
    col3.metric("Net Revenue at Risk", f"${total_risk_revenue:,.2f}")
    col4.metric("Model Selected", "Isolation Forest")
    
    st.markdown("---")
    
    # Tabs for Visuals & Playbook
    tab1, tab2 = st.tabs(["📊 Distributions & Risk", "📋 Executive Playbook & Data"])
    
    with tab1:
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
        sns.histplot(df['quantity'], kde=True, ax=axes[0], color='teal')
        axes[0].set_title("Distribution Check: Quantity")
        sns.histplot(df['unit_price'], kde=True, ax=axes[1], color='teal')
        axes[1].set_title("Distribution Check: Unit Price")
        sns.histplot(df['discount_pct'], kde=True, ax=axes[2], color='teal')
        axes[2].set_title("Distribution Check: Discount %")
        st.pyplot(fig)
        
    with tab2:
        c_left, c_right = st.columns(2)
        with c_left:
            st.subheader("📋 Executive Decision Playbook")
            st.markdown("""
            1. **Immediate Audit:** Prioritize auditing flagged transactions for pricing errors or unauthorized discounts.
            2. **Quality Control:** Focus on high-return categories to minimize losses.
            3. **Supply Chain Sync:** Align lead times with sales velocity.
            """)
            export_cols = [c for c in ['transaction_id', 'customer_id', 'product_id', 'status', 'net_revenue', 'quantity'] if c in anomalies_df.columns]
            st.download_button("📥 Download Audit CSV", anomalies_df[export_cols].to_csv(index=False), "leaksense_audit.csv", "text/csv")
        with c_right:
            st.subheader("🚨 Flagged Anomalies Preview")
            st.dataframe(anomalies_df[export_cols].head(10), use_container_width=True)

else:
    # Live Single Transaction Input Mode
    st.header("⚡ Live Transaction Risk Analyzer")
    st.markdown("Input custom values below to test how **LeakSense** analyzes and scores a single transaction in real-time.")
    
    col_in1, col_in2, col_in3 = st.columns(3)
    with col_in1:
        input_qty = st.number_input("Quantity Purchased", min_value=1, max_value=100, value=2)
    with col_in2:
        input_price = st.number_input("Unit Price ($)", min_value=1.0, max_value=1000.0, value=250.0)
    with col_in3:
        input_disc = st.slider("Discount Percentage", min_value=0.0, max_value=0.50, value=0.10, step=0.01)
        
    if st.button("Run Leak Analysis"):
        # Train a quick model on baseline reference data to evaluate the custom input
        base_df = process_base_data(None)
        features = ['quantity', 'unit_price', 'discount_pct']
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(base_df[features])
        
        iso = IsolationForest(contamination=0.05, random_state=42)
        iso.fit(X_scaled)
        
        # Scale and predict for the single user input
        single_input = pd.DataFrame([[input_qty, input_price, input_disc]], columns=features)
        single_scaled = scaler.transform(single_input)
        prediction = iso.predict(single_scaled)[0] # -1 means anomaly, 1 means normal
        
        calc_net_rev = input_qty * input_price * (1 - input_disc)
        
        st.markdown("### 🔍 Analysis Result:")
        if prediction == -1:
            st.error(f"🚨 **HIGH RISK LEAK DETECTED!** (Anomaly Score Flagged)")
            st.markdown(f"**Net Revenue Exposure:** `${calc_net_rev:,.2f}`")
            st.markdown("**Recommendation:** This transaction falls outside normal operational boundaries (unusual combination of quantity, price, or high discount). Flag for **Immediate Pricing Audit**.")
        else:
            st.success(f"✅ **NORMAL TRANSACTION** (Within Expected Parameters)")
            st.markdown(f"**Net Revenue:** `${calc_net_rev:,.2f}`")
            st.markdown("**Status:** No anomalous risk patterns detected.")