import streamlit as st
import pandas as pd
import os
import io

# 1. INITIAL SETUP
st.set_page_config(page_title="CA Practice Manager - Udaipur", layout="wide")

if not os.path.exists("saved_clients"):
    os.makedirs("saved_clients")

# 2. INCOME TAX DEPRECIATION RATES
DEP_RATES = {
    "Furniture and Fittings": 0.10,
    "Plant and Machinery (General)": 0.15,
    "Computers (including software)": 0.40,
    "Books (Annual/Other)": 0.40,
    "Land and Building (Residential)": 0.05,
    "Land and Building (Commercial/General)": 0.10,
    "Pollution Control Equipment": 0.40,
    "Intangible Assets": 0.25
}

# 3. SIDEBAR: CLIENT DASHBOARD
st.sidebar.header("📂 Client List Dashboard")
all_files = os.listdir("saved_clients")
if all_files:
    unique_firms = sorted(list(set([f.split('_20')[0].replace('_', ' ') for f in all_files])))
    st.sidebar.write(f"Total Firms Managed: **{len(unique_firms)}**")
    for firm in unique_firms:
        st.sidebar.markdown(f"🔹 {firm}")
else:
    st.sidebar.info("No saved clients yet.")

st.sidebar.divider()
st.sidebar.header("🏢 Current Firm Settings")
company_name = st.sidebar.text_input("Company Name", "M/s Rudra Earthmovers")
address = st.sidebar.text_area("Address", "Udaipur, Rajasthan")
selected_fy = st.sidebar.selectbox("Financial Year", ["2021-22", "2022-23", "2023-24", "2024-25", "2025-26"])

if st.sidebar.button("♻️ Reset & New Firm"):
    st.session_state.clear()
    st.rerun()

# 4. DATA TEMPLATES
def get_pl_template():
    return pd.DataFrame({
        "Particulars": ["Sales", "Opening Stock", "Purchase", "Closing Stock", "Direct Expenses", "Interest Income", "Commission", "Salary", "Office Expenses", "Depreciation"],
        "Group": ["Trading", "Trading", "Trading", "Trading", "Trading", "Income", "Income", "Expense", "Expense", "Expense"],
        "Add Back": [False] * 10,
        "Amount": [0.0] * 10
    })

def get_bs_template():
    return pd.DataFrame({
        "Particulars": ["Promoter Capital", "Bank Loan", "Sundry Creditors", "Duties & Taxes", "Sundry Debtors", "Cash-in-Hand", "Bank Accounts"],
        "Group": ["Liability", "Liability", "Liability", "Liability", "Asset", "Asset", "Asset"],
        "Amount": [0.0] * 7
    })

def get_dep_template():
    return pd.DataFrame({
        "Asset Name": ["Furniture", "Computers"],
        "Type": ["Furniture and Fittings", "Computers (including software)"],
        "Opening WDV": [0.0, 0.0],
        "Additions > 180 Days": [0.0, 0.0],
        "Additions < 180 Days": [0.0, 0.0],
        "Deletions": [0.0, 0.0]
    })

# 5. DATA ENTRY TABS
st.title(f"Financial Reporting: {company_name}")
tab_entry, tab_report = st.tabs(["📝 Input Sheet", "📈 Final Reports & Analysis"])

with tab_entry:
    col_pl, col_bs = st.columns(2)
    with col_pl:
        st.subheader("Profit & Loss Account")
        pl_ed = st.data_editor(get_pl_template(), key="pl_key", num_rows="dynamic", use_container_width=True)
    with col_bs:
        st.subheader("Balance Sheet (Liabs & Assets)")
        bs_ed = st.data_editor(get_bs_template(), key="bs_key", num_rows="dynamic", use_container_width=True)

    st.subheader("🛠️ Fixed Asset & Depreciation Chart")
    dep_ed = st.data_editor(get_dep_template(), key="dep_key", num_rows="dynamic", use_container_width=True)

    if st.button("💾 SAVE ALL FIRM DATA"):
        file_path = f"saved_clients/{company_name.replace(' ', '_')}_{selected_fy}.csv"
        save_df = pd.concat([pl_ed, bs_ed, dep_ed.assign(Group="FA_Schedule")], ignore_index=True)
        save_df.to_csv(file_path, index=False)
        st.success(f"Successfully saved {company_name} for {selected_fy}!")

# 6. REPORT GENERATION
with tab_report:
    if st.button("📊 GENERATE FINAL P&L AND BALANCE SHEET"):
        # Calc Depreciation
        dep_results = []
        tot_dep = 0
        for _, row in dep_ed.iterrows():
            rate = DEP_RATES.get(row['Type'], 0.15)
            d1 = (row['Opening WDV'] + row['Additions > 180 Days'] - row['Deletions']) * rate
            d2 = row['Additions < 180 Days'] * (rate / 2)
            cur_dep = d1 + d2
            tot_dep += cur_dep
            dep_results.append({"Asset": row['Asset Name'], "Opening": row['Opening WDV'], "Depreciation": cur_dep, "Closing WDV": (row['Opening WDV'] + row['Additions > 180 Days'] + row['Additions < 180 Days'] - row['Deletions']) - cur_dep})
        
        st.subheader("Depreciation Schedule (IT Act)")
        st.table(pd.DataFrame(dep_results))
        st.success(f"Total Depreciation to P&L: ₹{tot_dep:,.2f}")

    # EXCEL EXPORT [Requires xlsxwriter in requirements.txt]
    output = io.BytesIO()
    try:
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            pl_ed.to_excel(writer, sheet_name='P_and_L')
            bs_ed.to_excel(writer, sheet_name='Balance_Sheet')
            pd.DataFrame(dep_results if 'dep_results' in locals() else []).to_excel(writer, sheet_name='Dep_Chart')
        
        st.download_button(
            label="📥 Export Full Report to Excel",
            data=output.getvalue(),
            file_name=f"{company_name}_{selected_fy}_Report.xlsx",
            mime="application/vnd.ms-excel"
        )
    except Exception as e:
        st.warning("Generate the report first to enable the Excel download.")
