import streamlit as st
import pandas as pd
import os
import io

# 1. INITIAL SETUP
st.set_page_config(page_title="CA Practice Manager - Final 2202", layout="wide")

if not os.path.exists("saved_clients"):
    os.makedirs("saved_clients")

# 2. COMPREHENSIVE INCOME TAX DEPRECIATION RATES (Finance Act 2025)
# Full referencer for 50+ items
IT_BLOCKS = {
    "Building - Residential (5%)": 0.05,
    "Building - General Office/Factory/Hotel (10%)": 0.10,
    "Building - Water Treatment System (40%)": 0.40,
    "Building - Purely Temporary/Wooden (40%)": 0.40,
    "Furniture and Fittings including electrical (10%)": 0.10,
    "Plant & Machinery - General (15%)": 0.15,
    "Motor Cars - Non-Commercial (15%)": 0.15,
    "Motor Cars - Commercial/Taxis/Hire (30%)": 0.30,
    "Motor Buses/Lorries/Taxis - Hire (45%)": 0.45,
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
    "Energy Saving Devices - Boilers/Furnaces (40%)": 0.40,
    "Renewable Energy - Solar Devices (40%)": 0.40,
    "Renewable Energy - Wind Mills (40%)": 0.40,
    "Gas Cylinders including valves (40%)": 0.40,
    "Glass Manufacturing Furnaces (40%)": 0.40,
    "Mineral Oil Concerns - Field Ops (40%)": 0.40,
    "Ships - Ocean-going / Tugs / Barges (20%)": 0.20,
    "Vessels - Inland Waters (20%)": 0.20,
    "Intangible Assets - Patents/Know-how (25%)": 0.25
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
st.sidebar.header("🏢 Current Firm Settings")
company_name = st.sidebar.text_input("Company Name", "M/s Rudra Earthmovers")
address = st.sidebar.text_area("Address", "Udaipur, Rajasthan")
selected_fy = st.sidebar.selectbox("Financial Year", ["2023-24", "2024-25", "2025-26"])

if st.sidebar.button("♻️ Reset & New Company"):
    st.session_state.clear()
    st.rerun()

# 4. TEMPLATES
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
        "Asset Name": ["Furniture", "Laptop"],
        "IT Block Type": ["Furniture and Fittings including electrical (10%)", "Computers including software (40%)"],
        "Opening WDV": [0.0] * 2,
        "Additions (>= 180 Days)": [0.0] * 2,
        "Additions (< 180 Days)": [0.0] * 2,
        "Deletions": [0.0] * 2
    })

# 5. DATA ENTRY
st.title(f"Financial Reporting: {company_name}")
t_entry, t_report = st.tabs(["📝 Input Sheet", "📈 Final Reports"])

with t_entry:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("P&L Input")
        pl_ed = st.data_editor(get_pl_template(), key="pl_v", num_rows="dynamic", use_container_width=True)
    with c2:
        st.subheader("Balance Sheet Input")
        bs_ed = st.data_editor(get_bs_template(), key="bs_v", num_rows="dynamic", use_container_width=True)

    st.subheader("🛠️ Depreciation Chart (Finance Act 2025)")
    dep_ed = st.data_editor(get_dep_template(), key="dep_v", num_rows="dynamic", use_container_width=True,
                            column_config={"IT Block Type": st.column_config.SelectboxColumn("IT Block Type", options=list(IT_BLOCKS.keys()), required=True)})

    if st.button("💾 SAVE FIRM DATA"):
        file_path = f"saved_clients/{company_name.replace(' ', '_')}_{selected_fy}.csv"
        save_df = pd.concat([pl_ed, bs_ed, dep_ed.assign(Group="FA_Schedule")], ignore_index=True)
        save_df.to_csv(file_path, index=False)
        st.success(f"Saved {company_name} - {selected_fy}!")

# 6. REPORTS
with t_report:
    if st.button("📊 GENERATE FINAL REPORTS"):
        # Dep Logic
        res = []
        tot_d = 0
        for _, r in dep_ed.iterrows():
            rate = IT_BLOCKS.get(r['IT Block Type'], 0.15)
            d_full = (r['Opening WDV'] + r['Additions (>= 180 Days)'] - r['Deletions']) * rate
            d_half = r['Additions (< 180 Days)'] * (rate * 0.5)
            cur = d_full + d_half
            tot_d += cur
            res.append({"Asset": r['Asset Name'], "Rate (%)": f"{rate*100}%", "Opening": r['Opening WDV'], "Depreciation": cur, "Closing WDV": (r['Opening WDV'] + r['Additions (>= 180 Days)'] + r['Additions (< 180 Days)'] - r['Deletions']) - cur})
        
        dep_df = pd.DataFrame(res)
        
        # P&L
        def s_p(df, n): return df[df['Particulars']==n]['Amount'].sum()
        gp = (s_p(pl_ed, "Sales") + s_p(pl_ed, "Closing Stock")) - (s_p(pl_ed, "Opening Stock") + s_p(pl_ed, "Purchase"))
        np = (gp + pl_ed[pl_ed['Group']=="Income"]['Amount'].sum()) - (pl_ed[pl_ed['Group']=="Expense"]['Amount'].sum() + tot_d)

        # Presentation
        st.markdown(f'<div style="background-color:#5B9BD5;color:white;text-align:center;padding:10px;font-weight:bold;font-size:24px;">{company_name.upper()}</div>', unsafe_allow_html=True)
        st.write(f"**FY:** {selected_fy} | **GP:** ₹{gp:,.2f} | **NP:** ₹{np:,.2f}")
        
        st.subheader("Depreciation Schedule & Balance Sheet Breakdown")
        st.table(dep_df[["Asset", "Rate (%)", "Opening", "Depreciation", "Closing WDV"]])

    # EXCEL EXPORT
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        pl_ed.to_excel(writer, sheet_name='P_and_L')
        bs_ed.to_excel(writer, sheet_name='Balance_Sheet')
        if 'dep_df' in locals(): dep_df.to_excel(writer, sheet_name='Dep_Schedule')
    st.download_button("📥 Export Final 2202 Excel", data=output.getvalue(), file_name=f"{company_name}_Final_2202.xlsx")
