import streamlit as st
import pandas as pd
import os
import io

# 1. INITIAL SETUP
st.set_page_config(page_title="CA Practice Manager - Udaipur", layout="wide")

if not os.path.exists("saved_clients"):
    os.makedirs("saved_clients")

# 2. COMPREHENSIVE INCOME TAX DEPRECIATION RATES (Finance Act 2025)
# This includes the expanded list from the CA Referencer
IT_BLOCKS = {
    "Building - Residential (5%)": 0.05,
    "Building - General Office/Factory/Hotel (10%)": 0.10,
    "Building - Water Treatment System (40%)": 0.40,
    "Building - Purely Temporary/Wooden (40%)": 0.40,
    "Furniture and Fittings including electrical (10%)": 0.10,
    "Plant & Machinery - General (15%)": 0.15,
    "Motor Cars - Non-Commercial (15%)": 0.15,
    "Motor Cars - Commercial/Taxis/Hire (30%)": 0.30,
    "Motor Buses/Lorries/Taxis - Hire (45% - Specified Period)": 0.45,
    "Aeroplanes / Aero Engines (40%)": 0.40,
    "Moulds - Rubber/Plastic factories (30%)": 0.30,
    "Air Pollution Control Equipment (40%)": 0.40,
    "Water Pollution Control Equipment (40%)": 0.40,
    "Solid Waste Control Equipment (40%)": 0.40,
    "Plant - Semiconductor Industry (30%)": 0.30,
    "Life Saving Medical Equipment (40%)": 0.40,
    "Computers including software (40%)": 0.40,
    "Books - Annual Publications (40%)": 0.40,
    "Books - Non-Annual (Professional) (40%)": 0.40,
    "Books - Lending Libraries (40%)": 0.40,
    "Energy Saving Devices - Furnaces/Boilers (40%)": 0.40,
    "Energy Saving Devices - Instrumentation (40%)": 0.40,
    "Energy Saving Devices - Waste Heat Recovery (40%)": 0.40,
    "Renewable Energy - Solar Devices (40%)": 0.40,
    "Renewable Energy - Wind Mills (post-2014) (40%)": 0.40,
    "Gas Cylinders including valves (40%)": 0.40,
    "Glass Manufacturing - Direct Fire Furnaces (40%)": 0.40,
    "Mineral Oil Concerns - Field Operations (Above Ground) (40%)": 0.40,
    "Mineral Oil Concerns - Field Operations (Below Ground) (40%)": 0.40,
    "Ships - Ocean-going / Tugs / Barges (20%)": 0.20,
    "Vessels - Inland Waters (20%)": 0.20,
    "Intangible Assets - Patents/Copyrights/Know-how (25%)": 0.25
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
        "Asset Name": ["Furniture", "Laptop", "Office Building"],
        "IT Block Type": ["Furniture and Fittings including electrical (10%)", "Computers including software (40%)", "Building - General Office/Factory/Hotel (10%)"],
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

    st.subheader("🛠️ Fixed Asset Schedule & Depreciation Chart (Finance Act 2025)")
    dep_ed = st.data_editor(
        get_dep_template(), 
        key="dep_key", 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={
            "IT Block Type": st.column_config.SelectboxColumn(
                "IT Block Type",
                help="Select the block as per Finance Act 2025",
                options=list(IT_BLOCKS.keys()),
                required=True,
            )
        }
    )

    if st.button("💾 SAVE ALL FIRM DATA"):
        file_path = f"saved_clients/{company_name.replace(' ', '_')}_{selected_fy}.csv"
        save_df = pd.concat([pl_ed, bs_ed, dep_ed.assign(Group="FA_Schedule")], ignore_index=True)
        save_df.to_csv(file_path, index=False)
        st.success(f"Successfully saved {company_name} for {selected_fy}!")

# 6. REPORT GENERATION
with tab_report:
    if st.button("📊 GENERATE FINAL P&L AND BALANCE SHEET"):
        dep_results = []
        tot_dep_amt = 0
        for _, row in dep_ed.iterrows():
            rate = IT_BLOCKS.get(row['IT Block Type'], 0.15)
            # Rule: 50% dep if used < 180 days
            opening_base = (row['Opening WDV'] + row['Additions (>= 180 Days)'] - row['Deletions'])
            d_full = opening_base * rate
            d_half = row['Additions (< 180 Days)'] * (rate * 0.5)
            
            cur_dep = d_full + d_half
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

        # Calculations
        def sum_p(df, name): return df[df['Particulars']==name]['Amount'].sum()
        gp = (sum_p(pl_ed, "Sales") + sum_p(pl_ed, "Closing Stock")) - (sum_p(pl_ed, "Opening Stock") + sum_p(pl_ed, "Purchase"))
        # NP = Income - (Expenses + Depreciation)
        np = (gp + pl_ed[pl_ed['Group']=="Income"]['Amount'].sum()) - (pl_ed[pl_ed['Group']=="Expense"]['Amount'].sum() + tot_dep_amt)

        st.markdown(f'<div style="background-color:#5B9BD5;color:white;text-align:center;padding:10px;font-weight:bold;">{company_name.upper()}</div>', unsafe_allow_html=True)
        
        st.subheader("Fixed Asset & Depreciation Schedule (Finance Act 2025)")
        st.dataframe(dep_summary_df, hide_index=True)

        st.subheader("Balance Sheet Summary")
        st.table(dep_summary_df[["Asset Name", "Rate (%)", "Opening WDV", "Depreciation", "Closing WDV"]])

    # EXCEL EXPORT
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        pl_ed.to_excel(writer, sheet_name='Profit_Loss')
        bs_ed.to_excel(writer, sheet_name='Balance_Sheet')
        if 'dep_summary_df' in locals():
            dep_summary_df.to_excel(writer, sheet_name='Depreciation_Chart')
    
    st.download_button("📥 Export Report to Excel", data=output.getvalue(), file_name=f"{company_name}_Report.xlsx")
