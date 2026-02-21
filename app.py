import streamlit as st
import pandas as pd
import os
import io

st.set_page_config(page_title="CA Financial Tool", layout="wide")

# 1. SIDEBAR & FILE LOGIC
st.sidebar.header("🏢 Firm Management")
company_name = st.sidebar.text_input("Company Name", "M/s Rudra Earthmovers")
selected_fy = st.sidebar.selectbox("Select Financial Year", ["2021-22", "2022-23", "2023-24", "2024-25", "2025-26"])

if not os.path.exists("saved_clients"):
    os.makedirs("saved_clients")

# Define Template
def get_template():
    return pd.DataFrame({
        "Particulars": ["Sales", "Opening Stock", "Purchase", "Closing Stock", "Direct Expenses", 
                        "Interest Income", "Commission", "Salary", "Office Expenses", "Depreciation"],
        "Category": ["Trading", "Trading", "Trading", "Trading", "Trading", 
                      "Indirect Income", "Indirect Income", "Indirect Expense", "Indirect Expense", "Indirect Expense"],
        "Add Back": [False] * 10,
        "Amount": [0.0] * 10
    })

if 'financial_data' not in st.session_state:
    st.session_state.financial_data = get_template()

# 2. INPUT SECTION
st.title(f"Financials for {company_name}")
edited_df = st.data_editor(st.session_state.financial_data, num_rows="dynamic", use_container_width=True)

# 3. ACTION BUTTONS (Placed clearly before reports)
col_btn1, col_btn2, col_btn3 = st.columns(3)

with col_btn1:
    if st.button("💾 Save Data for this FY"):
        file_path = f"saved_clients/{company_name.replace(' ', '_')}_{selected_fy}.csv"
        edited_df.to_csv(file_path, index=False)
        st.success(f"Saved {selected_fy}")

with col_btn2:
    generate_trigger = st.button("📊 Generate P&L and Balance Sheet")

with col_btn3:
    # EXCEL DOWNLOAD LOGIC
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        edited_df.to_excel(writer, sheet_name='Input_Data', index=False)
    
    st.download_button(
        label="📥 Download as Excel",
        data=buffer,
        file_name=f"{company_name}_{selected_fy}.xlsx",
        mime="application/vnd.ms-excel"
    )

# 4. REPORT DISPLAY
if generate_trigger:
    def get_val(name):
        return edited_df[edited_df['Particulars'] == name]['Amount'].sum()

    # Calculations
    gp = (get_val("Sales") + get_val("Closing Stock")) - (get_val("Opening Stock") + get_val("Purchase") + get_val("Direct Expenses"))
    ind_inc = edited_df[edited_df['Category'] == "Indirect Income"]['Amount'].sum()
    ind_exp = edited_df[edited_df['Category'] == "Indirect Expense"]['Amount'].sum()
    np = (gp + ind_inc) - ind_exp

    st.divider()
    t1, t2 = st.tabs(["Profit & Loss", "Balance Sheet"])
    
    with t1:
        st.subheader(f"P&L Account: {selected_fy}")
        st.write(f"**Gross Profit:** ₹{gp:,.2f}")
        st.write(f"**Net Profit:** ₹{np:,.2f}")

    with t2:
        st.subheader("Balance Sheet")
        st.info(f"Net Profit for BS: ₹{np:,.2f}")
