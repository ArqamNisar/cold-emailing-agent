import streamlit as st
import pandas as pd
import database

# Initialize database
database.init_db()

# Page setup
st.set_page_config(
    page_title="Cold Email Lead Generator",
    page_icon="✉️",
    layout="wide"
)

# Custom CSS for rich aesthetics (Inter font, sleek slate colors, glassmorphism)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Premium Header styling */
    .title-container {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        background: radial-gradient(circle at top, rgba(99, 102, 241, 0.15) 0%, transparent 60%);
        border-radius: 20px;
    }
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #a5b4fc 0%, #6366f1 50%, #4338ca 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.15rem;
        color: #94a3b8;
        font-weight: 400;
    }
    
    /* Card design system */
    .card-container {
        background: rgba(30, 41, 59, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 2rem;
        backdrop-filter: blur(12px);
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
    }
    
    /* Form inputs and buttons styling rules */
    div[data-testid="stForm"] {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
        padding: 2rem !important;
    }
    
    /* Clean badge for selection indicator */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        font-size: 0.85rem;
        font-weight: 600;
        color: #6366f1;
        background-color: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 9999px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown("""
<div class="title-container">
    <h1 class="main-title">Cold Email Lead Generator</h1>
    <p class="subtitle">Streamline your cold outreach by importing and managing targeted leads</p>
</div>
""", unsafe_allow_html=True)

# Setup navigation tabs
tab_csv, tab_manual, tab_db = st.tabs([
    "📥 CSV Import & Parse", 
    "📝 Manual Lead Entry", 
    "🗂️ Leads Database Explorer"
])

def auto_map_columns(columns):
    """Fuzzy match CSV columns to expected database fields."""
    mapping = {}
    standard_fields = {
        'company_name': ['company name', 'company', 'name', 'firm', 'organization'],
        'email': ['email', 'email address', 'mail', 'contact', 'email_address'],
        'target_role': ['target role', 'role', 'position', 'job title', 'title', 'target_role'],
        'company_focus': ['focus', 'company focus', 'areas of focus', 'industry', 'domain', 'focus_areas', 'company_focus'],
        'my_skills': ['my skills', 'skills', 'skill', 'technologies', 'tech stack', 'my_skills'],
        'experience_years': ['experience', 'years of experience', 'experience years', 'exp', 'years', 'experience_years']
    }
    
    for field, variations in standard_fields.items():
        found = False
        # 1. Try case-insensitive exact match
        for col in columns:
            if col.strip().lower() == field:
                mapping[field] = col
                found = True
                break
        
        # 2. Try substring match on variations
        if not found:
            for col in columns:
                col_lower = col.strip().lower()
                if any(var in col_lower for var in variations):
                    mapping[field] = col
                    found = True
                    break
                    
        # 3. Default to first column if no match
        if not found:
            mapping[field] = columns[0] if len(columns) > 0 else None
            
    return mapping

# --- TAB 1: CSV IMPORT & PARSE ---
with tab_csv:
    st.markdown("### 📥 Import Leads from CSV")
    st.write("Upload a CSV file containing your leads. You can map custom column headers, preview parsed results, and selectively save leads to the local database.")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.markdown("#### 🔍 Column Mapping Setup")
            st.write("Confirm which CSV column maps to each field in the database:")
            
            columns = list(df.columns)
            auto_mapping = auto_map_columns(columns)
            
            col1, col2, col3 = st.columns(3)
            col4, col5, col6 = st.columns(3)
            
            with col1:
                company_col = st.selectbox(
                    "Company Name column", 
                    columns, 
                    index=columns.index(auto_mapping['company_name']) if auto_mapping['company_name'] in columns else 0
                )
            with col2:
                email_col = st.selectbox(
                    "Email column", 
                    columns, 
                    index=columns.index(auto_mapping['email']) if auto_mapping['email'] in columns else 0
                )
            with col3:
                role_col = st.selectbox(
                    "Target Role column", 
                    columns, 
                    index=columns.index(auto_mapping['target_role']) if auto_mapping['target_role'] in columns else 0
                )
            with col4:
                focus_col = st.selectbox(
                    "Company Focus column", 
                    columns, 
                    index=columns.index(auto_mapping['company_focus']) if auto_mapping['company_focus'] in columns else 0
                )
            with col5:
                skills_col = st.selectbox(
                    "My Skills column", 
                    columns, 
                    index=columns.index(auto_mapping['my_skills']) if auto_mapping['my_skills'] in columns else 0
                )
            with col6:
                exp_col = st.selectbox(
                    "Experience (Years) column", 
                    columns, 
                    index=columns.index(auto_mapping['experience_years']) if auto_mapping['experience_years'] in columns else 0
                )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Map user selection to standard DataFrame
            mapped_df = pd.DataFrame()
            mapped_df['Company Name'] = df[company_col].astype(str)
            mapped_df['Email'] = df[email_col].astype(str)
            mapped_df['Target Role'] = df[role_col].astype(str)
            mapped_df['Company Focus'] = df[focus_col].astype(str)
            mapped_df['My Skills'] = df[skills_col].astype(str)
            
            # Safely parse experience to float
            def parse_exp(val):
                try:
                    if pd.isna(val) or str(val).strip() == "":
                        return 0.0
                    # Extract numeric digits if someone typed "3 years"
                    nums = ''.join(c for c in str(val) if c.isdigit() or c == '.')
                    return float(nums) if nums else 0.0
                except ValueError:
                    return 0.0
            
            mapped_df['Experience (Years)'] = df[exp_col].apply(parse_exp)
            
            # Render selection area
            st.markdown("### 📋 Parsed Leads List")
            st.info("Check/select the rows you want to import, then click 'Save Selected Leads' below.")
            
            # Display interactive selection dataframe
            event = st.dataframe(
                mapped_df,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="multi-row"
            )
            
            selected_rows = event.selection.rows
            
            # Visual counter badge
            st.markdown(f'<div class="badge">{len(selected_rows)} of {len(mapped_df)} rows selected</div>', unsafe_allow_html=True)
            
            # Action button
            if st.button("Save Selected Leads to Database", key="btn_save_csv"):
                if not selected_rows:
                    st.warning("No leads selected. Please click on the left edge of table rows to select them.")
                else:
                    leads_to_save = []
                    for idx in selected_rows:
                        row = mapped_df.iloc[idx]
                        leads_to_save.append({
                            'company_name': row['Company Name'],
                            'email': row['Email'],
                            'target_role': row['Target Role'],
                            'company_focus': row['Company Focus'],
                            'my_skills': row['My Skills'],
                            'experience_years': row['Experience (Years)']
                        })
                    
                    database.save_leads_batch(leads_to_save)
                    st.success(f"🎉 Successfully imported {len(leads_to_save)} leads into SQLite!")
                    
        except Exception as e:
            st.error(f"Error parsing CSV file: {str(e)}")

# --- TAB 2: MANUAL LEAD ENTRY ---
with tab_manual:
    st.markdown("### 📝 Enter Lead Details Manually")
    st.write("Add a single lead directly to the database by filling out the form below.")
    
    with st.form("manual_lead_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company Name *", placeholder="e.g. Acme Corp")
            email = st.text_input("Contact Email *", placeholder="e.g. recruitment@acme.com")
            target_role = st.text_input("Target Role *", placeholder="e.g. Senior Software Engineer")
        
        with col2:
            experience_years = st.number_input(
                "Number of Years of Experience", 
                min_value=0.0, 
                max_value=50.0, 
                value=2.0, 
                step=0.5
            )
            company_focus = st.text_area(
                "Company's Focus / Areas of Focus", 
                placeholder="e.g. Enterprise SaaS, Artificial Intelligence, Cybersecurity",
                height=68
            )
            my_skills = st.text_area(
                "My Skills (Relevant to role)", 
                placeholder="e.g. Python, Streamlit, Docker, Machine Learning",
                height=68
            )
            
        submitted = st.form_submit_button("Save Lead to Database")
        
        if submitted:
            if not company_name.strip() or not email.strip() or not target_role.strip():
                st.error("Please fill out all required fields (*).")
            elif "@" not in email:
                st.error("Please enter a valid email address.")
            else:
                database.save_lead(
                    company_name=company_name,
                    email=email,
                    target_role=target_role,
                    company_focus=company_focus,
                    my_skills=my_skills,
                    experience_years=experience_years
                )
                st.success(f"🎉 Lead for '{company_name}' has been saved to SQLite successfully!")

# --- TAB 3: LEADS DATABASE EXPLORER ---
with tab_db:
    st.markdown("### 🗂️ Leads Database Explorer")
    st.write("Browse, search, and delete leads stored in your local SQLite database.")
    
    # Reload leads
    leads = database.get_all_leads()
    
    if not leads:
        st.info("The database is currently empty. Go ahead and add some leads using CSV Import or Manual Entry.")
    else:
        db_df = pd.DataFrame(leads)
        
        # Format columns for display
        db_df_display = db_df.copy()
        # Reorder columns for a nicer view
        cols_display = [
            'id', 'company_name', 'email', 'target_role', 
            'company_focus', 'my_skills', 'experience_years', 'created_at'
        ]
        db_df_display = db_df_display[cols_display]
        db_df_display.columns = [
            'ID', 'Company Name', 'Email Address', 'Target Role', 
            'Company Focus', 'My Skills', 'Experience (Years)', 'Created At'
        ]
        
        # Search & Filter
        search_query = st.text_input("🔍 Search Leads", placeholder="Search by Company, Email, Role, Focus, or Skills...")
        if search_query.strip():
            q = search_query.lower().strip()
            db_df_display = db_df_display[
                db_df_display['Company Name'].str.lower().str.contains(q) |
                db_df_display['Email Address'].str.lower().str.contains(q) |
                db_df_display['Target Role'].str.lower().str.contains(q) |
                db_df_display['Company Focus'].str.lower().str.contains(q) |
                db_df_display['My Skills'].str.lower().str.contains(q)
            ]
            
        st.markdown(f'<div class="badge">{len(db_df_display)} lead(s) found</div>', unsafe_allow_html=True)
        
        if db_df_display.empty:
            st.warning("No database records match your search criteria.")
        else:
            # Table with row selection for deletion
            db_event = st.dataframe(
                db_df_display,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="multi-row"
            )
            
            selected_db_rows = db_event.selection.rows
            
            if selected_db_rows:
                selected_ids = db_df_display.iloc[selected_db_rows]['ID'].tolist()
                st.warning(f"⚠️ You have selected {len(selected_ids)} lead(s) for deletion.")
                if st.button("🗑️ Delete Selected Leads", key="btn_delete_db"):
                    database.delete_leads(selected_ids)
                    st.success("Selected leads deleted successfully!")
                    st.rerun()
