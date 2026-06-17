"""
Analyzer Agent — LangGraph pipeline
=====================================
Graph:  START → input_analyzer → strategy_planner → END

Node responsibilities
---------------------
input_analyzer   : Parse company details, identify target audience & email goal.
strategy_planner : Decide tone, email length bucket, and key hooks to emphasize.
"""

import json
import os
from typing import Optional

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

class LeadAnalysisState(TypedDict):
    # ── Inputs ──────────────────────────────────────────────────────────────
    company_name: str
    target_role: str
    company_focus: str
    my_skills: str
    experience_years: float
    api_key: str                        # passed in at invocation time

    # ── Phase 1: Input Analysis (populated by input_analyzer) ──────────────
    company_industry: str               # e.g. "Artificial Intelligence"
    value_proposition: str             # one-sentence company pitch
    target_audience: str               # "startup" | "mid-size" | "enterprise"
    email_goal: str                    # "sales" | "recruitment" | "partnership"

    # ── Phase 2: Strategy (populated by strategy_planner) ──────────────────
    tone: str                          # "formal" | "casual" | "persuasive" | "urgent"
    email_length: str                  # "short" | "medium" | "long"
    word_range: str                    # e.g. "<100 words"
    key_hooks: list                    # list[str] – bullet points to emphasize

    # ── Meta ────────────────────────────────────────────────────────────────
    error: Optional[str]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_llm(api_key: str = "") -> ChatGoogleGenerativeAI:
    """Return a Gemini 2.5 Flash chat model using the provided key."""
    key = api_key.strip() if api_key else (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY", ""))
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=key,
        temperature=0.3,
    )


def _parse_json_block(text: str) -> dict:
    """
    Extract the first JSON object from a model response that may be wrapped
    in markdown fences or contain extra prose.
    """
    # Strip markdown fences if present
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
# Node 1 – Input Analyzer
# ---------------------------------------------------------------------------

def input_analyzer_node(state: LeadAnalysisState) -> dict:
    """
    Analyse the raw lead data and return structured company / audience insight.
    """
    log.info("[input_analyzer] START | company='%s' role='%s'",
             state['company_name'], state['target_role'])

    system_prompt = (
        "You are a business intelligence analyst specialising in B2B outreach. "
        "Given a lead's details, extract structured information in valid JSON only. "
        "Do NOT include any prose outside the JSON block."
    )

    human_prompt = f"""Analyse the following lead and return a JSON object with exactly these keys:

- company_industry   : The primary industry of the company (string, ≤4 words)
- value_proposition  : One-sentence description of what the company does / its main value (string)
- target_audience    : Company size category — one of "startup", "mid-size", "enterprise" (string)
- email_goal         : Most appropriate email goal — one of "sales", "recruitment", "partnership" (string)

Lead data:
  Company Name  : {state["company_name"]}
  Target Role   : {state["target_role"]}
  Company Focus : {state["company_focus"]}
  My Skills     : {state["my_skills"]}
  Experience    : {state["experience_years"]} years

Return ONLY the JSON object, nothing else."""

    try:
        log.debug("[input_analyzer] Invoking Gemini LLM")
        llm = _get_llm(state["api_key"])
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt),
        ])
        log.debug("[input_analyzer] Raw LLM response: %s", response.content[:300])
        parsed = _parse_json_block(response.content)
        log.info("[input_analyzer] DONE | industry='%s' goal='%s' audience='%s'",
                 parsed.get('company_industry'), parsed.get('email_goal'), parsed.get('target_audience'))
        return {
            "company_industry": parsed.get("company_industry", "Technology"),
            "value_proposition": parsed.get("value_proposition", ""),
            "target_audience": parsed.get("target_audience", "mid-size"),
            "email_goal": parsed.get("email_goal", "recruitment"),
            "error": None,
        }
    except Exception as exc:
        log.error("[input_analyzer] FAILED with error: %s", exc, exc_info=True)
        # Graceful fallback so the graph doesn't crash
        return {
            "company_industry": "Technology",
            "value_proposition": f"{state['company_name']} operates in {state['company_focus']}.",
            "target_audience": "mid-size",
            "email_goal": "recruitment",
            "error": str(exc),
        }


# ---------------------------------------------------------------------------
# Node 2 – Strategy Planner
# ---------------------------------------------------------------------------

def strategy_planner_node(state: LeadAnalysisState) -> dict:
    """
    Decide the email tone, length, and key hooks based on the analysis output.
    """
    log.info("[strategy_planner] START | industry='%s' goal='%s'",
             state.get('company_industry'), state.get('email_goal'))

    system_prompt = (
        "You are an expert cold-email strategist. "
        "Given the analysis of a lead, decide the optimal email strategy and return valid JSON only. "
        "Do NOT include any prose outside the JSON block."
    )

    human_prompt = f"""Based on this lead analysis, determine the best email strategy and return a JSON object with exactly these keys:

- tone        : One of "formal", "casual", "persuasive", "urgent" (string)
- email_length: One of "short", "medium", "long" (string)
  - short  = fewer than 100 words
  - medium = 100–200 words
  - long   = more than 200 words
- word_range  : Human-readable range, e.g. "<100 words" or "100–200 words" or ">200 words" (string)
- key_hooks   : A list of 3–5 short bullet-point strings — the most important angles to emphasise
                in the email given the candidate's skills and the company's focus

Analysis:
  Company         : {state["company_name"]}
  Industry        : {state.get("company_industry", "")}
  Value Prop      : {state.get("value_proposition", "")}
  Audience Size   : {state.get("target_audience", "")}
  Email Goal      : {state.get("email_goal", "")}
  Target Role     : {state["target_role"]}
  Company Focus   : {state["company_focus"]}
  Candidate Skills: {state["my_skills"]}
  Experience      : {state["experience_years"]} years

Return ONLY the JSON object, nothing else."""

    try:
        log.debug("[strategy_planner] Invoking Gemini LLM")
        llm = _get_llm(state["api_key"])
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt),
        ])
        log.debug("[strategy_planner] Raw LLM response: %s", response.content[:300])
        parsed = _parse_json_block(response.content)

        # Normalise email_length → word_range fallback
        length = parsed.get("email_length", "medium")
        default_ranges = {"short": "<100 words", "medium": "100–200 words", "long": ">200 words"}

        hooks = parsed.get("key_hooks", [])
        log.info("[strategy_planner] DONE | tone='%s' length='%s' hooks=%d",
                 parsed.get('tone'), length, len(hooks))
        return {
            "tone": parsed.get("tone", "persuasive"),
            "email_length": length,
            "word_range": parsed.get("word_range", default_ranges.get(length, "100–200 words")),
            "key_hooks": hooks,
            "error": state.get("error"),   # preserve upstream error if any
        }
    except Exception as exc:
        log.error("[strategy_planner] FAILED with error: %s", exc, exc_info=True)
        return {
            "tone": "persuasive",
            "email_length": "medium",
            "word_range": "100–200 words",
            "key_hooks": [
                f"Strong expertise in {state['my_skills']}",
                f"Direct alignment with {state['company_focus']}",
                f"{state['experience_years']} years of relevant experience",
            ],
            "error": str(exc),
        }


# ---------------------------------------------------------------------------
# Graph assembly
# ---------------------------------------------------------------------------

def build_analyzer_graph():
    """Compile and return the LangGraph analyzer pipeline."""
    workflow = StateGraph(LeadAnalysisState)

    workflow.add_node("input_analyzer", input_analyzer_node)
    workflow.add_node("strategy_planner", strategy_planner_node)

    workflow.add_edge(START, "input_analyzer")
    workflow.add_edge("input_analyzer", "strategy_planner")
    workflow.add_edge("strategy_planner", END)

    return workflow.compile()


# Singleton — compiled once and reused across Streamlit reruns
_graph = None


def run_analyzer(lead: dict, api_key: str = "") -> LeadAnalysisState:
    """
    Entry point called from the Streamlit app.

    Parameters
    ----------
    lead    : dict with keys matching the lead fields (both display-name and
              snake_case variants are accepted).
    api_key : Gemini/Google API key (overrides environment variable).

    Returns
    -------
    Populated LeadAnalysisState dict.
    """
    global _graph
    if _graph is None:
        log.info("Compiling LangGraph analyzer pipeline")
        _graph = build_analyzer_graph()
        log.info("LangGraph pipeline compiled successfully")

    # Normalise key names — accept both "Company Name" and "company_name"
    def _get(d, *keys):
        for k in keys:
            if k in d:
                return d[k]
        return ""

    initial_state: LeadAnalysisState = {
        "company_name": str(_get(lead, "Company Name", "company_name")),
        "target_role": str(_get(lead, "Target Role", "target_role")),
        "company_focus": str(_get(lead, "Company Focus", "company_focus")),
        "my_skills": str(_get(lead, "My Skills", "my_skills")),
        "experience_years": float(_get(lead, "Experience (Years)", "experience_years") or 0),
        "api_key": api_key,
        # Phase 1 — will be populated by input_analyzer
        "company_industry": "",
        "value_proposition": "",
        "target_audience": "",
        "email_goal": "",
        # Phase 2 — will be populated by strategy_planner
        "tone": "",
        "email_length": "",
        "word_range": "",
        "key_hooks": [],
        "error": None,
    }

    log.info("Invoking analyzer graph | company='%s' role='%s' api_key_set=%s",
             initial_state["company_name"], initial_state["target_role"],
             bool(api_key.strip() if api_key else ""))

    result = _graph.invoke(initial_state)

    if result.get("error"):
        log.warning("Analyzer completed with error(s): %s", result["error"])
    else:
        log.info("Analyzer graph completed successfully | tone='%s' length='%s'",
                 result.get("tone"), result.get("email_length"))

    return result
