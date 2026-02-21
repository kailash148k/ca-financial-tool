import streamlit as st
import pandas as pd
import os
import io

# 1. DIRECTORY & INITIAL SETUP
# This block fixes the OSError by ensuring folders exist on the server
for folder in ["saved_clients", "templates"]:
    if not os.path.exists(folder):
        os.makedirs(folder)

st.set_page_config(page_title="CA Practice Manager - Final 2202", layout="wide")

# 2. COMPREHENSIVE LIBRARIES
ALL_PL_HEADS = [
    "Sales", "Closing Stock", "Opening Stock", "Purchases", "Wages", "Carriage Inward", 
    "Factory Rent", "Customs Duty", "Salaries (Office)", "Office Rent", "Audit Fees", 
    "Interest on Loans", "Depreciation", "Discount Allowed", "Interest Received"
]

ALL_BS_HEADS = [
    "Proprietor's Capital", "Reserves and Surplus", "Secured Loans", "Unsecured Loans", 
    "Sundry Creditors", "Provision for Income Tax", "Fixed Assets: Gross Block", 
    "Sundry Debtors", "Cash-in-Hand", "Balance with Banks", "Loans and Advances"
]

IT_BLOCKS = {
    "Building - General (10%)": 0.10,
    "Furniture and Fittings (10%)": 0.10,
    "Plant & Machinery - General (15%)": 0.15,
    "Computers including software (40%)": 0.40,
    "Intangible Assets (25%)": 0.25
}

# 3. SIDEBAR: CLIENT DASHBOARD
st.sidebar.header("📂 Client List Dashboard")
all_files = [f for f in os.listdir("saved_clients") if f.endswith('.csv')]
if all_files:
    unique_firms = sorted(list(set([f.split('_20')[0].replace('_', ' ') for f in all_files])))
    st.sidebar.write(f"Total Firms: **{len(unique_firms)}**")
    for firm in unique_firms:
        st.sidebar.markdown(f"🔹 {firm}")

st.sidebar.divider()
st.sidebar.header("🏢 Firm Settings")
company_name = st.sidebar.text_input("Company Name", "M/s Rudra Earthmovers")
address = st.sidebar.text_area("Address", "Udaipur, Rajasthan")
firm_type = st.sidebar.selectbox("Firm Category", ["Trading Firm", "Service Provider", "Manufacturing"])
selected_fy = st.sidebar.selectbox("Financial Year", ["2023-24", "2024-25", "2025-26"])

if st.sidebar.button("♻️ Load Category Default"):
    st.session_state.clear()
    st.rerun()

# 4. TEMPLATE LOADER
def load_template(form_type, firm_cat):
    file_path = f"templates/{firm_cat.replace(' ', '_')}_{form_type}.csv"
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    # Default initial sets
    if form_type == "PL":
        return pd.DataFrame({"Particulars": ["Sales", "Purchases", "Salaries", "Depreciation"], "Amount": [0.0]*4, "Add Back": [False]*4})
    return pd.DataFrame({"Particulars": ["Proprietor's Capital", "Sundry Creditors", "Sundry Debtors", "Cash-in-Hand"], "Amount": [0.0]*4})

# 5. DATA ENTRY TABS
st.title(f"Financial Reporting: {company_name}")
t_input, t_report, t_analysis = st.tabs(["📝 Input Sheet", "📈 Final Reports", "🧮 Cash Profit Analysis"])

with t_input:
    st.info(f"Viewing **{firm_type}** template. Customize it and save as default for this category below.")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Profit & Loss Account")
        pl_ed = st.data_editor(load_template("PL", firm_type), key=f"pl_{firm_type}", num_rows="dynamic", use_container_width=True,
                               column_config={"Particulars": st.column_config.SelectboxColumn("Account Head", options=ALL_PL_HEADS, required=True)})
        if st.button(f"💾 Save as Default {firm_type} P&L"):
            pl_ed.to_csv(f"templates/{firm_type.replace(' ', '_')}_PL.csv", index=False)
            st.success("Template Saved!")

    with c2:
        st.subheader("Balance Sheet")
        bs_ed = st.data_editor(load_template("BS", firm_type), key=f"bs_{firm_type}", num_rows="dynamic", use_container_width=True,
                               column_config={"Particulars": st.column_config.SelectboxColumn("Account Head", options=ALL_BS_HEADS, required=True)})
        if st.button(f"💾 Save as Default {firm_type} BS"):
            bs_ed.to_csv(f"templates/{firm_type.replace(' ', '_')}_BS.csv", index=False)
            st.success("Template Saved!")

    st.subheader("🛠️ Fixed Asset & Depreciation Chart")
    dep_ed = st.data_editor(pd.DataFrame({"Asset": ["Furniture"], "IT Block": ["Furniture and Fittings (10%)"], "Opening": [0.0], "Additions": [0.0], "Deletions": [0.0]}), 
                            num_rows="dynamic", use_container_width=True,
                            column_config={"IT Block": st.column_config.SelectboxColumn("IT Block", options=list(IT_BLOCKS.keys()))})

    if st.button("🚀 SAVE CLIENT DATA"):
        file_path = f"saved_clients/{company_name.replace(' ', '_')}_{selected_fy}.csv"
        # Combine data for saving
        full_save = pd.concat([pl_ed, bs_ed, dep_ed.assign(Group="FA")], ignore_index=True)
        full_save.to_csv(file_path, index=False)
        st.success(f"Successfully saved {company_name} for {selected_fy}!")

# 6. ANALYSIS TAB: RESTORED AVG CASH PROFIT
with t_analysis:
    st.header("Average Cash Profit Calculation")
    years_to_avg = st.multiselect("Select years to include", ["2023-24", "2024-25", "2025-26"])
    if st.button("🧮 Calculate Average Cash Profit"):
        cp_vals = []
        for y in years_to_avg:
            path = f"saved_clients/{company_name.replace(' ', '_')}_{y}.csv"
            if os.path.exists(path):
                data = pd.read_csv(path)
                # Filter for items where 'Add Back' was ticked
                add_back = data[data['Add Back'] == True]['Amount'].sum()
                cp_vals.append(add_back) 
        if cp_vals:
            st.metric("Average Cash Profit", f"₹{sum(cp_vals)/len(cp_vals):,.2f}")
        else:
            st.warning("No data found for selected years.")
