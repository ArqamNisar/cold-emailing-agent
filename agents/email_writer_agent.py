"""
Email Writer Agent — LangGraph pipeline
=========================================
Graph:  START → email_writer → END

Receives the fully-analyzed lead state + the user's chosen template and
generates N cold-email variations that honour both the template's structural
approach and the strategy from the analyzer (tone, length, key hooks).

Output shape (list of dicts):
    [{"subject": "...", "body": "..."}, ...]
"""

import json
import os
import re
from typing import List, Optional

from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from agents.email_templates import EmailTemplate, get_template
from logger import get_logger

log = get_logger(__name__)


# ---------------------------------------------------------------------------
# State schema
# ---------------------------------------------------------------------------

class EmailWriterState(TypedDict):
    # ── Inputs ──────────────────────────────────────────────────────────────
    company_name: str
    company_focus: str
    our_value_proposition: str
    email: str                     # recipient email (for personalisation hints)

    # ── From analyzer ───────────────────────────────────────────────────────
    company_industry: str
    value_proposition: str
    target_audience: str
    email_goal: str
    tone: str
    email_length: str
    word_range: str
    key_hooks: list

    # ── Template ─────────────────────────────────────────────────────────────
    template_id: str
    num_variations: int

    # ── Output ───────────────────────────────────────────────────────────────
    emails: list                   # list[dict] — [{"subject":…,"body":…}, …]

    # ── Meta ─────────────────────────────────────────────────────────────────
    error: Optional[str]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_llm() -> ChatGoogleGenerativeAI:
    key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY", "")
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=key,
        temperature=0.8,   # higher for creative variation
    )


def _parse_email_list(text: str) -> List[dict]:
    """
    Extract a JSON array of email objects from the LLM response.
    Handles markdown fences and leading prose.
    """
    clean = text.strip()

    # Strip markdown fences
    if "```" in clean:
        parts = clean.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("["):
                clean = part
                break

    # Find outermost array brackets
    start = clean.find("[")
    end = clean.rfind("]")
    if start != -1 and end != -1:
        clean = clean[start: end + 1]

    parsed = json.loads(clean)

    # Validate shape
    result = []
    for item in parsed:
        if isinstance(item, dict) and "subject" in item and "body" in item:
            result.append({"subject": str(item["subject"]), "body": str(item["body"])})

    return result


# ---------------------------------------------------------------------------
# Node — Email Writer
# ---------------------------------------------------------------------------

def email_writer_node(state: EmailWriterState) -> dict:
    """
    Core LLM node: generates N cold-email variations.
    """
    template: EmailTemplate = get_template(state["template_id"])
    n = state["num_variations"]

    log.info(
        "[email_writer] START | company='%s' template='%s' variations=%d",
        state["company_name"], template.id, n,
    )

    # Template-level config (take precedence over analyzer defaults)
    eff_tone       = template.tone
    eff_length     = template.length
    eff_word_range = template.word_range

    # Build hooks as a bullet list for the prompt
    hooks = state.get("key_hooks", [])
    hooks_text = "\n".join(f"  - {h}" for h in hooks) if hooks else "  - (none provided)"

    # Build use-cases context
    use_cases_text = "\n".join(f"  • {uc}" for uc in template.use_cases)

    system_prompt = (
        "You are an elite cold-email copywriter specialising in high-converting, "
        "personalised outreach emails.\n\n"
        f"=== TEMPLATE CATEGORY : {template.category} ===\n"
        f"Template Name : {template.name} ({template.style})\n"
        f"Goal          : {template.tagline}\n\n"
        f"When to use this template:\n{use_cases_text}\n\n"
        f"--- Body Structure ---\n"
        f"{template.body_template}\n\n"
        f"--- Detailed Writing Rules ---\n"
        f"{template.structure_hint}\n\n"
        "--- Global Writing Constraints ---\n"
        f"  • Tone       : {eff_tone}\n"
        f"  • Length     : {eff_length} ({eff_word_range})\n"
        "  • Elaborate and develop details fully so that the length matches the target range. Do not write single-sentence placeholder paragraphs; ensure every hook and partnership value is fully written out and natural.\n"
        "  • Every variation MUST have a UNIQUE subject line and a noticeably different opening sentence.\n"
        "  • Personalise deeply: weave in the company's name, industry, focus, and value proposition.\n"
        "  • The sender is a representative of the company pitching partnerships or closing deals (writing on behalf of their team/firm).\n"
        "  • Do NOT include placeholder text like [Your Name] or [Link] — write naturally.\n"
        "  • Do NOT include any prose outside the JSON array in your response.\n\n"
        "Return ONLY a valid JSON array with this exact schema:\n"
        '[\n  {"subject": "...", "body": "..."},\n  ...\n]'
    )

    human_prompt = (
        f"Generate {n} cold-email variation(s) following the template structure above.\n\n"
        "--- Our Value Proposition ---\n"
        f"  Offer/Services: {state['our_value_proposition']}\n\n"
        "--- Target Company ---\n"
        f"  Company     : {state['company_name']}\n"
        f"  Industry    : {state.get('company_industry', '')}\n"
        f"  Value Prop  : {state.get('value_proposition', '')}\n"
        f"  Focus       : {state['company_focus']}\n"
        f"  Audience    : {state.get('target_audience', '')}\n"
        f"  Email Goal  : {state.get('email_goal', '')}\n\n"
        f"--- Key Hooks to Weave In (from lead analysis) ---\n"
        f"{hooks_text}\n\n"
        f"Return exactly {n} email object(s) in the JSON array. Nothing else."
    )

    try:
        log.debug("[email_writer] Invoking Gemini LLM")
        llm = _get_llm()
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt),
        ])
        log.debug("[email_writer] Raw LLM response (first 500 chars): %s", response.content[:500])
        emails = _parse_email_list(response.content)

        if not emails:
            raise ValueError("LLM returned an empty or malformed email list.")

        log.info("[email_writer] DONE | generated %d email(s)", len(emails))
        return {"emails": emails, "error": None}

    except Exception as exc:
        log.error("[email_writer] FAILED: %s", exc, exc_info=True)
        return {"emails": [], "error": str(exc)}


# ---------------------------------------------------------------------------
# Graph assembly
# ---------------------------------------------------------------------------

def build_writer_graph():
    """Compile and return the LangGraph email writer pipeline."""
    workflow = StateGraph(EmailWriterState)
    workflow.add_node("email_writer", email_writer_node)
    workflow.add_edge(START, "email_writer")
    workflow.add_edge("email_writer", END)
    return workflow.compile()


_graph = None


def run_email_writer(
    lead: dict,
    analysis: dict,
    template: EmailTemplate,
    num_variations: int = 3,
) -> List[dict]:
    """
    Entry point called from the Streamlit app.

    Parameters
    ----------
    lead         : Raw lead dict (display-name or snake_case keys accepted).
    analysis     : Output of run_analyzer() — LeadAnalysisState dict.
    template     : EmailTemplate dataclass instance (from email_templates.py).
    num_variations: How many email variations to generate (1–5).

    Returns
    -------
    List of {"subject": str, "body": str} dicts.
    Raises RuntimeError on complete failure (caller should fall back to mock).
    """
    global _graph
    if _graph is None:
        log.info("Compiling LangGraph email writer pipeline")
        _graph = build_writer_graph()
        log.info("LangGraph writer pipeline compiled successfully")

    def _get(d, *keys):
        for k in keys:
            if k in d:
                return d[k]
        return ""

    initial_state: EmailWriterState = {
        # Lead fields
        "company_name": str(_get(lead, "Company Name", "company_name")),
        "company_focus":str(_get(lead, "Company Focus","company_focus")),
        "our_value_proposition": str(_get(lead, "Our Value Proposition", "our_value_proposition")),
        "email":        str(_get(lead, "Email", "email", "Email Address") or ""),

        # Analysis fields (from analyzer agent)
        "company_industry":  str(analysis.get("company_industry", "")),
        "value_proposition": str(analysis.get("value_proposition", "")),
        "target_audience":   str(analysis.get("target_audience", "")),
        "email_goal":        str(analysis.get("email_goal", "")),
        # Tone/length/word_range: template values take precedence over analyzer
        "tone":              template.tone,
        "email_length":      template.length,
        "word_range":        template.word_range,
        "key_hooks":         list(analysis.get("key_hooks", [])),

        # Template + config
        "template_id":    template.id,
        "num_variations": max(1, min(5, num_variations)),

        # Output placeholders
        "emails": [],
        "error": None,
    }

    log.info(
        "Invoking email writer graph | company='%s' template='%s' variations=%d",
        initial_state["company_name"], template.id, num_variations,
    )

    result = _graph.invoke(initial_state)

    if result.get("error"):
        log.warning("Email writer completed with error: %s", result["error"])
        if not result.get("emails"):
            raise RuntimeError(result["error"])

    return result.get("emails", [])
