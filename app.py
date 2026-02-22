import streamlit as st
import pandas as pd
import os
import io

# 1. DIRECTORY & INITIAL SETUP
for folder in ["saved_clients", "templates"]:
    if not os.path.exists(folder):
        os.makedirs(folder)

st.set_page_config(page_title="CA Practice Manager - Final 2202", layout="wide")

# 2. LIBRARIES
TRADING_PL_HEADS = ["Sales", "Opening Stock", "Purchases", "Wages", "Direct Expenses", "Salaries", "Office Rent", "Audit Fees", "Depreciation", "Interest Received"]
BALANCE_SHEET_HEADS = ["Proprietor's Capital", "Secured Loans", "Unsecured Loans", "Sundry Creditors", "Sundry Debtors", "Cash-in-Hand", "Balance with Banks", "Security Deposits"]
IT_BLOCKS = {"Building (10%)": 0.10, "Furniture (10%)": 0.10, "Plant & Machinery (15%)": 0.15, "Computers (40%)": 0.40}

# 3. SIDEBAR: KYC & LOAN DOSSIER
with st.sidebar:
    st.header("📂 Client List Dashboard")
    all_files = [f for f in os.listdir("saved_clients") if f.endswith('.csv')]
    if all_files:
        unique_firms = sorted(list(set([f.split('_20')[0].replace('_', ' ') for f in all_files])))
        st.write(f"Total Firms Managed: **{len(unique_firms)}**")
        for firm in unique_firms:
            st.markdown(f"🔹 {firm}")
    
    st.divider()
    st.header("👤 Customer Details")
    company_name = st.text_input("Firm Name", "M/s Rudra Earthmovers")
    address = st.text_area("Address", "Udaipur, Rajasthan")
    selected_fy = st.selectbox("Financial Year", ["2023-24", "2024-25", "2025-26"])
    firm_type = st.sidebar.selectbox("Firm Category", ["Trading Firm", "Service Provider", "Manufacturing"])

    # MULTI-APPLICANT KYC SECTION
    num_applicants = st.number_input("Number of Applicants", min_value=1, value=1, step=1)
    applicant_summary = []
    
    for i in range(int(num_applicants)):
        with st.expander(f"Applicant {i+1} Details", expanded=(i==0)):
            app_name = st.text_input(f"Applicant Name", key=f"app_name_{i}")
            app_dob = st.date_input(f"DOB", key=f"app_dob_{i}")
            st.text_input(f"Mother's Name", key=f"app_moth_{i}")
            st.text_input(f"Mobile No.", key=f"app_mob_{i}")
            st.text_input(f"Email ID", key=f"app_mail_{i}")
            
            st.checkbox("Electricity Bill Collected", key=f"lb_{i}")
            st.checkbox("Photo Collected", key=f"ph_{i}")
            
            income_source = st.radio("Income Type", ["Salaried", "Business", "None"], key=f"inc_{i}")
            if income_source == "Salaried":
                st.checkbox("Last 6m Salary Slip", key=f"ss_{i}")
                st.checkbox("Last 2y Form 16", key=f"f16_{i}")
                st.checkbox("Last 2y ITR", key=f"itrs_{i}")
            elif income_source == "Business":
                st.checkbox("Last 3y ITR Ack", key=f"itrb_{i}")
                st.checkbox("Computation of Income", key=f"comp_{i}")
                st.checkbox("P&L and Balance Sheet", key=f"plbs_{i}")
            
            applicant_summary.append({"Name": app_name, "DOB": app_dob, "Income": income_source})

    # RUNNING LOAN TRACKER
    st.divider()
    st.header("💳 Running Loans")
    num_loans = st.number_input("Existing Loans?", min_value=0, value=0)
    loan_data = []
    for j in range(int(num_loans)):
        with st.expander(f"Loan {j+1}", expanded=False):
            bnk = st.text_input("Bank Name", key=f"ln_bnk_{j}")
            amt = st.number_input("Loan Amount", key=f"ln_amt_{j}")
            st.text_input("Tenure", key=f"ln_ten_{j}")
            st.checkbox("Sanction Letter", key=f"ln_sanc_{j}")
            st.checkbox("LOD", key=f"ln_lod_{j}")
            st.checkbox("Loan Statement", key=f"ln_stmt_{j}")
            loan_data.append({"Bank": bnk, "Amount": amt})

    st.divider()
    st.checkbox("Property Paper Chain Collected", key="prop_chain")
    st.text_input("Bank Name (PDF Banking)", key="bnk_pdf")

# 4. TEMPLATE LOADER
def load_template(form_type, firm_cat):
    file_path = f"templates/{firm_cat.replace(' ', '_')}_{form_type}.csv"
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    if form_type == "PL":
        return pd.DataFrame({"Particulars": ["Sales", "Purchases", "Salaries", "Depreciation"], "Amount": [0.0]*4, "Add Back": [False]*4})
    return pd.DataFrame({"Particulars": ["Proprietor's Capital", "Sundry Creditors", "Sundry Debtors", "Cash-in-Hand"], "Amount": [0.0]*4})

# 5. MAIN INTERFACE
st.title(f"Financial Reporting: {company_name}")
t_input, t_report, t_analysis = st.tabs(["📝 Input Sheet", "📈 Final Reports", "🧮 Cash Profit Analysis"])

with t_input:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Profit & Loss Account")
        pl_ed = st.data_editor(load_template("PL", firm_type), key=f"pl_{firm_type}", num_rows="dynamic", use_container_width=True,
                               column_config={"Particulars": st.column_config.SelectboxColumn("Account Head", options=TRADING_PL_HEADS)})
        if st.button(f"💾 Save Default {firm_type} P&L"):
            pl_ed.to_csv(f"templates/{firm_type.replace(' ', '_')}_PL.csv", index=False)
            st.success("P&L Template Locked!")

    with c2:
        st.subheader("Balance Sheet")
        bs_ed = st.data_editor(load_template("BS", firm_type), key=f"bs_{firm_type}", num_rows="dynamic", use_container_width=True,
                               column_config={"Particulars": st.column_config.SelectboxColumn("Account Head", options=BALANCE_SHEET_HEADS)})
        if st.button(f"💾 Save Default {firm_type} BS"):
            bs_ed.to_csv(f"templates/{firm_type.replace(' ', '_')}_BS.csv", index=False)
            st.success("BS Template Locked!")

    if st.button("🚀 SAVE CLIENT DOSSIER"):
        file_path = f"saved_clients/{company_name.replace(' ', '_')}_{selected_fy}.csv"
        full_save = pd.concat([pl_ed, bs_ed], ignore_index=True)
        full_save.to_csv(file_path, index=False)
        st.success(f"Dossier for {company_name} saved successfully!")

# 6. REPORTS & BANK SUMMARY
with t_report:
    if st.button("📊 GENERATE BANK SUMMARY"):
        st.markdown(f'<div style="background-color:#5B9BD5;color:white;text-align:center;padding:10px;font-weight:bold;font-size:24px;">BANK LOAN APPLICATION SUMMARY</div>', unsafe_allow_html=True)
        st.subheader("Applicant Information")
        st.table(pd.DataFrame(applicant_summary))
        st.subheader("Existing Liability Summary")
        if loan_data: st.table(pd.DataFrame(loan_data))
        else: st.info("No running loans reported.")

# 7. CASH PROFIT ANALYSIS
with t_analysis:
    st.header("Average Cash Profit Calculation")
    years_to_avg = st.multiselect("Select years to include", ["2023-24", "2024-25", "2025-26"])
    if st.button("🧮 Calculate Average"):
        cp_vals = []
        for y in years_to_avg:
            p = f"saved_clients/{company_name.replace(' ', '_')}_{y}.csv"
            if os.path.exists(p):
                data = pd.read_csv(p)
                add_back = data[data['Add Back'] == True]['Amount'].sum()
                cp_vals.append(add_back) 
        if cp_vals: st.metric("Average Cash Profit", f"₹{sum(cp_vals)/len(cp_vals):,.2f}")
