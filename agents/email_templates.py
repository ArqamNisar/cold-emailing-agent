"""
Email Templates — Template Library
====================================
Each template describes an *email approach style*.

Frontend  : uses `id`, `name`, `icon`, `tagline`, `description`, `example_opening`
LLM prompt: uses `structure_hint` — a concise structural skeleton injected into
            the email writer agent's system prompt.
"""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class EmailTemplate:
    id: str
    name: str
    icon: str
    tagline: str
    description: str
    example_opening: str
    structure_hint: str   # injected verbatim into the LLM system prompt


# ---------------------------------------------------------------------------
# Template Definitions
# ---------------------------------------------------------------------------

VALUE_PROP = EmailTemplate(
    id="value_prop",
    name="Value Proposition",
    icon="💎",
    tagline="Lead with what you uniquely bring to the table",
    description=(
        "Open by immediately stating the concrete value you deliver. "
        "No small talk — the first sentence answers 'why should I care?'. "
        "Best for confident, senior candidates targeting growth-stage companies."
    ),
    example_opening="I help engineering teams ship faster by cutting infra costs — here's how I'd do that for you.",
    structure_hint=(
        "STRUCTURE — Value Proposition approach:\n"
        "1. Opening line: State your single strongest value claim in one crisp sentence. "
        "   Make it specific and benefit-oriented (not just a job title).\n"
        "2. Evidence sentence: Back the claim with one concrete achievement or number.\n"
        "3. Relevance bridge: Directly connect your value to the company's known focus or challenge.\n"
        "4. Soft CTA: End with a low-friction ask (e.g. a 10-minute call).\n"
        "Do NOT use generic openers like 'I hope this email finds you well.'"
    ),
)

PAIN_POINT = EmailTemplate(
    id="pain_point",
    name="Problem → Solution",
    icon="🎯",
    tagline="Open with a pain point, position yourself as the fix",
    description=(
        "Start by naming a real challenge the company likely faces based on their industry "
        "and focus. Then pivot smoothly to position yourself as the solution. "
        "High-impact for B2B outreach and competitive hiring markets."
    ),
    example_opening="Scaling AI infrastructure while controlling cloud spend is a brutal trade-off — one I've solved before.",
    structure_hint=(
        "STRUCTURE — Problem → Solution approach:\n"
        "1. Pain hook: Open by naming a specific, realistic pain the company faces "
        "   (derived from their industry and focus). Be empathetic, not presumptuous.\n"
        "2. Pivot: Transition with a phrase like 'That's exactly where I come in' or 'I've solved this before'.\n"
        "3. Solution proof: One or two sentences showing HOW your skills address that pain.\n"
        "4. Invitation: Invite them to learn more with a friendly, no-pressure CTA.\n"
        "Do NOT open with pleasantries. Lead with the pain point immediately."
    ),
)

SOCIAL_PROOF = EmailTemplate(
    id="social_proof",
    name="Social Proof",
    icon="🏆",
    tagline="Build credibility fast with accomplishments & numbers",
    description=(
        "Lead with a striking achievement, metric, or brand name that establishes "
        "instant credibility. Numbers and recognisable names do the heavy lifting. "
        "Great for candidates with impressive portfolios or prior company experience."
    ),
    example_opening="At my last role, I reduced deployment time by 60% — and I'd love to bring that same impact to your team.",
    structure_hint=(
        "STRUCTURE — Social Proof approach:\n"
        "1. Achievement opener: Start with a quantified accomplishment or a recognisable "
        "   brand/technology you've worked with. Use real numbers where possible.\n"
        "2. Relevance link: In one sentence, explain why that achievement is directly "
        "   applicable to this company's goals or the target role.\n"
        "3. Credibility amplifier: Add one more supporting proof point (a skill, tool, "
        "   or outcome that matches their focus).\n"
        "4. CTA: Request a brief call or ask a question that invites engagement.\n"
        "Avoid generic phrases. Every sentence must reinforce credibility."
    ),
)

CURIOSITY_HOOK = EmailTemplate(
    id="curiosity_hook",
    name="Curiosity Hook",
    icon="🤔",
    tagline="Pique interest with a bold question or surprising insight",
    description=(
        "Open with a thought-provoking question or a counterintuitive observation "
        "that makes the reader pause. Creates intrigue and compels them to read on. "
        "Works especially well for creative roles and innovative companies."
    ),
    example_opening="What if your next machine-learning hire could also cut your AWS bill by 30%?",
    structure_hint=(
        "STRUCTURE — Curiosity Hook approach:\n"
        "1. Hook: Begin with a bold, relevant question OR a surprising/counterintuitive "
        "   insight related to the company's industry or the role. Make it specific — "
        "   not clickbait. The reader should think 'hm, tell me more'.\n"
        "2. Answer/reveal: In 1–2 sentences, answer or explain the hook, naturally "
        "   weaving in your skills as the reason you can deliver.\n"
        "3. Relevance: Briefly tie your experience to their specific context.\n"
        "4. Light CTA: End with an easy next step or a second curiosity-triggering question.\n"
        "The tone should feel fresh, smart, and slightly unexpected — never salesy."
    ),
)

WARM_REFERRAL = EmailTemplate(
    id="warm_referral",
    name="Warm Referral",
    icon="🤝",
    tagline="Leverage shared context or common ground to build rapport",
    description=(
        "Create an immediate sense of familiarity by referencing shared context — "
        "the company's public work, a recent achievement, or industry common ground. "
        "Makes the email feel personal rather than mass-blasted."
    ),
    example_opening="I've been following your team's work on real-time fraud detection — the system you published last quarter is genuinely impressive.",
    structure_hint=(
        "STRUCTURE — Warm Referral / Common Ground approach:\n"
        "1. Personal opening: Reference something specific and genuine about the company — "
        "   a product, a blog post, a recent milestone, or their stated mission. "
        "   This MUST feel researched, not generic.\n"
        "2. Bridge: Transition naturally from their work to why you're reaching out.\n"
        "3. Fit statement: In 1–2 sentences explain how your background aligns with "
        "   what they're building, using their own language where possible.\n"
        "4. CTA: Keep the ask warm and conversational (e.g. 'Would love to swap notes' "
        "   or 'Open to a quick chat?').\n"
        "The email should feel like it was written specifically for this person, not templated."
    ),
)

DIRECT_ASK = EmailTemplate(
    id="direct_ask",
    name="Direct & Concise",
    icon="⚡",
    tagline="No fluff — get straight to the point in under 80 words",
    description=(
        "Busy hiring managers appreciate brevity. This approach strips every word "
        "to its essence: who you are, what you do, why them, what you want. "
        "Ideal for senior executives, technical leads, and startup founders."
    ),
    example_opening="I'm a backend engineer with 5 years in distributed systems. I want to work at your company. Here's why it makes sense.",
    structure_hint=(
        "STRUCTURE — Direct & Concise approach:\n"
        "1. Identity line: One sentence — who you are and your core expertise.\n"
        "2. Why them: One sentence — a specific, genuine reason you want THIS company.\n"
        "3. Value fit: One sentence — the single most relevant thing you bring.\n"
        "4. CTA: One sentence — clear, direct ask (call, reply, review profile).\n"
        "CRITICAL: The entire email body MUST be under 80 words. Every word must earn its place. "
        "No filler, no pleasantries, no fluff. Bullet points are acceptable if they save words."
    ),
)


# ---------------------------------------------------------------------------
# Exported registry — ordered for display in the UI
# ---------------------------------------------------------------------------

ALL_TEMPLATES: List[EmailTemplate] = [
    VALUE_PROP,
    PAIN_POINT,
    SOCIAL_PROOF,
    CURIOSITY_HOOK,
    WARM_REFERRAL,
    DIRECT_ASK,
]

TEMPLATES_BY_ID: dict = {t.id: t for t in ALL_TEMPLATES}


def get_template(template_id: str) -> EmailTemplate:
    """Return a template by its ID, defaulting to VALUE_PROP if not found."""
    return TEMPLATES_BY_ID.get(template_id, VALUE_PROP)
