import streamlit as st
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

import database
from agents.analyzer_agent import run_analyzer
from agents.email_writer_agent import run_email_writer
from agents.email_templates import (
    ALL_TEMPLATES, CATEGORIES, CATEGORY_ICONS,
    get_template, get_templates_by_category
)
from logger import get_logger

log = get_logger(__name__)

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

    /* ── Template Library Cards ─────────────────────────────────────── */
    .template-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin: 1rem 0 1.5rem 0;
    }
    .template-card {
        background: rgba(30, 41, 59, 0.55);
        border: 1.5px solid rgba(255, 255, 255, 0.07);
        border-radius: 14px;
        padding: 1.2rem 1rem;
        cursor: pointer;
        transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
        position: relative;
        min-height: 130px;
    }
    .template-card:hover {
        transform: translateY(-4px);
        border-color: rgba(99, 102, 241, 0.45);
        box-shadow: 0 8px 28px rgba(99, 102, 241, 0.18);
    }
    .template-card.selected {
        border-color: #6366f1;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.35), 0 8px 28px rgba(99, 102, 241, 0.25);
        background: rgba(99, 102, 241, 0.12);
    }
    .template-card .tc-icon {
        font-size: 1.8rem;
        margin-bottom: 0.4rem;
        display: block;
    }
    .template-card .tc-name {
        font-size: 0.95rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 0.3rem;
    }
    .template-card .tc-tagline {
        font-size: 0.78rem;
        color: #94a3b8;
        line-height: 1.4;
    }
    .template-card .tc-example {
        margin-top: 0.6rem;
        font-size: 0.72rem;
        color: #6366f1;
        font-style: italic;
        border-left: 2px solid rgba(99,102,241,0.4);
        padding-left: 0.5rem;
        line-height: 1.35;
    }
    .template-card .tc-selected-badge {
        position: absolute;
        top: 0.55rem;
        right: 0.65rem;
        background: #6366f1;
        color: #fff;
        font-size: 0.65rem;
        font-weight: 700;
        padding: 0.15rem 0.45rem;
        border-radius: 9999px;
        letter-spacing: 0.03em;
    }
    .template-section-header {
        font-size: 1.05rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 0.25rem;
    }
    .template-section-sub {
        font-size: 0.82rem;
        color: #94a3b8;
        margin-bottom: 0.9rem;
    }
    .template-card .tc-meta {
        display: flex;
        gap: 0.4rem;
        flex-wrap: wrap;
        margin-top: 0.55rem;
    }
    .tc-pill {
        display: inline-block;
        padding: 0.15rem 0.5rem;
        font-size: 0.68rem;
        font-weight: 600;
        border-radius: 9999px;
        letter-spacing: 0.02em;
        text-transform: capitalize;
    }
    .tc-pill-tone  { background: rgba(99,102,241,0.18); color: #a5b4fc; border: 1px solid rgba(99,102,241,0.3); }
    .tc-pill-len   { background: rgba(16,185,129,0.15); color: #6ee7b7; border: 1px solid rgba(16,185,129,0.3); }
    .tc-pill-style { background: rgba(251,191,36,0.13); color: #fcd34d; border: 1px solid rgba(251,191,36,0.25); }
    .tc-use-cases {
        margin-top: 0.55rem;
        padding-left: 1rem;
        font-size: 0.72rem;
        color: #94a3b8;
        line-height: 1.6;
    }
    .tc-use-cases li { margin-bottom: 0.1rem; }
    @media (max-width: 900px) {
        .template-grid { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 560px) {
        .template-grid { grid-template-columns: 1fr; }
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
    """Fallback mock generator used when the LLM writer agent fails."""
    log.info("Generating %d MOCK emails | company='%s' role='%s'", num_variations, company, role)
    variations = [
        {
            "subject": f"Inquiry: Connecting regarding {role} roles at {company}",
            "body": f"Hi team,\n\nI hope you're doing well.\n\nI've been following {company}'s work and was very impressed by your progress. I noticed you are expanding your team for {role} positions.\n\nWith {experience} years of experience specialising in {skills}, I have built similar systems and would love to see if I could add value to your team. Are you open to a brief chat next week?\n\nBest regards"
        },
        {
            "subject": f"Interested in {role} opportunities at {company}",
            "body": f"Hello,\n\nI am reaching out because I am very interested in the {role} position at {company}. I have spent the last {experience} years honing my skills in {skills}, and I am confident that my background aligns well with your team's current focus.\n\nI would appreciate the opportunity to connect and learn more about what you're building. Please let me know if you have 10 minutes to sync.\n\nThanks"
        },
        {
            "subject": f"Skills match for {role} at {company}",
            "body": f"Hi there,\n\nI'm writing to express my interest in the {role} opening at {company}.\n\nGiven my experience ({experience} years) with {skills}, I am excited about the prospect of contributing to {company}'s upcoming milestones.\n\nWould you be open to a quick call to explore how my skills could support your goals?\n\nSincerely"
        },
        {
            "subject": f"Let's connect — {role} at {company}",
            "body": f"Hi,\n\nI'm a professional with {experience} years of experience and I've been looking closely at the {role} position at {company}.\n\nMy core expertise includes {skills}, which seems to be a strong fit for your current needs.\n\nDo you have a few minutes for a quick introductory call?\n\nWarmly"
        },
        {
            "subject": f"Value proposition for {company}'s {role} opening",
            "body": f"Dear Hiring Team,\n\nI am reaching out to highlight my candidacy for the {role} position at {company}. With a track record of {experience} years working with {skills}, I can jump in and contribute immediately.\n\nI'd love to share more about how my profile fits your current needs. Let me know if we can connect.\n\nBest"
        }
    ]
    return variations[:num_variations]

def render_email_generation_ui(lead, key_prefix):
    company = lead.get('Company Name', lead.get('company_name', ''))
    role = lead.get('Target Role', lead.get('target_role', ''))
    skills = lead.get('My Skills', lead.get('my_skills', ''))

    exp_val = lead.get('Experience (Years)', lead.get('experience_years', 0.0))
    try:
        exp = f"{float(exp_val):.1f}"
    except (ValueError, TypeError):
        exp = str(exp_val)

    lead_id = f"{company}_{role}"
    state_lead_id_key  = f"{key_prefix}_current_lead_id"
    session_key        = f"{key_prefix}_generated_emails"
    analysis_key       = f"{key_prefix}_analysis"

    # Reset generated state when a different lead is selected
    if st.session_state.get(state_lead_id_key) != lead_id:
        st.session_state[state_lead_id_key] = lead_id
        for k in (session_key, analysis_key):
            if k in st.session_state:
                del st.session_state[k]

    # ── Template selection state key (per tab prefix) ────────────────────
    template_key = f"{key_prefix}_selected_template"
    if template_key not in st.session_state:
        st.session_state[template_key] = ALL_TEMPLATES[0].id   # default: Value Prop

    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown(f"### ✉️ Create Emails for **{company}**")
    st.write(f"Targeting the **{role}** position.")

    # ── Flow 1: Lead not yet analyzed ─────────────────────────────────────
    if analysis_key not in st.session_state:
        st.write("Analyse the lead's business focus and role to determine the best cold-email outreach strategy.")
        
        analyze_clicked = st.button(
            "🔍 Run Lead Analysis",
            type="primary",
            key=f"{key_prefix}_analyze_btn"
        )
        
        if analyze_clicked:
            log.info("Run Lead Analysis clicked | lead='%s'", lead_id)
            with st.spinner("🔍 Running lead analyzer (LangGraph)…"):
                analysis = run_analyzer(lead)
                st.session_state[analysis_key] = analysis
                # Clear previous generated emails if any
                if session_key in st.session_state:
                    del st.session_state[session_key]
                st.rerun()

    # ── Flow 2: Lead has been analyzed ────────────────────────────────────
    else:
        analysis = st.session_state[analysis_key]
        if analysis.get("error") and not analysis.get("company_industry"):
            st.warning(f"⚠️ Analyzer ran in fallback mode: {analysis['error']}")

        with st.expander("🔬 Lead Analysis Report", expanded=True):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**📊 Input Analysis**")
                st.markdown(f"- **Industry:** {analysis.get('company_industry', '—')}")
                st.markdown(f"- **Value Proposition:** {analysis.get('value_proposition', '—')}")
                st.markdown(f"- **Audience Size:** {analysis.get('target_audience', '—').capitalize()}")
                st.markdown(f"- **Email Goal:** {analysis.get('email_goal', '—').capitalize()}")
            with col_b:
                st.markdown("**🎯 Email Strategy**")
                st.markdown(f"- **Tone:** {analysis.get('tone', '—').capitalize()}")
                st.markdown(f"- **Length:** {analysis.get('email_length', '—').capitalize()} ({analysis.get('word_range', '')})")
                hooks = analysis.get('key_hooks', [])
                if hooks:
                    st.markdown("- **Key Hooks:**")
                    for h in hooks:
                        st.markdown(f"  - {h}")

        st.markdown("---")
        
        # Action controls: Re-analyse (left) vs Generate (right)
        col_ctrl1, col_ctrl2 = st.columns([1, 2])
        
        with col_ctrl1:
            st.markdown("#### 🔄 Adjust Strategy")
            st.write("Not satisfied with the analysis? Run the LangGraph agent again.")
            reanalyze_clicked = st.button(
                "🔄 Re-analyse Lead",
                type="secondary",
                key=f"{key_prefix}_reanalyze_btn"
            )
            if reanalyze_clicked:
                log.info("Re-analyse Lead clicked | lead='%s'", lead_id)
                with st.spinner("🔄 Re-running lead analyzer (LangGraph)…"):
                    analysis = run_analyzer(lead)
                    st.session_state[analysis_key] = analysis
                    # Clear previous generated emails
                    if session_key in st.session_state:
                        del st.session_state[session_key]
                    st.rerun()

        with col_ctrl2:
            st.markdown("#### 🚀 Cold Emails")
            st.write("Ready to draft? Choose the number of email variations to generate.")
            
            num_variations = st.radio(
                "Number of email variations to generate:",
                options=[1, 2, 3, 4, 5],
                index=2,
                horizontal=True,
                key=f"{key_prefix}_num_vars"
            )

        # ── Template Library ─────────────────────────────────────────────
        st.markdown("---")
        st.markdown('<p class="template-section-header">📚 Template Library — Choose Your Email Approach</p>', unsafe_allow_html=True)
        st.markdown('<p class="template-section-sub">Browse templates by category. Each template defines the structure, tone, and style the AI writer will follow when generating your emails.</p>', unsafe_allow_html=True)

        current_template_id = st.session_state.get(template_key, ALL_TEMPLATES[0].id)

        # Category tabs — one tab per category
        cat_tab_labels = [
            f"{CATEGORY_ICONS[cat]} {cat}" for cat in CATEGORIES
        ]
        cat_tabs = st.tabs(cat_tab_labels)

        for cat_tab, category in zip(cat_tabs, CATEGORIES):
            with cat_tab:
                cat_templates = get_templates_by_category(category)
                # 2 cards per row
                for row_start in range(0, len(cat_templates), 2):
                    row_tmpls = cat_templates[row_start : row_start + 2]
                    cols = st.columns(len(row_tmpls))
                    for col, tmpl in zip(cols, row_tmpls):
                        is_selected = (tmpl.id == current_template_id)
                        selected_badge = '<span class="tc-selected-badge">✓ Selected</span>' if is_selected else ''
                        card_class = 'template-card selected' if is_selected else 'template-card'
                        use_cases_html = ''.join(f'<li>{uc}</li>' for uc in tmpl.use_cases)
                        example_short = tmpl.example_opening[:90] + ('…' if len(tmpl.example_opening) > 90 else '')
                        with col:
                            st.markdown(
                                f"""<div class="{card_class}">
    {selected_badge}
    <span class="tc-icon">{tmpl.icon}</span>
    <div class="tc-name">{tmpl.name}</div>
    <div class="tc-tagline">{tmpl.tagline}</div>
    <div class="tc-meta">
        <span class="tc-pill tc-pill-style">{tmpl.style}</span>
        <span class="tc-pill tc-pill-tone">{tmpl.tone}</span>
        <span class="tc-pill tc-pill-len">{tmpl.length} · {tmpl.word_range}</span>
    </div>
    <ul class="tc-use-cases">{use_cases_html}</ul>
    <div class="tc-example">"{example_short}"</div>
</div>""",
                                unsafe_allow_html=True,
                            )
                            btn_label = "✓ Selected" if is_selected else "Use This Template"
                            btn_type  = "primary" if is_selected else "secondary"
                            if st.button(btn_label, key=f"{key_prefix}_tmpl_{tmpl.id}", type=btn_type, use_container_width=True):
                                st.session_state[template_key] = tmpl.id
                                if session_key in st.session_state:
                                    del st.session_state[session_key]
                                st.rerun()

        # Confirmation strip showing active template details
        active_tmpl = get_template(st.session_state.get(template_key, ALL_TEMPLATES[0].id))
        st.markdown(
            f'<div class="badge">{active_tmpl.icon} {active_tmpl.name} &nbsp;·&nbsp; {active_tmpl.tone.capitalize()} &nbsp;·&nbsp; {active_tmpl.word_range}</div>',
            unsafe_allow_html=True,
        )

        # ── Generate button (placed after template selection) ──────────────
        st.markdown("")
        generate_clicked = st.button(
            "🚀 Generate Email Variations",
            type="primary",
            key=f"{key_prefix}_generate_btn"
        )

        if generate_clicked:
            chosen_template = get_template(st.session_state.get(template_key, ALL_TEMPLATES[0].id))
            log.info(
                "Generate clicked | variations=%d | lead='%s' | template='%s'",
                num_variations, lead_id, chosen_template.id,
            )
            with st.spinner(f"✍️ Writing emails using *{chosen_template.name}* approach…"):
                try:
                    emails = run_email_writer(
                        lead=lead,
                        analysis=st.session_state[analysis_key],
                        template=chosen_template,
                        num_variations=num_variations,
                    )
                    log.info("Email writer returned %d email(s)", len(emails))
                except Exception as writer_err:
                    log.warning("Email writer failed (%s) — falling back to mock", writer_err)
                    st.warning(f"⚠️ AI writer encountered an issue — showing template-based drafts instead.")
                    emails = generate_mock_emails(company, role, skills, exp, num_variations)

                st.session_state[session_key] = emails
                st.rerun()

    # ── Show generated emails (if available) ──────────────────────────────
    if session_key in st.session_state:
        emails = st.session_state[session_key]
        if emails:
            st.markdown("---")
            active_tmpl_display = get_template(st.session_state.get(template_key, ALL_TEMPLATES[0].id))
            st.markdown(f"#### 📄 Generated Email Variations &nbsp; <span style='font-size:0.8rem;color:#6366f1;font-weight:600;'>{active_tmpl_display.icon} {active_tmpl_display.name}</span>", unsafe_allow_html=True)
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
        if not st.session_state.get('csv_upload_saved'):
            log.info("Processing new CSV upload: '%s'", uploaded_file.name)
            try:
                df = pd.read_csv(uploaded_file)
                st.session_state['csv_columns'] = df.columns.tolist()
                
                # Auto-map columns
                mapping = auto_map_columns(df.columns.tolist())
                
                # Create mapped dataframe for consistent display
                company_col = mapping.get('company_name', df.columns[0])
                email_col = mapping.get('email', df.columns[0])
                role_col = mapping.get('target_role', df.columns[0])
                focus_col = mapping.get('company_focus', df.columns[0])
                skills_col = mapping.get('my_skills', df.columns[0])
                exp_col = mapping.get('experience_years', df.columns[0])
                
                mapped_df = pd.DataFrame()
                mapped_df['Company Name'] = df[company_col].astype(str)
                mapped_df['Email'] = df[email_col].astype(str)
                mapped_df['Target Role'] = df[role_col].astype(str)
                mapped_df['Company Focus'] = df[focus_col].astype(str)
                mapped_df['My Skills'] = df[skills_col].astype(str)
                
                def parse_exp(val):
                    try:
                        if pd.isna(val) or str(val).strip() == "": return 0.0
                        nums = ''.join(c for c in str(val) if c.isdigit() or c == '.')
                        return float(nums) if nums else 0.0
                    except ValueError:
                        return 0.0
                        
                mapped_df['Experience (Years)'] = df[exp_col].apply(parse_exp)
                st.session_state['csv_data'] = mapped_df
                
                st.success(f"Successfully loaded {len(df)} rows from {uploaded_file.name}")
                
                # Save immediately to DB
                leads_to_save = []
                for _, row in mapped_df.iterrows():
                    lead_data = {
                        'company_name': row['Company Name'],
                        'email': row['Email'],
                        'target_role': row['Target Role'],
                        'company_focus': row['Company Focus'],
                        'my_skills': row['My Skills'],
                        'experience_years': row['Experience (Years)']
                    }
                    leads_to_save.append(lead_data)
                
                database.save_leads_batch(leads_to_save)
                st.session_state['csv_upload_saved'] = True
                log.info("Successfully saved %d leads from CSV", len(leads_to_save))
                
            except Exception as e:
                log.error("Failed to parse or save CSV '%s': %s", uploaded_file.name, e, exc_info=True)
                st.error(f"Error parsing CSV: {str(e)}")

        # Fetch latest mapped data for display
        mapped_df = st.session_state.get('csv_data', pd.DataFrame())
        
        if not mapped_df.empty:
            
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
                log.warning("Manual lead entry failed validation: missing/invalid %s", errors)
                st.error("Please complete the following required fields:\n- " + "\n- ".join(errors))
            else:
                log.info("Manual lead entry passed validation — saving '%s'", company_name)
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
                selection_mode="multi-row",
                key="db_lead_table"
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
                if st.button("🗑️ Delete Selected Leads", key="btn_delete_db"):
                    database.delete_leads(selected_ids)
                    st.success("Selected leads deleted successfully!")
                    st.rerun()
