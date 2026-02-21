import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="CA Financial Analysis Tool", layout="wide")

# 1. DATABASE SETUP
if not os.path.exists("saved_clients"):
    os.makedirs("saved_clients")

def get_empty_df():
    # Added 'Add Back' column for the checkbox logic
    template = {
        "Particulars": [
            "Sales", "Opening Stock", "Purchase", "Closing Stock", "Direct Expenses",
            "Interest Income", "Commission", "Wages and Salary (Other)",
            "Salary", "Office Expenses", "Depreciation", "Interest on Term Loan", "Interest on CC",
            "Promoter Capital", "Bank Loan", "Sundry Creditors", "Duties & Taxes",
            "Office Computers", "Office Furnitures", "Land and Building", "Sundry Debtors", "Cash-in-Hand"
        ],
        "Category": [
            "Trading", "Trading", "Trading", "Trading", "Trading",
            "Indirect Income", "Indirect Income", "Indirect Income",
            "Indirect Expense", "Indirect Expense", "Indirect Expense", "Indirect Expense", "Indirect Expense",
            "Liability", "Liability", "Liability", "Liability",
            "Asset", "Asset", "Asset", "Asset", "Asset"
        ],
        "Add Back": [False] * 22, # Checkbox for Cash Income calculation
        "Amount": [0.0] * 22
    }
    return pd.DataFrame(template)

# 2. SIDEBAR - MULTI-YEAR MANAGEMENT
st.sidebar.header("🏢 Firm & FY Management")
company_name = st.sidebar.text_input("Company Name", "M/s Rudra Earthmovers")
# Dropdown for 5 Financial Years
selected_fy = st.sidebar.selectbox("Select Financial Year", 
    ["2021-22", "2022-23", "2023-24", "2024-25", "2025-26"])

# 3. DATA LOADING LOGIC
# We save files as FirmName_FY.csv to keep them separate
file_key = f"{company_name.replace(' ', '_')}_{selected_fy}"
file_path = f"saved_clients/{file_key}.csv"

if 'current_df' not in st.session_state:
    st.session_state.current_df = get_empty_df()

# Load data if it exists for that specific FY
if os.path.exists(file_path) and st.sidebar.button("📂 Load Data for this FY"):
    st.session_state.current_df = pd.read_csv(file_path)
    st.sidebar.success(f"Loaded {selected_fy}")

# 4. INPUT GRID
st.title(f"📊 Financials: {company_name} ({selected_fy})")
edited_df = st.data_editor(st.session_state.current_df, num_rows="dynamic", use_container_width=True)

if st.button("💾 Save Data for this FY"):
    edited_df.to_csv(file_path, index=False)
    st.success(f"Saved data for {selected_fy}")

# 5. CALCULATION ENGINE (WITH CASH INCOME LOGIC)
def get_val(df, name):
    subset = df[df['Particulars'] == name]
    return subset['Amount'].sum() if not subset.empty else 0.0

if st.button("📈 Calculate & Generate Reports"):
    # Standard P&L Logic
    sales = get_val(edited_df, "Sales")
    closing = get_val(edited_df, "Closing Stock")
    opening = get_val(edited_df, "Opening Stock")
    purchase = get_val(edited_df, "Purchase")
    direct_exp = get_val(edited_df, "Direct Expenses")
    
    gp = (sales + closing) - (opening + purchase + direct_exp)
    
    ind_inc = edited_df[edited_df['Category'] == "Indirect Income"]['Amount'].sum()
    ind_exp = edited_df[edited_df['Category'] == "Indirect Expense"]['Amount'].sum()
    np = (gp + ind_inc) - ind_exp
    
    # CASH INCOME LOGIC
    # Sum of all expenses where the 'Add Back' checkbox is True
    added_back_amt = edited_df[(edited_df['Add Back'] == True) & (edited_df['Category'].str.contains("Expense"))]['Amount'].sum()
    cash_income = np + added_back_amt
    
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Net Profit", f"₹{np:,.2f}")
    with col2:
        st.metric("Cash Income (Net Profit + Added Back)", f"₹{cash_income:,.2f}", help="Includes items you ticked in the 'Add Back' column")

    st.info(f"Add-back items total: ₹{added_back_amt:,.2f}")
