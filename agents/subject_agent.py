"""
Subject Line Writer Agent — LangGraph pipeline
===============================================
Graph: START → subject_writer → END

Generates three highly efficient subject lines for an email variation:
1. Personalized (references company/industry context directly)
2. Benefit-driven (focuses on our value proposition/utility)
3. Curiosity / Hook (intriguing, low-friction, conversational)
"""

import json
import os
from typing import Optional, List, Dict
from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from logger import get_logger

log = get_logger(__name__)


# ---------------------------------------------------------------------------
# State schema
# ---------------------------------------------------------------------------

class SubjectState(TypedDict):
    # ── Inputs ──────────────────────────────────────────────────────────────
    lead_company_name: str
    lead_company_focus: str
    lead_our_value_proposition: str
    email_body: str
    tone: str
    email_goal: str
    key_hooks: List[str]

    # ── Outputs ─────────────────────────────────────────────────────────────
    subject_options: List[Dict[str, str]]  # list of {"subject": "...", "type": "...", "reason": "..."}

    # ── Meta ────────────────────────────────────────────────────────────────
    error: Optional[str]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_llm() -> ChatGoogleGenerativeAI:
    """Return a Gemini 2.5 Flash chat model, sourcing the key from environment."""
    key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY", "")
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=key,
        temperature=0.7,  # slightly higher temperature for creative variations
    )


def _parse_json_block(text: str) -> dict:
    """
    Extract the first JSON object from a model response that may be wrapped
    in markdown fences or contain extra prose.
    """
    clean = text.strip()
    if "```" in clean:
        parts = clean.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{"):
                clean = part
                break

    # Find outermost braces
    start = clean.find("{")
    end = clean.rfind("}")
    if start != -1 and end != -1:
        clean = clean[start : end + 1]

    return json.loads(clean)


# ---------------------------------------------------------------------------
# Node – Subject Line Writer
# ---------------------------------------------------------------------------

def subject_writer_node(state: SubjectState) -> dict:
    """
    Generates three optimized subject lines.
    """
    log.info("[subject_writer] START | lead='%s'", state['lead_company_name'])

    system_prompt = (
        "You are an elite B2B email copywriter specializing in high-open-rate cold email subject lines.\n"
        "Your task is to write exactly 3 distinct, high-converting subject line options for a cold outreach email.\n"
        "You must return a valid JSON object ONLY. Do NOT include any markdown formatting, "
        "comments, or prose outside the JSON block."
    )

    hooks_text = "\n".join(f"  - {h}" for h in state["key_hooks"]) if state["key_hooks"] else "  - (none)"

    human_prompt = f"""Analyze the lead information and email body, then write exactly 3 optimized subject line options.

--- LEAD & STRATEGY CONTEXT ---
Target Company: {state["lead_company_name"]}
Company Focus: {state["lead_company_focus"]}
Our Value Proposition: {state["lead_our_value_proposition"]}
Email Goal: {state["email_goal"]}
Tone: {state["tone"]}
Key Hooks:
{hooks_text}

--- EMAIL BODY ---
{state["email_body"]}

--- SUBJECT LINE WRITING RULES ---
Write exactly 3 options, each representing a different angle:
1. **Personalized**: Mentions the company name or specific focus context in a highly organic way.
2. **Benefit-driven**: Emphasizes the value or synergy they get (our value proposition).
3. **Curiosity / Hook**: Intriguing, short (3-5 words), low-friction, conversational (reads like it is from a colleague).

*Subject Line Best Practices:*
- Keep them short: 3 to 7 words. Long subjects get cut off on mobile.
- Use a conversational, natural casing (e.g. "quick question for {state['lead_company_name']}" or "synergy regarding {state['lead_company_focus']}"). Avoid title case or overly formal capitalization.
- NEVER use spam trigger words in the subject line (no "guarantee", "free", "limited time", "opportunity", "increase sales").
- Do not include placeholders like "[Company Name]" — replace it directly with the actual lead company name or details.

Return ONLY a JSON object with this exact schema:
{{
  "subject_options": [
     {{
       "subject": "the subject line option",
       "type": "Personalized / Benefit-driven / Curiosity Hook",
       "reason": "short explanation of why this converts based on lead data and psychological trigger"
     }},
     ...
  ]
}}

Return ONLY the raw JSON block. No markdown wrapper, no prose.
"""

    try:
        log.debug("[subject_writer] Invoking LLM")
        llm = _get_llm()
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt),
        ])
        log.debug("[subject_writer] Raw LLM response: %s", response.content[:300])
        parsed = _parse_json_block(response.content)

        options = parsed.get("subject_options", [])
        # Ensure we have exactly 3 options
        if not options:
            raise ValueError("No subject options returned in JSON.")

        log.info("[subject_writer] DONE | generated %d options", len(options))
        return {
            "subject_options": options,
            "error": None
        }
    except Exception as exc:
        log.error("[subject_writer] FAILED with error: %s", exc, exc_info=True)
        # Fallback response
        return {
            "subject_options": [
                {
                    "subject": f"Quick question for {state['lead_company_name']}",
                    "type": "Personalized",
                    "reason": "Uses company name to build relevance."
                },
                {
                    "subject": f"Value proposition for {state['lead_company_name']}",
                    "type": "Benefit-driven",
                    "reason": "Direct focus on B2B value exchange."
                },
                {
                    "subject": "synergy question",
                    "type": "Curiosity Hook",
                    "reason": "Short, informal, conversational."
                }
            ],
            "error": str(exc)
        }


# ---------------------------------------------------------------------------
# Graph assembly
# ---------------------------------------------------------------------------

def build_subject_graph():
    """Compile and return the LangGraph subject writer pipeline."""
    workflow = StateGraph(SubjectState)
    workflow.add_node("subject_writer", subject_writer_node)
    workflow.add_edge(START, "subject_writer")
    workflow.add_edge("subject_writer", END)
    return workflow.compile()


_graph = None


def run_subject_writer(
    lead: dict,
    analysis: dict,
    email_body: str
) -> List[Dict[str, str]]:
    """
    Entry point to run the Subject Line Writer Agent.
    """
    global _graph
    if _graph is None:
        log.info("Compiling LangGraph subject writer pipeline")
        _graph = build_subject_graph()
        log.info("LangGraph subject writer pipeline compiled successfully")

    def _get(d, *keys):
        for k in keys:
            if k in d:
                return d[k]
        return ""

    initial_state: SubjectState = {
        "lead_company_name": str(_get(lead, "Company Name", "company_name")),
        "lead_company_focus": str(_get(lead, "Company Focus", "company_focus")),
        "lead_our_value_proposition": str(_get(lead, "Our Value Proposition", "our_value_proposition")),
        "email_body": email_body,
        "tone": str(analysis.get("tone", "persuasive")),
        "email_goal": str(analysis.get("email_goal", "sales")),
        "key_hooks": list(analysis.get("key_hooks", [])),
        "subject_options": [],
        "error": None
    }

    log.info("Invoking subject writer graph | company='%s'", initial_state["lead_company_name"])
    result = _graph.invoke(initial_state)

    if result.get("error"):
        log.warning("Subject writer completed with error: %s", result["error"])

    return result.get("subject_options", [])
