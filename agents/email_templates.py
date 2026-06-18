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
    id: str                   # machine key, e.g. "job_inquiry_direct"
    name: str                 # display name, e.g. "Direct Job Inquiry"
    icon: str                 # emoji shown in card
    category: str             # top-level bucket: "Job Inquiry" | "Networking" |
                              #   "Portfolio Share" | "Sales" | "Partnership"
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
# ║  CATEGORY 1 — JOB INQUIRY                               ║
# ╚══════════════════════════════════════════════════════════╝

JOB_INQUIRY_DIRECT = EmailTemplate(
    id="job_inquiry_direct",
    name="Direct Job Inquiry",
    icon="💼",
    category="Job Inquiry",
    style="Professional & Confident",
    tagline="Straight to the point — express your interest and fit",
    description=(
        "A professional, concise email expressing direct interest in a role at the company. "
        "States who you are, what you bring, and why you want THIS company specifically. "
        "Ideal when a job posting exists or you're confident about a need."
    ),
    use_cases=[
        "Responding to an active job posting",
        "Reaching out to HR / recruiters directly",
        "Applying to startups with no formal process",
        "Following up after submitting an application",
    ],
    example_opening="I'm reaching out to express my strong interest in the {role} position at {company}.",
    tone="formal",
    length="medium",
    word_range="100–150 words",
    body_template=(
        "Opening  : State the role you're interested in and where you found it (or that you're reaching out proactively).\n"
        "Paragraph 1: Two sentences on your most relevant experience — skills + years + one measurable achievement.\n"
        "Paragraph 2: One sentence explaining why THIS company excites you (reference their focus/mission).\n"
        "CTA      : Ask to connect, share your portfolio/CV, or schedule a brief call.\n"
        "Sign-off : Professional close."
    ),
    structure_hint=(
        "STRUCTURE — Direct Job Inquiry:\n"
        "1. Hook: 'I'm reaching out about the {role} role at {company}.' Keep it immediate.\n"
        "2. Credentials: 1–2 sentences — your experience + a specific, quantified achievement.\n"
        "3. Company alignment: Why THIS company? Reference their product/mission/industry in one sentence.\n"
        "4. CTA: Clear, low-friction ask. E.g. 'I'd love to share my portfolio — are you open to a 15-min call?'\n"
        "Tone: formal, confident, respectful. No fluff. No 'I hope this email finds you well.'"
    ),
)

JOB_INQUIRY_VALUE = EmailTemplate(
    id="job_inquiry_value",
    name="Value-Led Inquiry",
    icon="💎",
    category="Job Inquiry",
    style="Bold & Results-Driven",
    tagline="Lead with the impact you'll deliver, not your job title",
    description=(
        "Instead of opening with 'I'm applying for…', open with the specific value you deliver. "
        "Hiring managers read dozens of standard applications — this approach stands out by "
        "making the benefit to them immediately obvious."
    ),
    use_cases=[
        "Standing out in competitive hiring pipelines",
        "Reaching out to companies not actively hiring",
        "Senior / specialist roles where impact matters",
        "When you have strong, quantifiable achievements",
    ],
    example_opening="I cut infrastructure costs by 40% at my last company — I'd like to explore if I can do the same for {company}.",
    tone="persuasive",
    length="medium",
    word_range="120–180 words",
    body_template=(
        "Opening  : Lead with your single strongest, quantified value claim — make the benefit obvious.\n"
        "Paragraph 1: Back the claim — one concrete project, metric, or outcome that proves it.\n"
        "Paragraph 2: Connect your value to the company's known focus area or a challenge they face.\n"
        "CTA      : Invite a conversation to explore fit.\n"
        "Sign-off : Confident, brief close."
    ),
    structure_hint=(
        "STRUCTURE — Value-Led Inquiry:\n"
        "1. Value hook: Open with a bold, specific, quantified claim in the first sentence. "
        "   Make the reader think 'how?' — do NOT open with 'I am a developer with 5 years…'\n"
        "2. Proof: One concrete example backing the claim (project, tool, result).\n"
        "3. Relevance: Connect your value directly to the company's industry/focus in 1 sentence.\n"
        "4. CTA: 'I'd love to explore whether my profile fits what you're building at {company}.'\n"
        "Tone: persuasive, confident. Use active voice throughout. Avoid generic filler phrases."
    ),
)

# ╔══════════════════════════════════════════════════════════╗
# ║  CATEGORY 2 — NETWORKING                                ║
# ╚══════════════════════════════════════════════════════════╝

NETWORKING_GENUINE = EmailTemplate(
    id="networking_genuine",
    name="Genuine Connection",
    icon="🤝",
    category="Networking",
    style="Warm & Conversational",
    tagline="Build a real relationship — no immediate ask",
    description=(
        "A warm, low-pressure email that seeks to establish a genuine connection with "
        "someone at the company — not to directly ask for a job. References their work, "
        "finds common ground, and simply opens a dialogue. Plays a long game."
    ),
    use_cases=[
        "Reaching out to potential mentors or industry peers",
        "Building a relationship before a role opens up",
        "Connecting with team leads / engineers at dream companies",
        "Following someone whose work you genuinely admire",
    ],
    example_opening="I've been following your team's work on {company_focus} and your recent post on {topic} really resonated with me.",
    tone="conversational",
    length="short",
    word_range="80–120 words",
    body_template=(
        "Opening  : Reference something specific about their work, company, or a public post — make it genuine.\n"
        "Paragraph 1: Briefly introduce yourself and the intersection between your work and theirs.\n"
        "CTA      : A very soft ask — 'I'd love to hear your perspective' or 'Would you be open to a quick chat?'\n"
        "Sign-off : Warm, casual close. First name only is fine."
    ),
    structure_hint=(
        "STRUCTURE — Genuine Networking:\n"
        "1. Personal opener: Reference something SPECIFIC about their company, work, or a public statement. "
        "   This must feel researched and human — not generic.\n"
        "2. Self-intro: Who you are in 1 sentence (no job title recitation — focus on what you care about).\n"
        "3. Intersection: The shared interest or topic area that makes this connection make sense.\n"
        "4. Soft CTA: No job ask. Just an invitation to connect, share ideas, or chat briefly.\n"
        "Tone: warm, genuine, conversational. Read like a message from a real person, not a recruiter."
    ),
)

NETWORKING_INSIGHT = EmailTemplate(
    id="networking_insight",
    name="Insight Share",
    icon="💡",
    category="Networking",
    style="Thought Leadership",
    tagline="Lead with a useful insight to spark a real conversation",
    description=(
        "Open by sharing a relevant observation, trend, or insight related to the recipient's "
        "industry or work. Positions you as a peer worth talking to, not just a job seeker. "
        "Exceptional for connecting with CTOs, engineering leads, and founders."
    ),
    use_cases=[
        "Reaching out to technical leaders or founders",
        "Starting a conversation about industry trends",
        "Demonstrating domain expertise before a job ask",
        "Standing out when everyone else is begging for a call",
    ],
    example_opening="I've been thinking about how companies like {company} are approaching {company_focus} — and I have a take that might be worth 5 minutes of your time.",
    tone="conversational",
    length="short",
    word_range="80–100 words",
    body_template=(
        "Opening  : Share a specific, non-obvious observation about their industry or company focus.\n"
        "Paragraph 1: Expand the insight briefly — 2 sentences max. Don't over-explain.\n"
        "Bridge   : Connect your expertise to the insight ('I've been working in this space and…').\n"
        "CTA      : Invite a conversation — not about a job, but about the topic itself.\n"
        "Sign-off : Casual, curious close."
    ),
    structure_hint=(
        "STRUCTURE — Insight Share Networking:\n"
        "1. Insight hook: Open with a sharp, specific observation about the company's industry or "
        "   technology space. It should make the reader think 'hmm, that's interesting'.\n"
        "2. Brief expansion: 1–2 sentences that deepen the insight without over-explaining.\n"
        "3. Credential bridge: Tie your background naturally to the insight topic.\n"
        "4. Curiosity CTA: Ask for THEIR perspective, not a job interview. E.g. 'Would love to hear your take.'\n"
        "Tone: peer-to-peer, intellectually curious, not salesy."
    ),
)

# ╔══════════════════════════════════════════════════════════╗
# ║  CATEGORY 3 — PORTFOLIO SHARE                           ║
# ╚══════════════════════════════════════════════════════════╝

PORTFOLIO_SHOWCASE = EmailTemplate(
    id="portfolio_showcase",
    name="Portfolio Showcase",
    icon="🎨",
    category="Portfolio Share",
    style="Creative & Confident",
    tagline="Let your work speak first — then invite them in",
    description=(
        "Opens by pointing to specific work relevant to the company's product or domain. "
        "Positions the portfolio as the primary credibility signal, not a resume. "
        "Excellent for designers, engineers, writers, and other craft-driven roles."
    ),
    use_cases=[
        "Creative / design / engineering portfolios",
        "Open-source projects relevant to the company's stack",
        "Freelancers or consultants pitching for project work",
        "Candidates who feel their work speaks louder than their CV",
    ],
    example_opening="I built something that I think you'll find relevant to what {company} is working on — I'd love your feedback.",
    tone="casual",
    length="short",
    word_range="80–120 words",
    body_template=(
        "Opening  : Lead with the portfolio item — describe it in one intriguing sentence.\n"
        "Paragraph 1: Explain the relevance — how this work connects to the company's product/stack/domain.\n"
        "Link/CTA : Share the link and invite them to take a look. Keep the ask lightweight.\n"
        "Optional : One sentence noting openness to roles or collaboration.\n"
        "Sign-off : Casual and confident."
    ),
    structure_hint=(
        "STRUCTURE — Portfolio Showcase:\n"
        "1. Lead with work: Describe a specific project, tool, or piece of work in one intriguing sentence. "
        "   Make them curious enough to click a link.\n"
        "2. Relevance bridge: Why does this work matter to THIS company? Connect it to their stack or domain.\n"
        "3. Invite: Share the link concept (write '[portfolio link]') and ask for their thoughts — "
        "   a curiosity CTA is more powerful than a job ask here.\n"
        "4. Optional role mention: One final sentence noting you're open to roles/collaboration if it fits.\n"
        "Tone: casual, confident, creative. The work is the star — not the job hunt."
    ),
)

PORTFOLIO_CASE_STUDY = EmailTemplate(
    id="portfolio_case_study",
    name="Case Study Pitch",
    icon="📊",
    category="Portfolio Share",
    style="Data-Driven & Professional",
    tagline="Show a before/after result that mirrors their challenge",
    description=(
        "Presents a mini case study: a problem you solved that mirrors a challenge the company "
        "likely faces. Quantified outcomes make this highly persuasive. Ideal for consultants, "
        "analysts, and senior engineers with measurable track records."
    ),
    use_cases=[
        "Consulting or freelance pitches",
        "Senior roles requiring proven outcomes",
        "Companies in the same domain as your past project",
        "When you want to demonstrate ROI before being hired",
    ],
    example_opening="Here's a 60-second case study that might be relevant to what {company} is tackling right now.",
    tone="persuasive",
    length="medium",
    word_range="130–180 words",
    body_template=(
        "Hook     : One sentence framing the case study — make it relevant to their world.\n"
        "Problem  : The challenge you or your client faced (1 sentence).\n"
        "Solution : What you built/did to solve it (1–2 sentences, skills used).\n"
        "Result   : The quantified outcome — numbers, percentages, time saved.\n"
        "Bridge   : Connect this directly to the company's context.\n"
        "CTA      : Offer to share more details or discuss how this applies to them."
    ),
    structure_hint=(
        "STRUCTURE — Case Study Pitch:\n"
        "1. Frame: Introduce a mini case study relevant to the company's domain in 1 sentence.\n"
        "2. Problem → Solution → Result: Present the 3-part story concisely — each part 1 sentence. "
        "   The result MUST include a number or measurable outcome.\n"
        "3. Company bridge: 'I believe a similar approach could benefit {company} because…'\n"
        "4. CTA: Offer to walk them through the full case study or discuss applicability.\n"
        "Tone: data-driven, credible, professional. Every sentence must justify its existence."
    ),
)

# ╔══════════════════════════════════════════════════════════╗
# ║  CATEGORY 4 — SALES                                     ║
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
        "then pivots to position your skills/service as the targeted solution. "
        "The most effective sales cold email structure for B2B and consulting outreach."
    ),
    use_cases=[
        "B2B service / SaaS sales outreach",
        "Freelancers pitching to companies with visible problems",
        "Consultants targeting a specific industry challenge",
        "Any situation where you know the company's pain point",
    ],
    example_opening="Most {company_focus} teams I talk to are losing hours every week to {pain_point} — and there's usually a faster way.",
    tone="persuasive",
    length="medium",
    word_range="100–160 words",
    body_template=(
        "Pain hook : Name a specific, realistic pain the target faces — be empathetic, not presumptuous.\n"
        "Pivot     : 'That's exactly the problem I help solve' — smooth transition.\n"
        "Solution  : 2 sentences: what you offer + how it specifically addresses the pain.\n"
        "Proof     : One result or credential that validates the claim.\n"
        "CTA       : Low-friction next step — a quick call, a demo, or a case study offer.\n"
        "Sign-off  : Confident, brief."
    ),
    structure_hint=(
        "STRUCTURE — Pain → Solution Sales:\n"
        "1. Pain hook: Open by naming a SPECIFIC, realistic pain related to the company's industry/focus. "
        "   Be empathetic — you're describing their problem, not selling at them yet.\n"
        "2. Pivot: Natural transition: 'That's exactly the problem I help [company type] solve.'\n"
        "3. Solution: What you offer and HOW it solves the named pain. Be specific, not vague.\n"
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
        "When you have impressive, verifiable past results",
        "Reaching out to large companies or known brands",
        "Competitive markets where credibility matters first",
        "When name-dropping a mutual client is appropriate",
    ],
    example_opening="We helped a company in {company_focus} cut operational costs by 35% in 90 days — here's how we did it.",
    tone="formal",
    length="medium",
    word_range="120–170 words",
    body_template=(
        "Proof opener : Lead with your strongest achievement or most relevant client result.\n"
        "Relevance    : Explain in 1 sentence why this result matters to the prospect.\n"
        "Offer        : Describe what you offer in 1–2 sentences — be specific.\n"
        "Fit          : Why does this company specifically benefit? Connect to their focus.\n"
        "CTA          : Offer a case study, call, or next step.\n"
        "Sign-off     : Professional close."
    ),
    structure_hint=(
        "STRUCTURE — Social Proof Sales:\n"
        "1. Proof opener: Lead with a quantified result or recognisable brand credential. "
        "   Use real numbers — '35% cost reduction', '10x faster deployment', etc.\n"
        "2. Relevance: 'Companies like {company} in {company_focus} face the same challenge…'\n"
        "3. Offer: What exactly you provide — be concrete, not 'I offer solutions'.\n"
        "4. Company fit: Directly reference their industry/focus and why your offer fits.\n"
        "5. CTA: Offer to share the full case study or schedule a call.\n"
        "Tone: formal, credible, professional. Let the numbers do the persuasion."
    ),
)

# ╔══════════════════════════════════════════════════════════╗
# ║  CATEGORY 5 — PARTNERSHIP                               ║
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
        "Leads with mutual benefit — what THEY gain — before explaining what you need. "
        "Essential framing: this is about them as much as about you."
    ),
    use_cases=[
        "Proposing a product integration or API partnership",
        "Agency / freelancer seeking a retainer collaboration",
        "Two complementary businesses exploring co-marketing",
        "Referral or affiliate partnership proposals",
    ],
    example_opening="I think there's a genuine opportunity for {company} and my team to create something that neither of us could build as well alone.",
    tone="conversational",
    length="medium",
    word_range="130–200 words",
    body_template=(
        "Hook       : Frame a shared opportunity — something both sides stand to gain.\n"
        "Their gain : What THEY get from this partnership (lead with their benefit, not yours).\n"
        "Your offer : What you bring to the table — skills, audience, technology, etc.\n"
        "Evidence   : A quick credential or past collaboration that shows you deliver.\n"
        "Fit reason : Why THIS specific company is the right partner.\n"
        "CTA        : Propose a discovery call or a concrete next step.\n"
        "Sign-off   : Warm but professional."
    ),
    structure_hint=(
        "STRUCTURE — Collaboration Partnership:\n"
        "1. Mutual opportunity hook: Open with the shared opportunity — what BOTH sides could gain. "
        "   Do NOT open with what YOU want.\n"
        "2. Their benefit: 1–2 sentences on what the company gains from this partnership specifically.\n"
        "3. Your contribution: What you bring — be concrete (skills, platform, audience, technology).\n"
        "4. Validation: One proof point showing you've successfully collaborated before.\n"
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
        "A concise proposal for a referral or affiliate arrangement — you'll send them clients, "
        "they send you clients (or vice versa). Works best when there's a clear complementary "
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
    length="short",
    word_range="80–120 words",
    body_template=(
        "Hook    : State the obvious overlap — 'Our clients need you, yours might need us.'\n"
        "Who you are: 1 sentence — what you do and who you serve.\n"
        "Overlap : Why the client bases are complementary.\n"
        "Proposal: Simple referral / affiliate structure idea (1 sentence).\n"
        "CTA     : 'Want to explore this over a quick call?'\n"
        "Sign-off: Casual, friendly."
    ),
    structure_hint=(
        "STRUCTURE — Referral / Affiliate Pitch:\n"
        "1. Hook: State the audience overlap immediately — make it obvious in the first sentence.\n"
        "2. Who you are: 1 sentence. Focus on WHO you serve, not what you do.\n"
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
    # Job Inquiry
    JOB_INQUIRY_DIRECT,
    JOB_INQUIRY_VALUE,
    # Networking
    NETWORKING_GENUINE,
    NETWORKING_INSIGHT,
    # Portfolio Share
    PORTFOLIO_SHOWCASE,
    PORTFOLIO_CASE_STUDY,
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
    "Job Inquiry",
    "Networking",
    "Portfolio Share",
    "Sales",
    "Partnership",
]

CATEGORY_ICONS: dict = {
    "Job Inquiry":     "💼",
    "Networking":      "🤝",
    "Portfolio Share": "🎨",
    "Sales":           "🎯",
    "Partnership":     "🚀",
}

def get_template(template_id: str) -> EmailTemplate:
    """Return a template by its ID, defaulting to JOB_INQUIRY_DIRECT if not found."""
    return TEMPLATES_BY_ID.get(template_id, JOB_INQUIRY_DIRECT)


def get_templates_by_category(category: str) -> List[EmailTemplate]:
    """Return all templates belonging to a given category."""
    return [t for t in ALL_TEMPLATES if t.category == category]
