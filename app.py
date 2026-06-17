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

def generate_mock_emails(company, role, skills, experience, num_variations):
    variations = [
        {
            "subject": f"Inquiry: Connecting regarding {role} roles at {company}",
            "body": f"Hi team,\n\nI hope you're doing well.\n\nI've been following {company}'s work in engineering and was very impressed by your progress. I noticed you are expanding your team for {role} positions.\n\nWith {experience} years of experience specializing in {skills}, I have built similar systems and would love to see if I could add value to your team. Are you open to a brief chat next week to discuss potential alignment?\n\nBest regards,\n[Your Name]"
        },
        {
            "subject": f"Interested in {role} opportunities at {company}",
            "body": f"Hello,\n\nI hope this email finds you well.\n\nI am reaching out because I am very interested in the {role} position at {company}. I have spent the last {experience} years honing my skills in {skills}, and I am confident that my background aligns well with your team's current focus.\n\nI would appreciate the opportunity to connect and learn more about what you're building. Please let me know if you have 10 minutes to sync.\n\nThanks,\n[Your Name]"
        },
        {
            "subject": f"Skills match for {role} at {company}",
            "body": f"Hi there,\n\nI'm writing to express my interest in the {role} opening at {company}.\n\nGiven my experience ({experience} years) with {skills}, I am excited about the prospect of contributing to {company}'s upcoming milestones.\n\nWould you be open to a quick call to explore how my skills could support your engineering goals?\n\nSincerely,\n[Your Name]"
        },
        {
            "subject": f"Let's connect / {role} search at {company}",
            "body": f"Hi,\n\nI hope your week is going well.\n\nI'm a software engineer with {experience} years of experience, and I've been looking closely at the {role} position at {company}.\n\nMy core technical expertise includes {skills}, which seems to be a strong fit for your current engineering stack.\n\nDo you have a few minutes for a quick introductory call next Tuesday?\n\nWarmly,\n[Your Name]"
        },
        {
            "subject": f"Value proposition for {company}'s {role} opening",
            "body": f"Dear Hiring Team,\n\nI hope you are having a productive week.\n\nI am reaching out to highlight my candidacy for the {role} position at {company}. With a track record of {experience} years working with tools like {skills}, I can jump in and contribute immediately.\n\nI'd love to share more about how my profile fits your current needs. Let me know if we can connect.\n\nBest,\n[Your Name]"
        }
    ]
    return variations[:num_variations]

def render_email_generation_ui(lead, key_prefix):
    company = lead.get('Company Name', lead.get('company_name', ''))
    role = lead.get('Target Role', lead.get('target_role', ''))
    skills = lead.get('My Skills', lead.get('my_skills', ''))
    
    # Safely handle experience parsing/display
    exp_val = lead.get('Experience (Years)', lead.get('experience_years', 0.0))
    try:
        exp = f"{float(exp_val):.1f}"
    except (ValueError, TypeError):
        exp = str(exp_val)
        
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown(f"### ✉️ Create Emails for {company}")
    st.write(f"Customize and generate outreach emails for the **{role}** position.")
    
    # Variations selection button / radio
    num_variations = st.radio(
        "Select number of variations of emails to be generated:",
        options=[1, 2, 3, 4, 5],
        index=2, # default to 3
        horizontal=True,
        key=f"{key_prefix}_num_vars"
    )
    
    lead_id = f"{company}_{role}"
    state_lead_id_key = f"{key_prefix}_current_lead_id"
    session_key = f"{key_prefix}_generated_emails"
    
    if st.session_state.get(state_lead_id_key) != lead_id:
        st.session_state[state_lead_id_key] = lead_id
        if session_key in st.session_state:
            del st.session_state[session_key]
            
    generate_clicked = st.button("Generate Email Variations", type="primary", key=f"{key_prefix}_generate_btn")
    
    if generate_clicked:
        with st.spinner("Generating email variations..."):
            emails = generate_mock_emails(company, role, skills, exp, num_variations)
            st.session_state[session_key] = emails
            st.success(f"🎉 Generated {len(emails)} variations!")
            
    if session_key in st.session_state:
        emails = st.session_state[session_key]
        if emails:
            st.markdown("#### 📄 Generated Email Variations")
            tabs = st.tabs([f"Variation {i+1}" for i in range(len(emails))])
            for i, tab in enumerate(tabs):
                with tab:
                    email_data = emails[i]
                    st.markdown(f"**Subject:** {email_data['subject']}")
                    st.code(email_data['body'], language="text")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 1: CSV IMPORT & PARSE ---
with tab_csv:
    st.markdown("### 📥 Import Leads from CSV")
    st.write("Upload a CSV file — all leads will be automatically saved to the database. Select any lead from the table to generate email variations.")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            columns = list(df.columns)
            auto_mapping = auto_map_columns(columns)
            
            # Map columns silently behind the scenes
            company_col = auto_mapping.get('company_name', columns[0] if columns else None)
            email_col = auto_mapping.get('email', columns[0] if columns else None)
            role_col = auto_mapping.get('target_role', columns[0] if columns else None)
            focus_col = auto_mapping.get('company_focus', columns[0] if columns else None)
            skills_col = auto_mapping.get('my_skills', columns[0] if columns else None)
            exp_col = auto_mapping.get('experience_years', columns[0] if columns else None)
            
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
            
            # Auto-save all leads to the database once per unique file upload
            file_key = f"csv_saved_{uploaded_file.name}_{len(mapped_df)}"
            if not st.session_state.get(file_key):
                leads_to_save = []
                for _, row in mapped_df.iterrows():
                    leads_to_save.append({
                        'company_name': row['Company Name'],
                        'email': row['Email'],
                        'target_role': row['Target Role'],
                        'company_focus': row['Company Focus'],
                        'my_skills': row['My Skills'],
                        'experience_years': row['Experience (Years)']
                    })
                database.save_leads_batch(leads_to_save)
                st.session_state[file_key] = True
                st.success(f"🎉 {len(leads_to_save)} leads automatically saved to the database!")
            
            # Render selection area
            st.markdown("### 📋 Parsed Leads List")
            st.info("Select a lead from the table below to generate email variations.")
            
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
            
            # If leads are selected, display the Create Emails feature
            if selected_rows:
                # If multiple are selected, show dropdown to choose one
                if len(selected_rows) > 1:
                    lead_options = [f"{mapped_df.iloc[idx]['Company Name']} ({mapped_df.iloc[idx]['Target Role']})" for idx in selected_rows]
                    selected_lead_idx = st.selectbox(
                        "Select a lead to generate emails for:",
                        options=range(len(selected_rows)),
                        format_func=lambda x: lead_options[x],
                        key="csv_lead_selector"
                    )
                    chosen_lead = mapped_df.iloc[selected_rows[selected_lead_idx]]
                else:
                    chosen_lead = mapped_df.iloc[selected_rows[0]]
                
                # Render the email generation UI
                render_email_generation_ui(chosen_lead, "csv")
                    
        except Exception as e:
            st.error(f"Error parsing CSV file: {str(e)}")

# --- TAB 2: MANUAL LEAD ENTRY ---
with tab_manual:
    st.markdown("### 📝 Enter Lead Details Manually")
    st.write("Fill in the lead details below — it will be saved automatically and you can immediately generate cold email variations.")
    
    with st.form("manual_lead_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company Name *", placeholder="e.g. Acme Corp")
            email = st.text_input("Contact Email *", placeholder="e.g. recruitment@acme.com")
            target_role = st.text_input("Target Role *", placeholder="e.g. Senior Software Engineer")
        
        with col2:
            experience_years = st.number_input(
                "Years of Experience *", 
                min_value=0.0, 
                max_value=50.0, 
                value=0.0, 
                step=0.5
            )
            company_focus = st.text_area(
                "Company's Focus / Areas of Focus *", 
                placeholder="e.g. Enterprise SaaS, Artificial Intelligence, Cybersecurity",
                height=68
            )
            my_skills = st.text_area(
                "My Skills (Relevant to role) *", 
                placeholder="e.g. Python, Streamlit, Docker, Machine Learning",
                height=68
            )
            
        submitted = st.form_submit_button("➕ Add Lead")
        
        if submitted:
            errors = []
            if not company_name.strip():
                errors.append("Company Name")
            if not email.strip():
                errors.append("Contact Email")
            elif "@" not in email:
                errors.append("Contact Email (must be a valid address)")
            if not target_role.strip():
                errors.append("Target Role")
            if experience_years <= 0.0:
                errors.append("Years of Experience (must be greater than 0)")
            if not company_focus.strip():
                errors.append("Company's Focus")
            if not my_skills.strip():
                errors.append("My Skills")
            
            if errors:
                st.error("Please complete the following required fields:\n- " + "\n- ".join(errors))
            else:
                database.save_lead(
                    company_name=company_name,
                    email=email,
                    target_role=target_role,
                    company_focus=company_focus,
                    my_skills=my_skills,
                    experience_years=experience_years
                )
                st.success(f"🎉 Lead for '{company_name}' saved! Now generate emails below.")
                # Persist this lead in session state so the email UI appears below
                st.session_state['manual_last_lead'] = {
                    'Company Name': company_name,
                    'Target Role': target_role,
                    'My Skills': my_skills,
                    'Experience (Years)': experience_years
                }
    
    # Show email generation UI for the most recently added manual lead
    if 'manual_last_lead' in st.session_state:
        render_email_generation_ui(st.session_state['manual_last_lead'], "manual")

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
                # If multiple are selected, show dropdown to choose one
                if len(selected_db_rows) > 1:
                    lead_options = [f"{db_df_display.iloc[idx]['Company Name']} ({db_df_display.iloc[idx]['Target Role']})" for idx in selected_db_rows]
                    selected_lead_idx = st.selectbox(
                        "Select a lead to generate emails for:",
                        options=range(len(selected_db_rows)),
                        format_func=lambda x: lead_options[x],
                        key="db_lead_selector"
                    )
                    chosen_lead = db_df_display.iloc[selected_db_rows[selected_lead_idx]]
                else:
                    chosen_lead = db_df_display.iloc[selected_db_rows[0]]
                
                # Render the email generation UI
                render_email_generation_ui(chosen_lead, "db")
                
                # Delete options
                st.markdown("---")
                selected_ids = db_df_display.iloc[selected_db_rows]['ID'].tolist()
                st.warning(f"⚠️ You have selected {len(selected_ids)} lead(s) for deletion.")
                if st.button("🗑️ Delete Selected Leads", key="btn_delete_db"):
                    database.delete_leads(selected_ids)
                    st.success("Selected leads deleted successfully!")
                    st.rerun()
