"""
Email Templates — Template Library
====================================
Defines all available cold-email approach templates.

Each EmailTemplate has a rich schema covering:
  - Identity      : id, name, icon, category, style
  - Display       : tagline, description, use_cases, example_opening
  - Email Config  : tone, length, word_range
  - LLM Inputs    : body_template (structural skeleton), structure_hint

Frontend  : renders cards using all display + config fields
LLM prompt: injects structure_hint + body_template + tone/length
"""

from dataclasses import dataclass, field
from typing import List


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EmailTemplate:
    # ── Identity ─────────────────────────────────────────────────────────────
    id: str                   # machine key, e.g. "sales_pain_solution"
    name: str                 # display name, e.g. "Pain → Solution"
    icon: str                 # emoji shown in card
    category: str             # top-level bucket: "Sales" | "Partnership"
    style: str                # writing style label, e.g. "Professional", "Warm & Casual"

    # ── Display ──────────────────────────────────────────────────────────────
    tagline: str              # one-liner shown on the card
    description: str          # paragraph explaining the approach
    use_cases: List[str]      # 2–4 bullet points: when to use this
    example_opening: str      # first sentence of a sample email

    # ── Email Config ─────────────────────────────────────────────────────────
    tone: str                 # "formal" | "casual" | "persuasive" | "conversational" | "urgent"
    length: str               # "short" | "medium" | "long"
    word_range: str           # human-readable, e.g. "<100 words"

    # ── LLM Inputs ───────────────────────────────────────────────────────────
    body_template: str        # structural skeleton with {placeholder} hints
    structure_hint: str       # concise prose rules injected into LLM system prompt


# ---------------------------------------------------------------------------
# Template Definitions
# ---------------------------------------------------------------------------

# ╔══════════════════════════════════════════════════════════╗
# ║  CATEGORY 1 — SALES                                      ║
# ╚══════════════════════════════════════════════════════════╝

SALES_PAIN_SOLUTION = EmailTemplate(
    id="sales_pain_solution",
    name="Pain → Solution",
    icon="🎯",
    category="Sales",
    style="Sharp & Problem-Focused",
    tagline="Name the pain, then show yourself as the cure",
    description=(
        "Opens by identifying a specific pain point the prospect likely has, "
        "then pivots to position our product/service as the targeted solution. "
        "The most effective sales cold email structure for B2B and consulting outreach."
    ),
    use_cases=[
        "B2B service / SaaS sales outreach",
        "Agencies / SaaS companies pitching to businesses with visible challenges",
        "Consultants targeting a specific industry challenge",
        "Any situation where you know the company's pain point",
    ],
    example_opening="Most {company_focus} teams I talk to are losing hours every week to {pain_point} — and there's usually a faster way.",
    tone="persuasive",
    length="medium",
    word_range="130–190 words",
    body_template=(
        "Pain hook : Name a specific, realistic pain the target faces — be empathetic, not presumptuous.\n"
        "Pivot     : 'That's exactly the problem we help solve' — smooth transition.\n"
        "Solution  : 2 sentences: what we offer + how it specifically addresses the pain.\n"
        "Proof     : One result or credential that validates the claim.\n"
        "CTA       : Low-friction next step — a quick call, a demo, or a case study offer.\n"
        "Sign-off  : Confident, brief."
    ),
    structure_hint=(
        "STRUCTURE — Pain → Solution Sales:\n"
        "1. Pain hook: Open by naming a SPECIFIC, realistic pain related to the company's industry/focus. "
        "   Be empathetic — you're describing their problem, not selling at them yet.\n"
        "2. Pivot: Natural transition: 'That's exactly the problem we help [company type] solve.'\n"
        "3. Solution: What we offer and HOW it solves the named pain. Be specific, not vague.\n"
        "4. Proof: One credential, metric, or client result that builds credibility.\n"
        "5. CTA: One easy next step — a 15-min call, a free audit, a short demo.\n"
        "Tone: confident, problem-focused, never pushy. No buzzwords."
    ),
)

SALES_SOCIAL_PROOF = EmailTemplate(
    id="sales_social_proof",
    name="Social Proof First",
    icon="🏆",
    category="Sales",
    style="Credibility-First",
    tagline="Open with your biggest win to earn instant trust",
    description=(
        "Lead with a striking achievement, recognisable client name, or impressive metric "
        "that immediately establishes authority. Best when you have impressive past results "
        "that are directly relevant to the prospect's world."
    ),
    use_cases=[
        "When we have impressive, verifiable past results",
        "Reaching out to large companies or known brands",
        "Competitive markets where credibility matters first",
        "When name-dropping a mutual client is appropriate",
    ],
    example_opening="We helped a company in {company_focus} cut operational costs by 35% in 90 days — here's how we did it.",
    tone="formal",
    length="medium",
    word_range="140–200 words",
    body_template=(
        "Proof opener : Lead with our strongest achievement or most relevant client result.\n"
        "Relevance    : Explain in 1 sentence why this result matters to the prospect.\n"
        "Offer        : Describe what we offer in 1–2 sentences — be specific.\n"
        "Fit          : Why does this company specifically benefit? Connect to their focus.\n"
        "CTA          : Offer a case study, call, or next step.\n"
        "Sign-off     : Professional close."
    ),
    structure_hint=(
        "STRUCTURE — Social Proof Sales:\n"
        "1. Proof opener: Lead with a quantified result or recognisable brand credential. "
        "   Use real numbers — '35% cost reduction', '10x faster deployment', etc.\n"
        "2. Relevance: 'Companies like {company} in {company_focus} face the same challenge…'\n"
        "3. Offer: What exactly we provide — be concrete, not 'we offer solutions'.\n"
        "4. Company fit: Directly reference their industry/focus and why our offer fits.\n"
        "5. CTA: Offer to share the full case study or schedule a call.\n"
        "Tone: formal, credible, professional. Let the numbers do the persuasion."
    ),
)


# ╔══════════════════════════════════════════════════════════╗
# ║  CATEGORY 2 — PARTNERSHIP                                ║
# ╚══════════════════════════════════════════════════════════╝

PARTNERSHIP_COLLAB = EmailTemplate(
    id="partnership_collab",
    name="Collaboration Proposal",
    icon="🚀",
    category="Partnership",
    style="Strategic & Mutual-Benefit",
    tagline="Pitch a win-win partnership with clear mutual upside",
    description=(
        "A strategic email proposing a partnership, integration, or collaboration. "
        "Leads with mutual benefit — what THEY gain — before explaining what we offer. "
        "Essential framing: this is about them as much as about you."
    ),
    use_cases=[
        "Proposing a product integration or API partnership",
        "Agency / business seeking a strategic collaboration",
        "Two complementary businesses exploring co-marketing",
        "Referral or affiliate partnership proposals",
    ],
    example_opening="I think there's a genuine opportunity for {company} and our team to create something that neither of us could build as well alone.",
    tone="conversational",
    length="long",
    word_range="150–230 words",
    body_template=(
        "Hook       : Frame a shared opportunity — something both sides stand to gain.\n"
        "Their gain : What THEY get from this partnership (lead with their benefit, not yours).\n"
        "Our offer  : What we bring to the table — offerings, audience, technology, etc.\n"
        "Evidence   : A quick credential or past collaboration that shows we deliver.\n"
        "Fit reason : Why THIS specific company is the right partner.\n"
        "CTA        : Propose a discovery call or a concrete next step.\n"
        "Sign-off   : Warm but professional."
    ),
    structure_hint=(
        "STRUCTURE — Collaboration Partnership:\n"
        "1. Mutual opportunity hook: Open with the shared opportunity — what BOTH sides could gain. "
        "   Do NOT open with what WE want.\n"
        "2. Their benefit: 1–2 sentences on what the company gains from this partnership specifically.\n"
        "3. Our contribution: What we bring — be concrete (services, platform, audience, technology).\n"
        "4. Validation: One proof point showing we've successfully collaborated before.\n"
        "5. Specificity: Why THIS company over any other potential partner?\n"
        "6. CTA: A low-friction next step — 'Would a 20-minute discovery call make sense?'\n"
        "Tone: strategic, warm, peer-level. Avoid sounding like you need them more than they need you."
    ),
)

PARTNERSHIP_REFERRAL = EmailTemplate(
    id="partnership_referral",
    name="Referral / Affiliate Pitch",
    icon="🔗",
    category="Partnership",
    style="Direct & Benefit-Focused",
    tagline="Propose a simple referral loop that benefits both sides",
    description=(
        "A concise proposal for a referral or affiliate arrangement — we'll send them clients, "
        "they send us clients (or vice versa). Works best when there's a clear complementary "
        "audience overlap with no direct competition."
    ),
    use_cases=[
        "Agencies with complementary but non-competing services",
        "Freelancers with overlapping client bases",
        "SaaS tools that integrate with each other",
        "Service providers targeting the same buyer persona",
    ],
    example_opening="Our clients often need exactly what {company} offers — and I suspect yours might need what we do.",
    tone="casual",
    length="medium",
    word_range="110–160 words",
    body_template=(
        "Hook    : State the obvious overlap — 'Our clients need you, yours might need us.'\n"
        "Who we are: 1 sentence — what we do and who we serve.\n"
        "Overlap : Why the client bases are complementary.\n"
        "Proposal: Simple referral / affiliate structure idea (1 sentence).\n"
        "CTA     : 'Want to explore this over a quick call?'\n"
        "Sign-off: Casual, friendly."
    ),
    structure_hint=(
        "STRUCTURE — Referral / Affiliate Pitch:\n"
        "1. Hook: State the audience overlap immediately — make it obvious in the first sentence.\n"
        "2. Who we are: 1 sentence. Focus on WHO we serve, not what we do.\n"
        "3. Overlap: Why the two audiences are complementary without competing.\n"
        "4. Proposal: A simple, fair referral or affiliate idea — keep it informal at this stage.\n"
        "5. CTA: Very soft — a call to explore, nothing more.\n"
        "Tone: casual, friendly, peer-to-peer. This is a conversation starter, not a legal proposal."
    ),
)


# ---------------------------------------------------------------------------
# Exported Registry
# ---------------------------------------------------------------------------

ALL_TEMPLATES: List[EmailTemplate] = [
    # Sales
    SALES_PAIN_SOLUTION,
    SALES_SOCIAL_PROOF,
    # Partnership
    PARTNERSHIP_COLLAB,
    PARTNERSHIP_REFERRAL,
]

TEMPLATES_BY_ID: dict = {t.id: t for t in ALL_TEMPLATES}

# Category ordering for the UI tab/group display
CATEGORIES: List[str] = [
    "Sales",
    "Partnership",
]

CATEGORY_ICONS: dict = {
    "Sales":           "🎯",
    "Partnership":     "🚀",
}

def get_template(template_id: str) -> EmailTemplate:
    """Return a template by its ID, defaulting to SALES_PAIN_SOLUTION if not found."""
    return TEMPLATES_BY_ID.get(template_id, SALES_PAIN_SOLUTION)


def get_templates_by_category(category: str) -> List[EmailTemplate]:
    """Return all templates belonging to a given category."""
    return [t for t in ALL_TEMPLATES if t.category == category]
