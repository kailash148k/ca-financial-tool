import streamlit as st
import pandas as pd
import os
import io

st.set_page_config(page_title="CA Multi-Year Analysis", layout="wide")

# 1. SIDEBAR & CLIENT SETUP
st.sidebar.header("🏢 Client Management")
company_name = st.sidebar.text_input("Company Name", "M/s Rudra Earthmovers")
address = st.sidebar.text_area("Address", "Udaipur, Rajasthan")

if not os.path.exists("saved_clients"):
    os.makedirs("saved_clients")

# 2. SEPARATE TEMPLATES
def get_pl_template():
    return pd.DataFrame({
        "Particulars": ["Sales", "Opening Stock", "Purchase", "Closing Stock", "Direct Expenses", 
                        "Interest Income", "Commission", "Salary", "Office Expenses", "Depreciation", "Interest on CC"],
        "Group": ["Trading", "Trading", "Trading", "Trading", "Trading", 
                  "Income", "Income", "Expense", "Expense", "Expense", "Expense"],
        "Add Back (for Cash Profit)": [False] * 11,
        "Amount": [0.0] * 11
    })

def get_bs_template():
    return pd.DataFrame({
        "Particulars": ["Promoter Capital", "Bank Loan", "Sundry Creditors", "Duties & Taxes", 
                        "Office Computers", "Office Furnitures", "Land and Building", "Sundry Debtors", "Cash-in-Hand"],
        "Group": ["Liability", "Liability", "Liability", "Liability", "Asset", "Asset", "Asset", "Asset", "Asset"],
        "Amount": [0.0] * 9
    })

# 3. INPUT SECTION (TWO PARTS)
st.title(f"Data Entry: {company_name}")
selected_fy = st.selectbox("Select Financial Year for Data Entry", ["2021-22", "2022-23", "2023-24", "2024-25", "2025-26"])

col_pl, col_bs = st.columns(2)

with col_pl:
    st.subheader("📝 1. Profit & Loss Input")
    pl_df = st.data_editor(get_pl_template(), key=f"pl_{selected_fy}", use_container_width=True)

with col_bs:
    st.subheader("⚖️ 2. Balance Sheet Input")
    bs_df = st.data_editor(get_bs_template(), key=f"bs_{selected_fy}", use_container_width=True)

# 4. SAVE & PERSISTENCE
if st.button("💾 Save All Data for this FY"):
    full_data = pd.concat([pl_df, bs_df], ignore_index=True)
    file_path = f"saved_clients/{company_name.replace(' ', '_')}_{selected_fy}.csv"
    full_data.to_csv(file_path, index=False)
    st.success(f"Saved {selected_fy} successfully!")

st.divider()

# 5. AVG CASH PROFIT SELECTOR
st.header("📈 Average Cash Profit Analysis")
years_to_avg = st.multiselect("Select years to calculate Average Cash Profit", 
                              ["2021-22", "2022-23", "2023-24", "2024-25", "2025-26"],
                              default=["2024-25"])

if st.button("🧮 Calculate Average Cash Profit"):
    cash_profits = []
    
    for fy in years_to_avg:
        path = f"saved_clients/{company_name.replace(' ', '_')}_{fy}.csv"
        if os.path.exists(path):
            data = pd.read_csv(path)
            
            # Simplified Logic for Demo
            sales = data[data['Particulars'] == "Sales"]['Amount'].sum()
            pur = data[data['Particulars'] == "Purchase"]['Amount'].sum()
            # Net Profit approximation
            inc = data[data['Group'] == "Income"]['Amount'].sum()
            exp = data[data['Group'] == "Expense"]['Amount'].sum()
            np = (sales - pur + inc - exp)
            
            # Cash Profit: Add back items where tickmark was True
            add_back_amt = data[data['Add Back (for Cash Profit)'] == True]['Amount'].sum()
            cash_profits.append(np + add_back_amt)
    
    if cash_profits:
        avg_cp = sum(cash_profits) / len(cash_profits)
        st.metric("Average Cash Profit", f"₹{avg_cp:,.2f}", f"Based on {len(cash_profits)} years")
    else:
        st.error("No data found for the selected years. Please save data first.")
