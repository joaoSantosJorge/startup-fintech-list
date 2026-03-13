from config import NICHE_CATEGORIES

NICHE_LIST = ", ".join(NICHE_CATEGORIES)

EVALUATION_SYSTEM_PROMPT = """\
You are a fintech market analyst. You evaluate startup ideas using the "10 Ways to Evaluate a Market" framework. You always respond with valid JSON only, no markdown."""

EVALUATION_USER_PROMPT = """\
Evaluate this YC fintech startup as a market opportunity for someone looking to build a similar product:

**{name}**
- One-liner: {one_liner}
- Description: {long_description}
- Subindustry: {subindustry}
- Tags: {tags}
- Status: {status}
- Stage: {stage}
- Team size: {team_size}

Score each dimension 1-10 (10 = best for a new entrant):

1. **Urgency**: How urgently do customers need this? (10 = hair-on-fire problem)
2. **Market Size**: How large is the addressable market? (10 = massive TAM)
3. **Pricing Potential**: Can this command premium pricing? (10 = high willingness to pay)
4. **Acquisition Cost**: How easy/cheap to acquire customers? (10 = very easy/cheap)
5. **Delivery Cost**: How cheaply can the product be delivered? (10 = near-zero marginal cost)
6. **Uniqueness**: How differentiated is this from competitors? (10 = very unique)
7. **Speed to Market**: How quickly could a new entrant ship an MVP? (10 = very fast)
8. **Upfront Investment**: How little capital is needed to start? (10 = minimal investment needed)
9. **Upsell Potential**: Can you expand revenue per customer over time? (10 = strong expansion)
10. **Evergreen Potential**: Will this market exist in 10+ years? (10 = permanent need)

Also provide:
- **Replicability** (1-10): How feasible is it for a small team to replicate this idea?
- **Niche Category**: Choose exactly one from: {niche_list}
- **Reasoning**: 2-3 sentences explaining the scores.

Respond ONLY with this JSON (no markdown, no extra text):
{{
  "urgency": <int>,
  "market_size": <int>,
  "pricing_potential": <int>,
  "acquisition_cost": <int>,
  "delivery_cost": <int>,
  "uniqueness": <int>,
  "speed_to_market": <int>,
  "upfront_investment": <int>,
  "upsell_potential": <int>,
  "evergreen_potential": <int>,
  "replicability": <int>,
  "niche_category": "<string>",
  "reasoning": "<string>"
}}"""


def build_evaluation_prompt(company: dict) -> str:
    return EVALUATION_USER_PROMPT.format(
        name=company.get("name", "Unknown"),
        one_liner=company.get("one_liner", "N/A"),
        long_description=company.get("long_description", "N/A"),
        subindustry=company.get("subindustry", "N/A"),
        tags=company.get("tags", "N/A"),
        status=company.get("status", "N/A"),
        stage=company.get("stage", "N/A"),
        team_size=company.get("team_size", "N/A"),
        niche_list=NICHE_LIST,
    )
