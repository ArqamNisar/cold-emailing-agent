"""
Compliance Checker Agent — LangGraph pipeline
=============================================
Graph: START → compliance_checker → END

Evaluates generated cold emails for:
1. Spam keywords (flag and suggest alternatives)
2. FTC requirements (physical address and opt-out/unsubscribe instructions)
3. Misleading claims or exaggerations
4. Readability (sentence length, complexity)
5. Engagement factors (questions, personalization)

Also produces an enhanced version (enhanced_subject & enhanced_body) addressing any findings.
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

class ComplianceState(TypedDict):
    # ── Inputs ──────────────────────────────────────────────────────────────
    subject: str
    body: str
    lead_company_name: str
    lead_company_focus: str
    lead_our_value_proposition: str

    # ── Outputs ─────────────────────────────────────────────────────────────
    is_compliant: bool
    spam_keywords: List[Dict[str, str]]  # list of {"keyword": "...", "alternative": "...", "reason": "..."}
    ftc_status: Dict[str, any]           # {"has_address": bool, "has_unsubscribe": bool, "issues": list[str]}
    claims_status: Dict[str, any]        # {"has_misleading_claims": bool, "issues": list[str]}
    readability: Dict[str, any]          # {"sentence_length_ok": bool, "complexity": str, "score_desc": str, "issues": list[str]}
    engagement: Dict[str, any]           # {"has_questions": bool, "personalization_ok": bool, "suggestions": list[str]}

    enhanced_subject: str
    enhanced_body: str

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
        temperature=0.2,  # Low temperature for analytical consistency
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
# Node – Compliance Checker
# ---------------------------------------------------------------------------

def compliance_checker_node(state: ComplianceState) -> dict:
    """
    Evaluates the compliance of the input email and writes an enhanced version.
    """
    log.info("[compliance_checker] START | lead='%s'", state['lead_company_name'])

    system_prompt = (
        "You are an expert cold email compliance officer and copy editor.\n"
        "Your task is to analyze cold outreach emails for legal compliance (FTC CAN-SPAM), "
        "spam filter triggers, deceptive claims, readability, and engagement.\n"
        "You must return a valid JSON object ONLY. Do NOT include any markdown formatting, "
        "comments, or introductory/concluding text outside the JSON block."
    )

    human_prompt = f"""Analyze this generated cold email and return a JSON object.

--- LEAD CONTEXT ---
Target Company: {state["lead_company_name"]}
Company Focus: {state["lead_company_focus"]}
Our Value Proposition: {state["lead_our_value_proposition"]}

--- EMAIL TO EVALUATE ---
Subject: {state["subject"]}
Body:
{state["body"]}

--- EVALUATION REQUIREMENTS ---
Evaluate the email against these 5 categories and determine if improvements are needed:

1. Spam keywords:
   - Identify words or phrases known to trigger email spam filters (e.g., "guarantee", "100% free", "risk-free", "act now", "limited time", "click here", "cash", "earn", "pure profit", "winner").
   - If found, flag them and suggest professional, safer B2B alternatives.
   
2. FTC requirements (CAN-SPAM Act):
   - Check if there is a clear physical address placeholder or notice (e.g. "[Physical Address]" or an address footer).
   - Check if there is a clear unsubscribe/opt-out option (e.g. "If you'd rather not hear from us...", "reply with opt out", or "unsubscribe here").
   
3. Misleading claims or exaggerations:
   - Identify any pushy, exaggerated, or false guarantees (e.g. "we will double your revenue in 2 weeks" or "100% guaranteed success").
   
4. Readability:
   - Check if sentences are concise (avoid sentences longer than 25 words).
   - Grade the complexity (Low, Medium, High) and explain if it is conversational and easy to read.
   
5. Engagement:
   - Verify that there is at least one low-friction question or CTA.
   - Verify that the email is personalized using the lead's company focus/name.

--- ENHANCED VERSION WRITING RULES ---
If any category needs improvement (i.e. is_compliant is false or there are suggestions/issues), write an enhanced version (enhanced_subject & enhanced_body) that:
- Replaces spam keywords with the suggested alternatives.
- Appends a clean, professional FTC footer at the very bottom of the body, for example:
  "\\n\\n---\\nIf you would prefer not to receive future updates, please reply with 'opt out' or unsubscribe.\\n[Your Firm] | 123 Business Rd, Suite 100, City, State"
- Rewrites or tones down any exaggerated claims to be realistic and consultative.
- Breaks up overly complex or long sentences to improve flow.
- Adds an engaging CTA or personalization if they are weak.
- Ensure the layout, formatting, and paragraphs remain clean and natural.

Return ONLY a JSON object with this exact schema:
{{
  "is_compliant": true/false (set false if spam words exist, FTC address or unsubscribe is missing, or misleading claims exist),
  "spam_keywords": [
     {{"keyword": "...", "alternative": "...", "reason": "..."}}
  ],
  "ftc_status": {{
     "has_address": true/false,
     "has_unsubscribe": true/false,
     "issues": ["..."]
  }},
  "claims_status": {{
     "has_misleading_claims": true/false,
     "issues": ["..."]
  }},
  "readability": {{
     "sentence_length_ok": true/false,
     "complexity": "Low/Medium/High",
     "score_desc": "Conversational and clear / Jargon-heavy or too long",
     "issues": ["..."]
  }},
  "engagement": {{
     "has_questions": true/false,
     "personalization_ok": true/false,
     "suggestions": ["..."]
  }},
  "enhanced_subject": "...",
  "enhanced_body": "..."
}}

Return ONLY the raw JSON block. No markdown wrapper, no prose.
"""

    try:
        log.debug("[compliance_checker] Invoking LLM")
        llm = _get_llm()
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt),
        ])
        log.debug("[compliance_checker] Raw LLM response: %s", response.content[:300])
        parsed = _parse_json_block(response.content)

        # Ensure enhanced fields fall back to originals if missing or empty
        enhanced_sub = parsed.get("enhanced_subject", "").strip() or state["subject"]
        enhanced_bd = parsed.get("enhanced_body", "").strip() or state["body"]

        # If it is missing FTC details, double check if LLM added them. If not, append them programmatically to enhanced_body
        ftc = parsed.get("ftc_status", {})
        if not ftc.get("has_address") or not ftc.get("has_unsubscribe"):
            if "opt out" not in enhanced_bd.lower() and "unsubscribe" not in enhanced_bd.lower():
                enhanced_bd += "\n\n---\nIf you would prefer not to receive future updates, please reply with 'opt out' or unsubscribe.\n[Your Firm] | 123 Business Rd, Suite 100, City, State"

        log.info("[compliance_checker] DONE | compliant=%s | spam_words=%d",
                 parsed.get('is_compliant'), len(parsed.get('spam_keywords', [])))

        return {
            "is_compliant": parsed.get("is_compliant", True),
            "spam_keywords": parsed.get("spam_keywords", []),
            "ftc_status": {
                "has_address": parsed.get("ftc_status", {}).get("has_address", True),
                "has_unsubscribe": parsed.get("ftc_status", {}).get("has_unsubscribe", True),
                "issues": parsed.get("ftc_status", {}).get("issues", [])
            },
            "claims_status": {
                "has_misleading_claims": parsed.get("claims_status", {}).get("has_misleading_claims", False),
                "issues": parsed.get("claims_status", {}).get("issues", [])
            },
            "readability": {
                "sentence_length_ok": parsed.get("readability", {}).get("sentence_length_ok", True),
                "complexity": parsed.get("readability", {}).get("complexity", "Medium"),
                "score_desc": parsed.get("readability", {}).get("score_desc", "Good"),
                "issues": parsed.get("readability", {}).get("issues", [])
            },
            "engagement": {
                "has_questions": parsed.get("engagement", {}).get("has_questions", True),
                "personalization_ok": parsed.get("engagement", {}).get("personalization_ok", True),
                "suggestions": parsed.get("engagement", {}).get("suggestions", [])
            },
            "enhanced_subject": enhanced_sub,
            "enhanced_body": enhanced_bd,
            "error": None
        }
    except Exception as exc:
        log.error("[compliance_checker] FAILED with error: %s", exc, exc_info=True)
        # Fallback response
        return {
            "is_compliant": True,
            "spam_keywords": [],
            "ftc_status": {"has_address": True, "has_unsubscribe": True, "issues": []},
            "claims_status": {"has_misleading_claims": False, "issues": []},
            "readability": {"sentence_length_ok": True, "complexity": "Medium", "score_desc": "Good", "issues": []},
            "engagement": {"has_questions": True, "personalization_ok": True, "suggestions": []},
            "enhanced_subject": state["subject"],
            "enhanced_body": state["body"],
            "error": str(exc)
        }


# ---------------------------------------------------------------------------
# Graph assembly
# ---------------------------------------------------------------------------

def build_compliance_graph():
    """Compile and return the LangGraph compliance pipeline."""
    workflow = StateGraph(ComplianceState)
    workflow.add_node("compliance_checker", compliance_checker_node)
    workflow.add_edge(START, "compliance_checker")
    workflow.add_edge("compliance_checker", END)
    return workflow.compile()


_graph = None


def run_compliance_checker(
    subject: str,
    body: str,
    lead: dict
) -> ComplianceState:
    """
    Entry point to run compliance checking on a generated email.
    """
    global _graph
    if _graph is None:
        log.info("Compiling LangGraph compliance pipeline")
        _graph = build_compliance_graph()
        log.info("LangGraph compliance pipeline compiled successfully")

    def _get(d, *keys):
        for k in keys:
            if k in d:
                return d[k]
        return ""

    initial_state: ComplianceState = {
        "subject": subject,
        "body": body,
        "lead_company_name": str(_get(lead, "Company Name", "company_name")),
        "lead_company_focus": str(_get(lead, "Company Focus", "company_focus")),
        "lead_our_value_proposition": str(_get(lead, "Our Value Proposition", "our_value_proposition")),
        "is_compliant": True,
        "spam_keywords": [],
        "ftc_status": {"has_address": True, "has_unsubscribe": True, "issues": []},
        "claims_status": {"has_misleading_claims": False, "issues": []},
        "readability": {"sentence_length_ok": True, "complexity": "Medium", "score_desc": "Good", "issues": []},
        "engagement": {"has_questions": True, "personalization_ok": True, "suggestions": []},
        "enhanced_subject": "",
        "enhanced_body": "",
        "error": None
    }

    log.info("Invoking compliance checker graph | subject='%s'", subject)
    result = _graph.invoke(initial_state)

    if result.get("error"):
        log.warning("Compliance checker completed with error: %s", result["error"])

    return result
