# --- PART 1: COMPANY & PERIOD INFO ---
st.sidebar.header("🏢 Report Details")
company_name = st.sidebar.text_input("Company Name", "M/s Rudra Earthmovers") # Default from your firm
address = st.sidebar.text_area("Address", "Udaipur, Rajasthan") # Default location
financial_year = st.sidebar.text_input("Financial Year", "1-APR-2024 TO 31-MAR-2025")

# --- PART 2: THE UPDATED DISPLAY LOGIC ---
if st.button("Generate Reports"):
    gp, np = generate_reports(edited_df)
    
    tab1, tab2 = st.tabs(["Profit & Loss Account", "Balance Sheet"])
    
    with tab1:
        # Header for P&L
        st.markdown(f'<div class="report-header">{company_name.upper()}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center;">{address}</div>', unsafe_allow_html=True)
        st.markdown('<div class="blue-header">Profit & Loss A/c</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center; font-weight:bold;">{financial_year}</div>', unsafe_allow_html=True)
        
        # ... (rest of your P&L code)
        
    with tab2:
        # Header for Balance Sheet
        st.markdown(f'<div class="report-header">{company_name.upper()}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center;">{address}</div>', unsafe_allow_html=True)
        st.markdown('<div class="blue-header">Balance Sheet</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center; font-weight:bold;">As on {financial_year.split("TO")[-1].strip()}</div>', unsafe_allow_html=True)
        
        # ... (rest of your Balance Sheet code)
