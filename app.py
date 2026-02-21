import streamlit as st
import pandas as pd
import os
import io

# 1. INITIAL SETUP
st.set_page_config(page_title="CA Practice Manager - Final 2202", layout="wide")

if not os.path.exists("saved_clients"):
    os.makedirs("saved_clients")

# 2. COMPREHENSIVE LIBRARIES
TRADING_PL_HEADS = [
    "Opening Stock", "Purchases", "Purchases Returns", "Wages", "Carriage Inward", "Freight Inward",
    "Factory Rent", "Factory Lighting", "Customs Duty", "Octroi Duty", "Import Duty", "Dock Charges",
    "Manufacturing Expenses", "Fuel and Power", "Royalty on Production", "Packing Expenses", "Lorry Hire",
    "Sales", "Sales Returns", "Closing Stock", "Salaries (Office)", "Office Rent", "Printing and Stationery",
    "Postage", "Telephone Expenses", "Legal Charges", "Audit Fees", "Bank Charges", "Repairs and Maintenance",
    "Advertising", "Carriage Outward", "Bad Debts", "Interest on Loans", "Interest on Capital", "Depreciation",
    "Charity and Donations", "Rent Received", "Interest Received", "Commission Received", "Discount Received"
]

BALANCE_SHEET_HEADS = [
    "Proprietor's Capital", "Partner's Capital", "Share Capital", "Equity Share Capital", "Preference Share Capital",
    "Revaluation Reserve", "Capital Reserve", "Statutory Reserve", "General Reserve", "Securities Premium",
    "Surplus (P&L Balance)", "Foreign Currency Loans", "Rupee Loans from Banks", "Rupee Loans from Others",
    "Term Loans", "Working Capital Loan (CC)", "Unsecured Loans from Banks", "Unsecured Loans from Others",
    "Deferred Tax Liability", "Sundry Creditors", "Bills Payable", "Liability for Leased Assets",
    "Interest Accrued and Due", "Interest Accrued but not Due", "Advances from Customers", "Statutory Dues",
    "Provision for Income Tax", "Provision for Wealth Tax", "Provision for Gratuity", "Other Provisions",
    "Fixed Assets: Gross Block", "Capital Work-in-Progress", "Long-term Investments", "Quoted Securities",
    "Unquoted Securities", "Trade Investments", "Equity Shares (Investment)", "Debentures (Investment)",
    "Inventories: Raw Materials", "Inventories: Stock-in-Process", "Inventories: Finished Goods",
    "Inventories: Traded Goods", "Sundry Debtors", "Cash-in-Hand", "Balance with Banks", "Fixed Deposits",
    "Other Current Assets", "Interest Accrued on Investments", "Advances Recoverable in Cash/Kind",
    "Security Deposits", "Balance with Tax Authorities", "Deferred Tax Asset", "Prepaid Expenses",
    "Miscellaneous Expenditure (not written off)"
]

IT_BLOCKS = {
    "Building - Residential (5%)": 0.05,
    "Building - General (10%)": 0.10,
    "Furniture and Fittings (10%)": 0.10,
    "Plant & Machinery - General (15%)": 0.15,
    "Motor Cars - General (15%)": 0.15,
    "Computers including software (40%)": 0.40,
    "Books - Professional (40%)": 0.40,
    "Pollution Control Equipment (40%)": 0.40,
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
else:
    st.sidebar.info("No saved clients.")

st.sidebar.divider()
st.sidebar.header("🏢 Firm Settings")
company_name = st.sidebar.text_input("Company Name", "M/s Rudra Earthmovers")
address = st.sidebar.text_area("Address", "Udaipur, Rajasthan")
selected_fy = st.sidebar.selectbox("Financial Year", ["2023-24", "2024-25", "2025-26"])

if st.sidebar.button("♻️ Reset & New Company"):
    st.session_state.clear()
    st.rerun()

# 4. DATA ENTRY (SEARCHABLE)
st.title(f"Financial Reporting: {company_name}")
t_input, t_report = st.tabs(["📝 Searchable Input", "📈 Final Reports"])

with t_input:
    st.info("Start typing in 'Particulars' to see the pre-filled list of 100+ items.")
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Profit & Loss Account")
        pl_ed = st.data_editor(
            pd.DataFrame({"Particulars": ["Sales"], "Amount": [0.0], "Add Back": [False]}),
            key="pl_search", num_rows="dynamic", use_container_width=True,
            column_config={"Particulars": st.column_config.SelectboxColumn("Account Head", options=TRADING_PL_HEADS, required=True)}
        )

    with c2:
        st.subheader("Balance Sheet")
        bs_ed = st.data_editor(
            pd.DataFrame({"Particulars": ["Sundry Debtors"], "Amount": [0.0]}),
            key="bs_search", num_rows="dynamic", use_container_width=True,
            column_config={"Particulars": st.column_config.SelectboxColumn("Account Head", options=BALANCE_SHEET_HEADS, required=True)}
        )

    st.subheader("🛠️ Depreciation Chart (Finance Act 2025)")
    dep_ed = st.data_editor(
        pd.DataFrame({"Asset": ["Furniture"], "IT Block Type": ["Furniture and Fittings (10%)"], "Opening WDV": [0.0], "Additions (>= 180 Days)": [0.0], "Additions (< 180 Days)": [0.0], "Deletions": [0.0]}),
        key="dep_search", num_rows="dynamic", use_container_width=True,
        column_config={"IT Block Type": st.column_config.SelectboxColumn("IT Block", options=list(IT_BLOCKS.keys()), required=True)}
    )

    if st.button("💾 SAVE FIRM DATA"):
        file_path = f"saved_clients/{company_name.replace(' ', '_')}_{selected_fy}.csv"
        save_df = pd.concat([pl_ed, bs_ed, dep_ed.assign(Group="FA_Schedule")], ignore_index=True)
        save_df.to_csv(file_path, index=False)
        st.success(f"Successfully saved {company_name} for {selected_fy}!")

# 5. REPORTS
with t_report:
    if st.button("📊 GENERATE FINAL REPORTS"):
        # Dep Calc
        res = []
        tot_d = 0
        for _, r in dep_ed.iterrows():
            rate = IT_BLOCKS.get(r['IT Block Type'], 0.15)
            d_f = (r['Opening WDV'] + r['Additions (>= 180 Days)'] - r['Deletions']) * rate
            d_h = r['Additions (< 180 Days)'] * (rate * 0.5)
            cur = d_f + d_h
            tot_d += cur
            res.append({"Asset": r['Asset'], "Rate": f"{rate*100}%", "Opening": r['Opening WDV'], "Depreciation": cur, "Closing WDV": (r['Opening WDV'] + r['Additions (>= 180 Days)'] + r['Additions (< 180 Days)'] - r['Deletions']) - cur})
        
        dep_df = pd.DataFrame(res)
        
        st.markdown(f'<div style="background-color:#5B9BD5;color:white;text-align:center;padding:10px;font-weight:bold;font-size:24px;">{company_name.upper()}</div>', unsafe_allow_html=True)
        st.write(f"**FY:** {selected_fy} | **Address:** {address}")
        
        st.subheader("Fixed Asset & Depreciation Schedule")
        st.table(dep_df)

    # EXCEL EXPORT
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        pl_ed.to_excel(writer, sheet_name='P_and_L')
        bs_ed.to_excel(writer, sheet_name='Balance_Sheet')
        if 'dep_df' in locals(): dep_df.to_excel(writer, sheet_name='Depreciation_Chart')
    st.download_button("📥 Export Final 2202 Excel", data=output.getvalue(), file_name=f"{company_name}_Final_2202.xlsx")
