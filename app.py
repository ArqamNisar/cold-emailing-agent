import streamlit as st
import pandas as pd
import json
import os
from dotenv import load_dotenv
load_dotenv()

import database
import gmail_service
from agents.analyzer_agent import run_analyzer
from agents.email_writer_agent import run_email_writer
from agents.compliance_agent import run_compliance_checker
from agents.subject_agent import run_subject_writer
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
    page_title="Cold Email Generator System",
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
    
    /* Card design system using Streamlit's native bordered container */
    div[data-testid="stVerticalBlockBorderDiv"] {
        background: rgba(30, 41, 59, 0.45) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        backdrop-filter: blur(12px) !important;
        margin-bottom: 1.5rem !important;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2) !important;
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
    <h1 class="main-title">Cold Email Generator</h1>
    <p class="subtitle">Streamline your cold outreach by importing and managing targeted leads</p>
</div>
""", unsafe_allow_html=True)


# Setup navigation tabs
tab_csv, tab_db, tab_dashboard, tab_settings = st.tabs([
    "📥 Upload Leads", 
    "🗂️ Leads",
    "📊 Dashboard",
    "⚙️ Gmail Integration"
])

def auto_map_columns(columns):
    """Fuzzy match CSV columns to expected database fields."""
    mapping = {}
    standard_fields = {
        'company_name': ['company name', 'company', 'name', 'firm', 'organization'],
        'email': ['email', 'email address', 'mail', 'contact', 'email_address'],
        'company_focus': ['focus', 'company focus', 'areas of focus', 'industry', 'domain', 'focus_areas', 'company_focus'],
        'our_value_proposition': ['our value proposition', 'value proposition', 'pitch', 'our pitch', 'our value', 'value_proposition', 'our_value_proposition', 'synergy', 'proposition', 'offering', 'offer']
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


def generate_mock_emails(company, company_focus, our_value_proposition, num_variations):
    """Fallback mock generator used when the LLM writer agent fails."""
    log.info("Generating %d MOCK emails | company='%s'", num_variations, company)
    variations = [
        {
            "subject": f"Partnership Opportunity: Connecting {company} & Our Team",
            "body": f"Hi team,\n\nI hope you're doing well.\n\nI've been following {company}'s work and was very impressed by your focus on {company_focus}. I believe there is a strong potential synergy between our organisations.\n\nSpecifically, we specialise in: {our_value_proposition}. I'd love to see if we could explore a strategic partnership or integration that benefits both of our user bases. Are you open to a brief chat next week?\n\nBest regards"
        },
        {
            "subject": f"Proposal: Collaboration regarding {company_focus}",
            "body": f"Hello,\n\nI am reaching out because I am very interested in exploring a collaboration opportunity with {company}.\n\nGiven our work in {our_value_proposition}, I believe we could add significant value to your offerings in {company_focus}.\n\nI would appreciate the opportunity to connect and learn more about your upcoming priorities. Please let me know if you have 10 minutes to sync.\n\nThanks"
        },
        {
            "subject": f"Synergy between our solutions for {company}",
            "body": f"Hi there,\n\nI'm writing to propose a potential partnership between our teams.\n\nSince your focus is on {company_focus} and we specialize in {our_value_proposition}, there seems to be a clear alignment that could drive mutual growth.\n\nWould you be open to a quick call to explore this?\n\nSincerely"
        }
    ]
    return variations[:num_variations]

def render_email_generation_ui(lead, key_prefix):
    company = lead.get('Company Name', lead.get('company_name', ''))
    company_focus = lead.get('Company Focus', lead.get('company_focus', ''))
    our_value_proposition = lead.get('Our Value Proposition', lead.get('our_value_proposition', ''))

    lead_id = f"{company}_{hash(company_focus)}"
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
        st.session_state[template_key] = ALL_TEMPLATES[0].id   # default: Pain -> Solution

    with st.container(border=True):
        st.markdown(f"### ✉️ Create Emails for **{company}**")
        st.write(f"Focusing on B2B sales/partnership outreach.")

        # ── Flow 1: Lead not yet analyzed ─────────────────────────────────────
        if analysis_key not in st.session_state:
            st.write("Analyse the lead's business focus to determine the best cold-email outreach strategy.")
            
            analyze_clicked = st.button(
                "🔍 Run Lead Analysis",
                type="primary",
                key=f"{key_prefix}_analyze_btn"
            )
            
            if analyze_clicked:
                log.info("Run Lead Analysis clicked | lead='%s'", lead_id)
                with st.spinner("🔍 Running lead analyzer..."):
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
                st.write("Not satisfied with the analysis? Run the agent again.")
                reanalyze_clicked = st.button(
                    "🔄 Re-analyse Lead",
                    type="secondary",
                    key=f"{key_prefix}_reanalyze_btn"
                )
                if reanalyze_clicked:
                    log.info("Re-analyse Lead clicked | lead='%s'", lead_id)
                    with st.spinner("🔄 Re-running lead analyzer…"):
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
                                card_html = (
                                    f'<div class="{card_class}">'
                                    f'{selected_badge}'
                                    f'<span class="tc-icon">{tmpl.icon}</span>'
                                    f'<div class="tc-name">{tmpl.name}</div>'
                                    f'<div class="tc-tagline">{tmpl.tagline}</div>'
                                    f'<div class="tc-meta">'
                                    f'<span class="tc-pill tc-pill-style">{tmpl.style}</span>'
                                    f'<span class="tc-pill tc-pill-tone">{tmpl.tone}</span>'
                                    f'<span class="tc-pill tc-pill-len">{tmpl.length} · {tmpl.word_range}</span>'
                                    f'</div>'
                                    f'<ul class="tc-use-cases">{use_cases_html}</ul>'
                                    f'<div class="tc-example">"{example_short}"</div>'
                                    f'</div>'
                                )
                                st.markdown(card_html, unsafe_allow_html=True)
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
                        emails = generate_mock_emails(company, company_focus, our_value_proposition, num_variations)

                    # Run compliance and subject line optimization analysis on all generated variations
                    with st.spinner("🛡️ Analyzing compliance and generating optimized subject options…"):
                        for email in emails:
                            # 1. Run compliance checker
                            try:
                                comp_res = run_compliance_checker(
                                    subject=email["subject"],
                                    body=email["body"],
                                    lead=lead
                                )
                                email["compliance"] = comp_res
                            except Exception as comp_err:
                                log.error("Compliance checker failed for email: %s", comp_err, exc_info=True)
                                email["compliance"] = {
                                    "is_compliant": True,
                                    "spam_keywords": [],
                                    "ftc_status": {"has_address": True, "has_unsubscribe": True, "issues": []},
                                    "claims_status": {"has_misleading_claims": False, "issues": []},
                                    "readability": {"sentence_length_ok": True, "complexity": "Medium", "score_desc": "Good", "issues": []},
                                    "engagement": {"has_questions": True, "personalization_ok": True, "suggestions": []},
                                    "enhanced_subject": email["subject"],
                                    "enhanced_body": email["body"],
                                    "error": str(comp_err)
                                }
                            
                            # 2. Run subject writer
                            try:
                                subj_options = run_subject_writer(
                                    lead=lead,
                                    analysis=st.session_state[analysis_key],
                                    email_body=email["body"]
                                )
                                email["subject_options"] = subj_options
                            except Exception as subj_err:
                                log.error("Subject writer failed for email: %s", subj_err, exc_info=True)
                                email["subject_options"] = [
                                    {"subject": email["subject"], "type": "Original Draft", "reason": "Original subject line fallback"}
                                ]

                            email["original_subject"] = email["subject"]
                            email["original_body"] = email["body"]
                            email["enhanced_applied"] = False

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

                        # Subject Optimizer UI
                        subject_options = email_data.get("subject_options")
                        if subject_options:
                            with st.expander("🎯 Subject Line Optimizer (Alternatives)", expanded=False):
                                st.markdown("<p style='font-size:0.82rem;color:#94a3b8;margin-bottom:0.75rem;'>These subject lines are written by the Subject Writer Agent. Click 'Use Subject' to apply one directly.</p>", unsafe_allow_html=True)
                                for idx, opt in enumerate(subject_options):
                                    opt_subj = opt.get("subject", "")
                                    opt_type = opt.get("type", "")
                                    opt_reason = opt.get("reason", "")
                                    
                                    # Active badge if currently selected
                                    is_active = (email_data["subject"] == opt_subj)
                                    
                                    col_opt1, col_opt2 = st.columns([4, 1])
                                    with col_opt1:
                                        badge_html = f'<span style="background:rgba(99, 102, 241, 0.15); color:#a5b4fc; padding: 0.15rem 0.5rem; border-radius: 9999px; font-size: 0.68rem; font-weight:600; margin-right: 0.5rem;">{opt_type}</span>'
                                        st.markdown(f"{badge_html} **\"{opt_subj}\"**", unsafe_allow_html=True)
                                        st.markdown(f"<p style='font-size:0.78rem; color:#94a3b8; margin-top:0.15rem; margin-left:0.25rem;'>💡 {opt_reason}</p>", unsafe_allow_html=True)
                                    with col_opt2:
                                        if is_active:
                                            st.markdown("<p style='color:#10b981; font-weight:bold; font-size:0.85rem; text-align:right; margin-top:0.4rem;'>✓ Active</p>", unsafe_allow_html=True)
                                        else:
                                            if st.button("Use Subject", key=f"{key_prefix}_use_subj_{i}_{idx}", use_container_width=True, type="secondary"):
                                                email_data["subject"] = opt_subj
                                                st.session_state[session_key] = emails
                                                st.success(f"Subject updated to: \"{opt_subj}\"")
                                                st.rerun()
                                    if idx < len(subject_options) - 1:
                                        st.markdown("<hr style='margin:0.5rem 0; border:0; border-top:1px solid rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
                        email_html = (
                            f'<div style="'
                            f'background: rgba(30, 41, 59, 0.45);'
                            f'border: 1px solid rgba(255, 255, 255, 0.07);'
                            f'border-radius: 8px;'
                            f'padding: 1.2rem;'
                            f'color: #e2e8f0;'
                            f'font-family: \'Inter\', sans-serif;'
                            f'white-space: pre-wrap;'
                            f'line-height: 1.6;'
                            f'font-size: 0.92rem;'
                            f'margin-top: 0.5rem;'
                            f'">{email_data["body"]}</div>'
                        )
                        st.markdown(email_html, unsafe_allow_html=True)

                        # Compliance analysis visualization
                        comp = email_data.get("compliance")
                        if comp:
                            st.write("")
                            with st.container(border=True):
                                # Header section with status and actions
                                status_col, action_col = st.columns([3, 2])
                                is_ok = comp.get("is_compliant", True)
                                
                                with status_col:
                                    if is_ok:
                                        st.markdown("#### 🛡️ Compliance & Quality Check: <span style='color:#10b981;'>🟢 Fully Compliant & Optimized</span>", unsafe_allow_html=True)
                                    else:
                                        st.markdown("#### 🛡️ Compliance & Quality Check: <span style='color:#fbbf24;'>🟡 Quality/Compliance Enhancements Available</span>", unsafe_allow_html=True)
                                
                                with action_col:
                                    applied = email_data.get("enhanced_applied", False)
                                    if not applied:
                                        if st.button("✨ Apply Enhancements", key=f"{key_prefix}_apply_enh_{i}", type="primary", use_container_width=True):
                                            email_data["subject"] = comp.get("enhanced_subject", email_data["subject"])
                                            email_data["body"] = comp.get("enhanced_body", email_data["body"])
                                            email_data["enhanced_applied"] = True
                                            st.session_state[session_key] = emails
                                            st.success("Enhancements applied!")
                                            st.rerun()
                                    else:
                                        if st.button("🔄 Revert to Original Draft", key=f"{key_prefix}_revert_{i}", type="secondary", use_container_width=True):
                                            email_data["subject"] = email_data.get("original_subject", email_data["subject"])
                                            email_data["body"] = email_data.get("original_body", email_data["body"])
                                            email_data["enhanced_applied"] = False
                                            st.session_state[session_key] = emails
                                            st.success("Reverted to original!")
                                            st.rerun()
                                            
                                if applied:
                                    st.markdown("<p style='font-size:0.85rem;color:#10b981;font-weight:600;margin-top:-0.5rem;'>✨ Applied compliance enhancements to this draft (spam words replaced, FTC footer added, readability improved).</p>", unsafe_allow_html=True)

                                # Create sub-tabs for evaluation categories
                                comp_tabs = st.tabs([
                                    "🚨 Spam Keywords", 
                                    "⚖️ FTC CAN-SPAM", 
                                    "📝 Readability & Claims", 
                                    "🎯 Engagement"
                                ])

                                # 1. Spam Keywords
                                with comp_tabs[0]:
                                    spam_words = comp.get("spam_keywords", [])
                                    if not spam_words:
                                        st.success("✅ No typical spam trigger keywords detected. Great job!")
                                    else:
                                        st.warning(f"⚠️ Flagged {len(spam_words)} potential spam filter trigger keyword(s):")
                                        table_rows = ""
                                        for sw in spam_words:
                                            word = sw.get("keyword", "")
                                            alt = sw.get("alternative", "")
                                            reason = sw.get("reason", "")
                                            table_rows += (
                                                f'<tr>'
                                                f'<td style="padding: 8px; border-bottom: 1px solid rgba(255,255,255,0.07); color: #ef4444; font-weight: bold;">{word}</td>'
                                                f'<td style="padding: 8px; border-bottom: 1px solid rgba(255,255,255,0.07); color: #10b981; font-weight: bold;">{alt}</td>'
                                                f'<td style="padding: 8px; border-bottom: 1px solid rgba(255,255,255,0.07); color: #94a3b8;">{reason}</td>'
                                                f'</tr>'
                                            )
                                        
                                        table_html = (
                                            f'<table style="width:100%; border-collapse: collapse; margin-top: 10px; font-size: 0.85rem; background: rgba(30, 41, 59, 0.25);">'
                                            f'<thead>'
                                            f'<tr style="border-bottom: 2px solid rgba(255,255,255,0.1); text-align: left;">'
                                            f'<th style="padding: 8px; color: #e2e8f0;">Flagged Keyword</th>'
                                            f'<th style="padding: 8px; color: #e2e8f0;">Recommended Alternative</th>'
                                            f'<th style="padding: 8px; color: #e2e8f0;">Reason</th>'
                                            f'</tr>'
                                            f'</thead>'
                                            f'<tbody>{table_rows}</tbody>'
                                            f'</table>'
                                        )
                                        st.markdown(table_html, unsafe_allow_html=True)

                                # 2. FTC CAN-SPAM Rules
                                with comp_tabs[1]:
                                    ftc = comp.get("ftc_status", {})
                                    has_addr = ftc.get("has_address", True)
                                    has_unsub = ftc.get("has_unsubscribe", True)
                                    ftc_issues = ftc.get("issues", [])

                                    col_ftc1, col_ftc2 = st.columns(2)
                                    with col_ftc1:
                                        if has_addr:
                                            st.markdown("📍 **Physical Address Notice:** <span style='color:#10b981;'>✅ Present</span>", unsafe_allow_html=True)
                                        else:
                                            st.markdown("📍 **Physical Address Notice:** <span style='color:#ef4444;'>❌ Missing Location Info</span>", unsafe_allow_html=True)
                                    with col_ftc2:
                                        if has_unsub:
                                            st.markdown("✉️ **Opt-out Mechanism:** <span style='color:#10b981;'>✅ Present</span>", unsafe_allow_html=True)
                                        else:
                                            st.markdown("✉️ **Opt-out Mechanism:** <span style='color:#ef4444;'>❌ Missing Unsubscribe Option</span>", unsafe_allow_html=True)
                                    
                                    if ftc_issues:
                                        st.markdown("<p style='font-size:0.85rem;color:#ef4444;margin-top:0.5rem;'><b>Issues Found:</b></p>", unsafe_allow_html=True)
                                        for issue in ftc_issues:
                                            st.markdown(f"- {issue}")
                                    else:
                                        st.success("✅ This draft complies with key FTC CAN-SPAM requirements (offers an opt-out choice and physical location identifier).")

                                # 3. Readability & Claims
                                with comp_tabs[2]:
                                    read = comp.get("readability", {})
                                    claims = comp.get("claims_status", {})
                                    
                                    st.markdown(f"📊 **Sentence Length & Style:** {read.get('score_desc', '')}")
                                    st.markdown(f"🏷️ **Complexity Level:** `{read.get('complexity', 'Medium')}`")
                                    
                                    read_issues = read.get("issues", [])
                                    if read_issues:
                                        for ri in read_issues:
                                            st.markdown(f"- 📝 {ri}")
                                            
                                    has_claims = claims.get("has_misleading_claims", False)
                                    claims_issues = claims.get("issues", [])
                                    
                                    if has_claims:
                                        st.warning("⚠️ **Misleading or Exaggerated Claims detected:**")
                                        for ci in claims_issues:
                                            st.markdown(f"- 🔍 {ci}")
                                    else:
                                        st.success("✅ No misleading promises or exaggerated return-on-investment guarantees found.")

                                # 4. Engagement
                                with comp_tabs[3]:
                                    eng = comp.get("engagement", {})
                                    has_q = eng.get("has_questions", True)
                                    p_ok = eng.get("personalization_ok", True)
                                    suggestions = eng.get("suggestions", [])
                                    
                                    st.markdown(f"❓ **Call-To-Action / Engagement Question:** {'✅ Present' if has_q else '❌ Missing clear next-step question'}")
                                    st.markdown(f"👤 **Lead Personalization:** {'✅ Tailored to prospect focus & value prop' if p_ok else '❌ Low personalization context'}")
                                    
                                    if suggestions:
                                        st.markdown("<p style='font-size:0.85rem;color:#94a3b8;margin-top:0.5rem;'><b>Engagement Suggestions:</b></p>", unsafe_allow_html=True)
                                        for sug in suggestions:
                                            st.markdown(f"- 🎯 {sug}")

                        # ── Edit and Send via Gmail UI ─────────────────────────
                        st.write("")
                        with st.container(border=True):
                            st.markdown("#### 📧 Edit & Send via Gmail")
                            
                            # Retrieve lead email address from lead object
                            lead_email = lead.get("Email", lead.get("email", lead.get("Email Address", "")))
                            if hasattr(lead_email, "iloc"):
                                lead_email = lead_email.iloc[0] if not lead_email.empty else ""
                            lead_email = str(lead_email).strip()
                            
                            # Recipient Address Input
                            edit_recipient = st.text_input(
                                "Recipient Email Address",
                                value=lead_email,
                                key=f"{key_prefix}_send_to_{i}"
                            )
                            
                            # Subject Line Input
                            edit_subject = st.text_input(
                                "Subject Line",
                                value=email_data["subject"],
                                key=f"{key_prefix}_send_subj_{i}"
                            )
                            
                            # Email Body Text Area
                            edit_body = st.text_area(
                                "Email Body",
                                value=email_data["body"],
                                height=280,
                                key=f"{key_prefix}_send_body_{i}"
                            )
                            
                            # Check Gmail authorization status
                            is_gmail_connected = False
                            try:
                                is_gmail_connected = gmail_service.is_authenticated()
                            except Exception:
                                pass
                                
                            if not is_gmail_connected:
                                st.warning("⚠️ Gmail is not connected. Please go to the **⚙️ Gmail Integration** tab to authorize your account.")
                                st.button("🚀 Send Email", key=f"{key_prefix}_send_btn_{i}", disabled=True, use_container_width=True)
                            else:
                                if st.button("🚀 Send Email via Gmail", key=f"{key_prefix}_send_btn_{i}", type="primary", use_container_width=True):
                                    if not edit_recipient:
                                        st.error("Error: Recipient email address is required.")
                                    elif not edit_subject:
                                        st.error("Error: Subject line is required.")
                                    elif not edit_body:
                                        st.error("Error: Email body is required.")
                                    else:
                                        with st.spinner("Sending email..."):
                                            try:
                                                sent_msg = gmail_service.send_email(
                                                    to_email=edit_recipient,
                                                    subject=edit_subject,
                                                    body_text=edit_body
                                                )
                                                msg_id = sent_msg.get('id', 'Unknown')
                                                thread_id = sent_msg.get('threadId', 'Unknown')
                                                
                                                # Look up lead ID and log the sent email
                                                lead_id = database.get_lead_id_by_email(edit_recipient)
                                                database.save_sent_email(
                                                    lead_id=lead_id,
                                                    recipient_email=edit_recipient,
                                                    subject=edit_subject,
                                                    body=edit_body,
                                                    message_id=msg_id,
                                                    thread_id=thread_id
                                                )
                                                
                                                st.success(f"🎉 Email sent successfully to **{edit_recipient}**!")
                                            except Exception as send_err:
                                                st.error(f"❌ Failed to send email: {send_err}")

# --- TAB 1: CSV IMPORT & PARSE ---
with tab_csv:
    st.markdown("### 📥 Import Leads from CSV")
    st.write("Upload a CSV file — all leads will be automatically saved to the database. Select any lead from the table to generate email variations.")
    
    # Sample CSV Template Guide
    with st.expander("💡 View & Download Sample CSV Template", expanded=False):
        st.write("Your CSV file should have headers matching or similar to the example below. The importer will attempt to automatically map your columns:")
        try:
            sample_df = pd.read_csv("sample_leads.csv")
            st.dataframe(sample_df, hide_index=True, use_container_width=True)
            with open("sample_leads.csv", "rb") as f:
                sample_bytes = f.read()
        except Exception as e:
            # Fallback inline data
            sample_df = pd.DataFrame({
                "Company": ["Acme Corp", "CloudFlow"],
                "Email": ["partnerships@acme.com", "sales@cloudflow.io"],
                "Focus Areas": ["Supply chain logistics SaaS", "Cloud infrastructure monitoring"],
                "Our Value Proposition": ["AI-powered route optimization API", "Multi-cloud automated cost optimization tools"]
            })
            st.dataframe(sample_df, hide_index=True, use_container_width=True)
            sample_bytes = sample_df.to_csv(index=False).encode('utf-8')
            
        st.download_button(
            label="📥 Download Sample CSV Template",
            data=sample_bytes,
            file_name="sample_leads.csv",
            mime="text/csv",
            key="download_sample_csv"
        )
        
    st.write("")
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
                focus_col = mapping.get('company_focus', df.columns[0])
                val_prop_col = mapping.get('our_value_proposition', df.columns[0])
                
                mapped_df = pd.DataFrame()
                mapped_df['Company Name'] = df[company_col].astype(str)
                mapped_df['Email'] = df[email_col].astype(str)
                mapped_df['Company Focus'] = df[focus_col].astype(str)
                mapped_df['Our Value Proposition'] = df[val_prop_col].astype(str)
                
                st.session_state['csv_data'] = mapped_df
                
                st.success(f"Successfully loaded {len(df)} rows from {uploaded_file.name}")
                
                # Save immediately to DB
                leads_to_save = []
                for _, row in mapped_df.iterrows():
                    lead_data = {
                        'company_name': row['Company Name'],
                        'email': row['Email'],
                        'company_focus': row['Company Focus'],
                        'our_value_proposition': row['Our Value Proposition']
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
                    lead_options = [f"{mapped_df.iloc[idx]['Company Name']} ({mapped_df.iloc[idx]['Company Focus']})" for idx in selected_rows]
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

# --- TAB 2: LEADS DATABASE EXPLORER ---
with tab_db:
    st.markdown("### 🗂️ Leads Database Explorer")
    st.write("Browse, search, and delete leads stored in your local SQLite database.")
    
    # Reload leads
    leads = database.get_all_leads()
    
    if not leads:
        st.info("The database is currently empty. Go ahead and upload some leads using CSV Import.")
    else:
        db_df = pd.DataFrame(leads)
        
        # Format columns for display
        db_df_display = db_df.copy()
        # Reorder columns for a nicer view
        cols_display = [
            'id', 'company_name', 'email', 
            'company_focus', 'our_value_proposition', 'created_at'
        ]
        db_df_display = db_df_display[cols_display]
        db_df_display.columns = [
            'ID', 'Company Name', 'Email Address', 
            'Company Focus', 'Our Value Proposition', 'Created At'
        ]
        
        # Search & Filter
        search_query = st.text_input("🔍 Search Leads", placeholder="Search by Company, Email, Focus, or Value Prop...")
        if search_query.strip():
            q = search_query.lower().strip()
            db_df_display = db_df_display[
                db_df_display['Company Name'].str.lower().str.contains(q) |
                db_df_display['Email Address'].str.lower().str.contains(q) |
                db_df_display['Company Focus'].str.lower().str.contains(q) |
                db_df_display['Our Value Proposition'].str.lower().str.contains(q)
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
                # ── Delete options right below the table ────────────────────
                selected_ids = [int(db_df.iloc[idx]['id']) for idx in selected_db_rows]
                st.markdown("---")
                col_del, _ = st.columns([1, 3])
                with col_del:
                    if st.button("🗑️ Delete Selected Leads", key="btn_delete_db", use_container_width=True):
                        database.delete_leads(selected_ids)
                        st.success("Selected leads deleted successfully!")
                        st.rerun()
                
                # If multiple are selected, show dropdown to choose one
                if len(selected_db_rows) > 1:
                    lead_options = [f"{db_df_display.iloc[idx]['Company Name']} ({db_df_display.iloc[idx]['Company Focus']})" for idx in selected_db_rows]
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

# --- TAB 3: ANALYTICS DASHBOARD ---
with tab_dashboard:
    st.markdown("### 📊 Cold Outreach Dashboard")
    st.write("Track sent emails, sync replies dynamically from Gmail, and monitor response rates.")

    # 1. Fetch leads & sent emails
    leads = database.get_all_leads()
    sent_emails = database.get_sent_emails()

    # Calculate metrics
    total_leads = len(leads)
    total_sent = len(sent_emails)
    
    # Calculate total replies (sum of reply_count for each sent email)
    total_replies = sum(item.get('reply_count', 0) for item in sent_emails)
    
    # Reply rate percentage
    reply_rate = (total_replies / total_sent * 100) if total_sent > 0 else 0.0

    # 2. Render Metrics Cards
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("🗂️ Total Leads", f"{total_leads}")
    with col_m2:
        st.metric("📨 Emails Sent", f"{total_sent}")
    with col_m3:
        st.metric("💬 Total Replies", f"{total_replies}")
    with col_m4:
        st.metric("📈 Response Rate", f"{reply_rate:.1f}%")

    # 3. Synchronize Replies Logic
    st.markdown("---")
    col_sync_btn, col_sync_msg = st.columns([1, 2])
    with col_sync_btn:
        # Check Gmail connection status
        is_gmail_connected = False
        try:
            is_gmail_connected = gmail_service.is_authenticated()
        except Exception:
            pass

        sync_btn_clicked = st.button(
            "🔄 Sync Replies from Gmail",
            key="sync_replies_btn",
            type="primary",
            disabled=not is_gmail_connected,
            use_container_width=True
        )
    with col_sync_msg:
        if not is_gmail_connected:
            st.warning("⚠️ Connect your Gmail account in the **⚙️ Gmail Integration** tab to enable reply synchronization.")
        else:
            st.info("ℹ️ Click the button to scan Gmail threads for new replies from your leads.")

    if is_gmail_connected and sync_btn_clicked:
        if not sent_emails:
            st.info("No sent emails to sync replies for.")
        else:
            with st.spinner("🔄 Checking Gmail threads for replies..."):
                synced_count = 0
                new_replies_total = 0
                for email_log in sent_emails:
                    thread_id = email_log.get('thread_id')
                    recipient = email_log.get('recipient_email')
                    log_id = email_log.get('id')
                    
                    if thread_id and thread_id != 'Unknown':
                        # Call Gmail API to fetch number of replies in this thread
                        current_replies = gmail_service.check_thread_replies(thread_id, recipient)
                        
                        # Update DB if different
                        old_replies = email_log.get('reply_count', 0)
                        if current_replies != old_replies:
                            database.update_reply_count(log_id, current_replies)
                            new_replies_total += (current_replies - old_replies)
                            synced_count += 1
                
                # Reload sent emails after update
                sent_emails = database.get_sent_emails()
                total_replies = sum(item.get('reply_count', 0) for item in sent_emails)
                reply_rate = (total_replies / len(sent_emails) * 100) if len(sent_emails) > 0 else 0.0
                
                st.success(f"✅ Sync complete! Checked {len(sent_emails)} threads. Updated {synced_count} log(s) with {new_replies_total} new reply/replies.")
                st.rerun()

    # 4. Sent Emails Log
    st.markdown("---")
    st.markdown("### 📋 Sent Emails History")
    if not sent_emails:
        st.info("No emails have been sent yet. Generate and send variation drafts from the Leads tab to begin.")
    else:
        # Create a dataframe for nice tabular display
        history_data = []
        for idx, email_log in enumerate(sent_emails):
            lead_company = email_log.get('lead_company_name') or "Unknown Lead"
            recipient = email_log.get('recipient_email', '')
            subject = email_log.get('subject', '')
            reply_cnt = email_log.get('reply_count', 0)
            sent_time = email_log.get('sent_at', '')
            status = f"✅ Replied ({reply_cnt})" if reply_cnt > 0 else "✉️ Sent (No reply)"
            
            history_data.append({
                "Company": lead_company,
                "Recipient Email": recipient,
                "Subject": subject,
                "Status": status,
                "Sent Time": sent_time
            })
            
        history_df = pd.DataFrame(history_data)
        
        # Display logs in Streamlit
        st.dataframe(history_df, use_container_width=True, hide_index=True)
        
        # Expanders to view content
        st.markdown("#### 🔍 View Email Content")
        for idx, email_log in enumerate(sent_emails):
            lead_company = email_log.get('lead_company_name') or "Unknown Lead"
            recipient = email_log.get('recipient_email', '')
            subject = email_log.get('subject', '')
            body = email_log.get('body', '')
            reply_cnt = email_log.get('reply_count', 0)
            status_text = f"✅ Replied ({reply_cnt})" if reply_cnt > 0 else "No reply yet"
            
            with st.expander(f"📄 To: {recipient} ({lead_company}) — {subject} | Status: {status_text}", expanded=False):
                st.markdown(f"**Subject:** {subject}")
                st.markdown(f"**Sent:** {email_log.get('sent_at', '')}")
                email_body_box = (
                    f'<div style="'
                    f'background: rgba(30, 41, 59, 0.45);'
                    f'border: 1px solid rgba(255, 255, 255, 0.07);'
                    f'border-radius: 8px;'
                    f'padding: 1.2rem;'
                    f'color: #e2e8f0;'
                    f'font-family: \'Inter\', sans-serif;'
                    f'white-space: pre-wrap;'
                    f'line-height: 1.6;'
                    f'font-size: 0.92rem;'
                    f'margin-top: 0.5rem;'
                    f'">{body}</div>'
                )
                st.markdown(email_body_box, unsafe_allow_html=True)

# --- TAB 4: GMAIL SETTINGS ---
with tab_settings:
    st.markdown("### ⚙️ Gmail API Integration")
    st.write("Connect your Gmail account to send generated email variations directly to your leads.")

    # Check connection status
    try:
        is_conn = gmail_service.is_authenticated()
    except Exception as e:
        is_conn = False
        st.error(f"Error checking Gmail status: {e}")

    if is_conn:
        email_addr = gmail_service.get_profile_email()
        if email_addr:
            st.success(f"🟢 Gmail Account Connected: **{email_addr}**")
        else:
            st.success("🟢 Gmail Account Connected")
            
        if st.button("🔴 Disconnect Gmail Account", key="disconnect_gmail", type="secondary"):
            try:
                gmail_service.disconnect()
                st.success("Disconnected Gmail account successfully.")
                st.rerun()
            except Exception as disconnect_err:
                st.error(f"Failed to disconnect: {disconnect_err}")
    else:
        st.warning("🔴 Gmail Account Disconnected")
        st.markdown("---")
        st.markdown("#### Setup Instructions")
        st.markdown("""
        To send emails via Gmail, you need Google OAuth Client credentials:
        1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
        2. Create a new project or select an existing one.
        3. Enable the **Gmail API** (search for "Gmail API" and click Enable).
        4. Configure the **OAuth consent screen** (choose User Type: **External**, enter app name/email, and add scope `https://www.googleapis.com/auth/gmail.send`). Add your email under Test Users.
        5. Go to **Credentials** -> **Create Credentials** -> **OAuth client ID**. Select Application type: **Desktop app**, name it, and click Create.
        6. Download the JSON credentials file, rename it to `credentials.json`, and upload it below.
        """)

        # File uploader for credentials.json
        uploaded_creds = st.file_uploader("Upload credentials.json file", type=["json"], key="creds_uploader")
        if uploaded_creds is not None:
            try:
                creds_data = json.load(uploaded_creds)
                # Verify that it is a valid Google OAuth Client secrets file
                if 'installed' in creds_data:
                    # Check if file on disk already exists and is identical
                    already_saved = False
                    if os.path.exists('.credentials.json'):
                        try:
                            with open('.credentials.json', 'r') as f:
                                existing_data = json.load(f)
                            if existing_data == creds_data:
                                already_saved = True
                        except Exception:
                            pass
                    
                    if not already_saved:
                        with open('.credentials.json', 'w') as f:
                            json.dump(creds_data, f)
                        st.success("credentials.json uploaded and saved successfully!")
                        st.rerun()
                elif 'web' in creds_data:
                    st.error("⚠️ You uploaded a Web Application credentials file. Google OAuth requires **Desktop Application** credentials for local desktop scripts to avoid 'redirect_uri_mismatch' errors. Please follow step 5 of the instructions above to create a Desktop app credential.")
                else:
                    st.error("Invalid credentials file format. Please upload a valid client secrets JSON file.")
            except Exception as e:
                st.error(f"Error reading credentials file: {e}")

        # If .credentials.json exists, show authorization button
        if os.path.exists('.credentials.json'):
            # Detect type
            is_desktop_creds = False
            try:
                with open('.credentials.json', 'r') as f:
                    c_data = json.load(f)
                    is_desktop_creds = 'installed' in c_data
            except Exception:
                pass

            if not is_desktop_creds:
                st.error("⚠️ The saved `.credentials.json` is a **Web Application** credential, which causes `redirect_uri_mismatch` errors on sign in. Please overwrite it by uploading a **Desktop Application** credential (follow step 5 above).")
            
            st.info("ℹ️ `.credentials.json` is present. Click the button below to authorize the application.")
            if st.button("🔗 Connect Gmail Account", key="connect_gmail", type="primary", disabled=not is_desktop_creds):
                with st.spinner("Opening browser for authorization..."):
                    try:
                        gmail_service.authenticate()
                        st.success("Gmail account authorized successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Authentication failed: {e}")
        else:
            st.info("ℹ️ Please upload credentials.json to enable the connection button.")
            

