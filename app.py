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

# 3. SIDEBAR: KYC, LOANS & REFERENCES
with st.sidebar:
    st.header("📂 Client List Dashboard")
    all_files = [f for f in os.listdir("saved_clients") if f.endswith('.csv')]
    if all_files:
        unique_firms = sorted(list(set([f.split('_20')[0].replace('_', ' ') for f in all_files])))
        st.write(f"Total Firms Managed: **{len(unique_firms)}**")
        for firm in unique_firms:
            st.markdown(f"🔹 {firm}")
    
    st.divider()
    st.header("👤 Customer & KYC Dossier")
    company_name = st.text_input("Firm Name", "M/s Rudra Earthmovers")
    selected_fy = st.selectbox("Financial Year", ["2023-24", "2024-25", "2025-26"])
    firm_type = st.selectbox("Firm Category", ["Trading Firm", "Service Provider", "Manufacturing"])

    # MULTI-APPLICANT KYC
    num_applicants = st.number_input("Number of Applicants", min_value=1, value=1, step=1)
    applicant_summary = []
    for i in range(int(num_applicants)):
        with st.expander(f"Applicant {i+1} Details", expanded=(i==0)):
            app_name = st.text_input(f"Applicant Name", key=f"app_name_{i}")
            st.date_input(f"DOB", key=f"app_dob_{i}")
            st.text_input(f"Mother's Name", key=f"app_moth_{i}")
            st.text_input(f"Mobile No.", key=f"app_mob_{i}")
            st.checkbox("Light Bill collected", key=f"lb_{i}")
            st.checkbox("Photo collected", key=f"ph_{i}")
            applicant_summary.append({"Applicant": app_name})

    # NEW: REFERENCES SECTION
    st.divider()
    st.header("📞 References")
    for r in range(1, 4):
        with st.expander(f"Reference {r}", expanded=False):
            st.text_input(f"Ref {r} Name", key=f"ref_name_{r}")
            st.text_input(f"Ref {r} Contact Number", key=f"ref_num_{r}")

    # RUNNING LOAN TRACKER
    st.divider()
    st.header("💳 Running Loans")
    num_loans = st.number_input("Existing Loans?", min_value=0, value=0)
    for j in range(int(num_loans)):
        with st.expander(f"Loan {j+1}", expanded=False):
            st.text_input("Bank Name", key=f"ln_bnk_{j}")
            st.number_input("Current Balance", key=f"ln_amt_{j}")
            st.checkbox("Sanction Letter collected", key=f"ln_sanc_{j}")

# 4. MAIN INTERFACE
def load_template(form_type, firm_cat):
    file_path = f"templates/{firm_cat.replace(' ', '_')}_{form_type}.csv"
    if os.path.exists(file_path): return pd.read_csv(file_path)
    if form_type == "PL":
        return pd.DataFrame({"Particulars": ["Sales", "Purchases", "Salaries", "Depreciation"], "Amount": [0.0]*4, "Add Back": [False]*4})
    return pd.DataFrame({"Particulars": ["Proprietor's Capital", "Sundry Creditors", "Sundry Debtors", "Cash-in-Hand"], "Amount": [0.0]*4})

st.title(f"Financial Reporting: {company_name}")
t_input, t_report, t_analysis = st.tabs(["📝 Input Sheet", "📈 Final Reports", "🧮 Cash Profit Analysis"])

with t_input:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Profit & Loss Account")
        pl_ed = st.data_editor(load_template("PL", firm_type), key=f"pl_{firm_type}", num_rows="dynamic", use_container_width=True,
                               column_config={"Particulars": st.column_config.SelectboxColumn("Account Head", options=TRADING_PL_HEADS)})
        if st.button(f"💾 Save Default P&L"):
            pl_ed.to_csv(f"templates/{firm_type.replace(' ', '_')}_PL.csv", index=False)
            st.success("Template Saved!")

    with c2:
        st.subheader("Balance Sheet")
        bs_ed = st.data_editor(load_template("BS", firm_type), key=f"bs_{firm_type}", num_rows="dynamic", use_container_width=True,
                               column_config={"Particulars": st.column_config.SelectboxColumn("Account Head", options=BALANCE_SHEET_HEADS)})
        if st.button(f"💾 Save Default BS"):
            bs_ed.to_csv(f"templates/{firm_type.replace(' ', '_')}_BS.csv", index=False)
            st.success("Template Saved!")

    if st.button("🚀 SAVE CLIENT DATA"):
        file_path = f"saved_clients/{company_name.replace(' ', '_')}_{selected_fy}.csv"
        pd.concat([pl_ed, bs_ed], ignore_index=True).to_csv(file_path, index=False)
        st.success(f"Dossier for {company_name} saved!")

with t_report:
    if st.button("📊 GENERATE BANK SUMMARY"):
        st.markdown(f'<div style="background-color:#5B9BD5;color:white;text-align:center;padding:10px;font-weight:bold;font-size:24px;">BANK LOAN APPLICATION SUMMARY</div>', unsafe_allow_html=True)
        st.subheader("Reference Details")
        refs = [{"Reference": f"Ref {r}", "Name": st.session_state[f"ref_name_{r}"], "Contact": st.session_state[f"ref_num_{r}"]} for r in range(1, 4)]
        st.table(pd.DataFrame(refs))
