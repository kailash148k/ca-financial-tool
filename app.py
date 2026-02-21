import streamlit as st
import pandas as pd
import os
import io

# 1. INITIAL SETUP
st.set_page_config(page_title="CA Practice Manager - Final 2202", layout="wide")

# Ensure folders for data and templates exist
for folder in ["saved_clients", "templates"]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# 2. SIDEBAR: FIRM CATEGORY & DASHBOARD
st.sidebar.header("📂 Client List Dashboard")
all_files = [f for f in os.listdir("saved_clients") if f.endswith('.csv')]
if all_files:
    unique_firms = sorted(list(set([f.split('_20')[0].replace('_', ' ') for f in all_files])))
    st.sidebar.write(f"Total Firms Managed: **{len(unique_firms)}**")
    for firm in unique_firms:
        st.sidebar.markdown(f"🔹 {firm}")

st.sidebar.divider()
st.sidebar.header("🏢 Current Firm Settings")
company_name = st.sidebar.text_input("Company Name", "M/s Rudra Earthmovers")
address = st.sidebar.text_area("Address", "Udaipur, Rajasthan")
firm_type = st.sidebar.selectbox("Firm Category", ["Trading Firm", "Service Provider", "Manufacturing"])
selected_fy = st.sidebar.selectbox("Financial Year", ["2023-24", "2024-25", "2025-26"])

if st.sidebar.button("♻️ Load Category Default"):
    st.session_state.clear()
    st.rerun()

# 3. DYNAMIC TEMPLATE LOADER
def load_template(form_type, firm_cat):
    # Generates path based on Category: e.g., templates/Trading_Firm_PL.csv
    file_path = f"templates/{firm_cat.replace(' ', '_')}_{form_type}.csv"
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    
    # Generic starting point if no default saved
    if form_type == "PL":
        return pd.DataFrame({"Particulars": ["Sales", "Purchases", "Salaries", "Depreciation"], "Amount": [0.0]*4, "Add Back": [False]*4})
    return pd.DataFrame({"Particulars": ["Capital", "Creditors", "Debtors", "Cash"], "Amount": [0.0]*4})

# 4. DATA ENTRY
st.title(f"Financial Reporting: {company_name}")
t_input, t_report, t_analysis = st.tabs(["📝 Input Sheet", "📈 Final Reports", "🧮 Cash Profit Analysis"])

with t_input:
    st.info(f"Currently viewing **{firm_type}** template. Customize it and save as default below.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Profit & Loss Account")
        pl_ed = st.data_editor(load_template("PL", firm_type), key=f"pl_{firm_type}", num_rows="dynamic", use_container_width=True)
        if st.button(f"💾 Save as Default {firm_type} P&L"):
            pl_ed.to_csv(f"templates/{firm_type.replace(' ', '_')}_PL.csv", index=False)
            st.success(f"Default P&L for {firm_type} updated!")

    with c2:
        st.subheader("Balance Sheet")
        bs_ed = st.data_editor(load_template("BS", firm_type), key=f"bs_{firm_type}", num_rows="dynamic", use_container_width=True)
        if st.button(f"💾 Save as Default {firm_type} BS"):
            bs_ed.to_csv(f"templates/{firm_type.replace(' ', '_')}_BS.csv", index=False)
            st.success(f"Default BS for {firm_type} updated!")

    # Fixed Assets / Depreciation Section
    st.subheader("🛠️ Fixed Asset & Depreciation Chart")
    dep_ed = st.data_editor(pd.DataFrame({"Asset": ["Furniture"], "IT Block": ["Furniture (10%)"], "Opening": [0.0], "Additions": [0.0], "Deletions": [0.0]}), num_rows="dynamic", use_container_width=True)

    if st.button("🚀 SAVE CLIENT DATA"):
        file_path = f"saved_clients/{company_name.replace(' ', '_')}_{selected_fy}.csv"
        full_save = pd.concat([pl_ed, bs_ed], ignore_index=True)
        full_save.to_csv(file_path, index=False)
        st.success(f"Data saved for {company_name}!")
