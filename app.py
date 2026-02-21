import streamlit as st
import pandas as pd
import os
import io

# 1. INITIAL SETUP
st.set_page_config(page_title="CA Practice Manager - Udaipur", layout="wide")

if not os.path.exists("saved_clients"):
    os.makedirs("saved_clients")

# 2. COMPREHENSIVE INCOME TAX DEPRECIATION RATES [cite: 2, 7, 15, 18, 47]
# These rates are mapped directly from your provided Income Tax Chart
IT_DEP_RATES = {
    "Building - Residential (Non-Hotel)": 0.05,
    "Building - General (Office/Factory)": 0.10,
    "Building - Temporary / Wooden Structures": 0.40,
    "Furniture and Fittings (including electrical)": 0.10,
    "Plant & Machinery (General)": 0.15,
    "Motor Cars (General - 15%)": 0.15,
    "Motor Cars (Commercial - 30%)": 0.30,
    "Computers including software": 0.40,
    "Books (Annual publications/Lending libraries)": 0.40,
    "Air/Water Pollution Control Equipment": 0.40,
    "Life Saving Medical Equipment": 0.40,
    "Intangible Assets (Patents/Copyrights/Trademarks)": 0.25,
    "Ships / Ocean-going Vessels": 0.20
}

# 3. SIDEBAR: CLIENT DASHBOARD
st.sidebar.header("📂 Client List Dashboard")
all_files = [f for f in os.listdir("saved_clients") if f.endswith('.csv')]
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
selected_fy = st.sidebar.selectbox("Financial Year", ["2023-24", "2024-25", "2025-26"])

if st.sidebar.button("♻️ Reset & New Company"):
    st.session_state.clear()
    st.rerun()

# 4. DATA TEMPLATES
def get_pl_template():
    return pd.DataFrame({
        "Particulars": ["Sales", "Opening Stock", "Purchase", "Closing Stock", "Direct Expenses", "Interest Income", "Commission", "Salary", "Office Expenses"],
        "Group": ["Trading", "Trading", "Trading", "Trading", "Trading", "Income", "Income", "Expense", "Expense"],
        "Add Back": [False] * 9,
        "Amount": [0.0] * 9
    })

def get_bs_template():
    return pd.DataFrame({
        "Particulars": ["Promoter Capital", "Bank Loan", "Sundry Creditors", "Duties & Taxes", "Sundry Debtors", "Cash-in-Hand", "Bank Accounts"],
        "Group": ["Liability", "Liability", "Liability", "Liability", "Asset", "Asset", "Asset"],
        "Amount": [0.0] * 7
    })

def get_dep_template():
    return pd.DataFrame({
        "Asset Name": ["Office Computers", "Office Furniture", "Office Building"],
        "IT Block Type": ["Computers including software", "Furniture and Fittings (including electrical)", "Building - General (Office/Factory)"],
        "Opening WDV": [0.0] * 3,
        "Additions (>= 180 Days)": [0.0] * 3,
        "Additions (< 180 Days)": [0.0] * 3,
        "Deletions": [0.0] * 3
    })

# 5. DATA ENTRY TABS
st.title(f"Financial Reporting: {company_name}")
tab_entry, tab_report = st.tabs(["📝 Input Sheet", "📈 Final Reports & Analysis"])

with tab_entry:
    col_pl, col_bs = st.columns(2)
    with col_pl:
        st.subheader("Profit & Loss Account Input")
        pl_ed = st.data_editor(get_pl_template(), key="pl_key", num_rows="dynamic", use_container_width=True)
    with col_bs:
        st.subheader("Current Assets & Liabilities Input")
        bs_ed = st.data_editor(get_bs_template(), key="bs_key", num_rows="dynamic", use_container_width=True)

    st.subheader("🛠️ Fixed Asset Schedule & Depreciation Chart (Income Tax Act)")
    # Dropdown for IT Block Type selection within the editor
    dep_ed = st.data_editor(
        get_dep_template(), 
        key="dep_key", 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={
            "IT Block Type": st.column_config.SelectboxColumn(
                "IT Block Type",
                help="Select the category as per Income Tax Act",
                options=list(IT_DEP_RATES.keys()),
                required=True,
            )
        }
    )

    if st.button("💾 SAVE ALL FIRM DATA"):
        file_path = f"saved_clients/{company_name.replace(' ', '_')}_{selected_fy}.csv"
        # Save all data into a structured CSV
        save_df = pd.concat([pl_ed, bs_ed, dep_ed.assign(Group="FA_Schedule")], ignore_index=True)
        save_df.to_csv(file_path, index=False)
        st.success(f"Successfully saved {company_name} for {selected_fy}!")

# 6. REPORT GENERATION
with tab_report:
    if st.button("📊 GENERATE FINAL P&L AND BALANCE SHEET"):
        # --- Depreciation Logic  ---
        dep_results = []
        tot_dep_amt = 0
        for _, row in dep_ed.iterrows():
            rate = IT_DEP_RATES.get(row['IT Block Type'], 0.15)
            # Rule: 50% dep if used < 180 days 
            # (Opening + Add >= 180 - Deletions) * Full Rate + (Add < 180) * Half Rate
            opening_base = (row['Opening WDV'] + row['Additions (>= 180 Days)'] - row['Deletions'])
            d1 = opening_base * rate
            d2 = row['Additions (< 180 Days)'] * (rate * 0.5)
            
            cur_dep = d1 + d2
            tot_dep_amt += cur_dep
            
            total_cost = (row['Opening WDV'] + row['Additions (>= 180 Days)'] + row['Additions (< 180 Days)'] - row['Deletions'])
            
            dep_results.append({
                "Asset Name": row['Asset Name'],
                "IT Block": row['IT Block Type'],
                "Rate (%)": f"{rate*100}%",
                "Opening WDV": row['Opening WDV'],
                "Additions": row['Additions (>= 180 Days)'] + row['Additions (< 180 Days)'],
                "Deletions": row['Deletions'],
                "Depreciation": cur_dep,
                "Closing WDV": total_cost - cur_dep
            })
        
        dep_summary_df = pd.DataFrame(dep_results)

        # --- P&L Logic ---
        # Note: Depreciation is automatically added to expenses
        sales = pl_ed[pl_ed['Particulars']=="Sales"]['Amount'].sum()
        cl_stock = pl_ed[pl_ed['Particulars']=="Closing Stock"]['Amount'].sum()
        op_stock = pl_ed[pl_ed['Particulars']=="Opening Stock"]['Amount'].sum()
        pur = pl_ed[pl_ed['Particulars']=="Purchase"]['Amount'].sum()
        gp = (sales + cl_stock) - (op_stock + pur)
        
        ind_inc = pl_ed[pl_ed['Group']=="Income"]['Amount'].sum()
        ind_exp = pl_ed[pl_ed['Group']=="Expense"]['Amount'].sum() + tot_dep_amt
        np = (gp + ind_inc) - ind_exp

        # --- Display Reports ---
        st.markdown(f'<div class="report-header">{company_name.upper()}</div>', unsafe_allow_html=True)
        st.write(f"**Gross Profit:** ₹{gp:,.2f} | **Net Profit:** ₹{np:,.2f}")
        
        st.subheader("Fixed Asset & Depreciation Schedule (As per Income Tax Act)")
        st.dataframe(dep_summary_df, hide_index=True)

        st.subheader("Balance Sheet (Fixed Assets Section)")
        # Showing Opening, Less Dep, and Closing separately as requested
        st.table(dep_summary_df[["Asset Name", "Opening WDV", "Depreciation", "Closing WDV"]])

    # EXCEL EXPORT
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        pl_ed.to_excel(writer, sheet_name='Profit_Loss')
        bs_ed.to_excel(writer, sheet_name='Balance_Sheet')
        if 'dep_summary_df' in locals():
            dep_summary_df.to_excel(writer, sheet_name='Depreciation_Chart')
    
    st.download_button("📥 Export Professional Excel Report", data=output.getvalue(), file_name=f"{company_name}_Full_Report.xlsx")
