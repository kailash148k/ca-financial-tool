import streamlit as st
import pandas as pd

st.set_page_config(page_title="CA Financial Tool", layout="wide")

# Custom CSS for the "Tally" professional look
st.markdown("""
    <style>
    .report-header { background-color: #5B9BD5; color: white; text-align: center; padding: 10px; font-weight: bold; border: 1px solid black; }
    .sub-group-header { background-color: #FFF2CC; font-weight: bold; padding: 5px; border-bottom: 1px solid #ddd; }
    .total-row { background-color: #DDEBF7; font-weight: bold; border-top: 2px solid black; }
    </style>
""", unsafe_allow_html=True)

# --- PART 1: PRE-FILLED INPUT DATA ---
if 'financial_data' not in st.session_state:
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
        "Amount": [0.0] * 22
    }
    st.session_state.financial_data = pd.DataFrame(template)

st.title("📊 Financial Statement Generator")
st.subheader("Input Sheet")
edited_df = st.data_editor(st.session_state.financial_data, num_rows="dynamic", use_container_width=True)

# --- PART 2: CALCULATION ENGINE ---
def generate_reports(df):
    # Trading Logic
    def get_val(name): return df[df['Particulars'] == name]['Amount'].sum()
    
    gp = (get_val("Sales") + get_val("Closing Stock")) - (get_val("Opening Stock") + get_val("Purchase") + get_val("Direct Expenses"))
    
    ind_inc = df[df['Category'] == "Indirect Income"]['Amount'].sum()
    ind_exp = df[df['Category'] == "Indirect Expense"]['Amount'].sum()
    net_profit = (gp + ind_inc) - ind_exp
    
    return gp, net_profit

# --- PART 3: DISPLAY RESULTS ---
if st.button("Generate P&L and Balance Sheet"):
    gp, np = generate_reports(edited_df)
    
    tab1, tab2 = st.tabs(["Profit & Loss Account", "Balance Sheet"])
    
    with tab1:
        st.markdown('<div class="report-header">Profit & Loss A/c</div>', unsafe_allow_html=True)
        # Layout logic for Trading vs Indirects...
        st.write(f"**Gross Profit: ₹{gp:,.2f}**")
        st.write(f"**Net Profit: ₹{np:,.2f}**")
        
    with tab2:
        st.markdown('<div class="report-header">Balance Sheet</div>', unsafe_allow_html=True)
        col_src, col_app = st.columns(2)
        
        with col_src:
            st.markdown('<div class="sub-group-header">Sources of Funds</div>', unsafe_allow_html=True)
            liabilities = edited_df[edited_df['Category'] == "Liability"]
            st.table(liabilities[['Particulars', 'Amount']])
            st.write(f"Profit & Loss (Current Period): ₹{np:,.2f}")
            total_src = liabilities['Amount'].sum() + np
            st.markdown(f'<div class="total-row">Total: ₹{total_src:,.2f}</div>', unsafe_allow_html=True)
            
        with col_app:
            st.markdown('<div class="sub-group-header">Application of Funds</div>', unsafe_allow_html=True)
            assets = edited_df[edited_df['Category'] == "Asset"]
            st.table(assets[['Particulars', 'Amount']])
            total_app = assets['Amount'].sum() + get_val("Closing Stock")
            st.markdown(f'<div class="total-row">Total: ₹{total_app:,.2f}</div>', unsafe_allow_html=True)

    if round(total_src, 2) == round(total_app, 2):
        st.success("Balanced! ✅")
    else:
        st.warning("Difference in Balance Sheet ⚠️")