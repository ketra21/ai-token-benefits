"""
Company Ranking Algorithm

Score = sum(model_weight × quota_multiplier × access_bonus) × benefit_mode_bonus × diversity_bonus × freshness_factor

Factors:
1. Model Value: Each AI model has an inherent weight based on capability
2. Quota Generosity: How many tokens the company provides
3. Access Type: API access is more valuable than chat-only
4. Benefit Mode: Company-wide > tech-only > team budget > reimbursement
5. Provider Diversity: Bonus for offering models from multiple providers
6. Freshness: Recent data is weighted slightly higher
"""

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import (
    ACCESS_TYPE_BONUS,
    BENEFIT_MODE_BONUS,
    DIVERSITY_STEP,
    MODEL_WEIGHTS,
    PROVIDER_STACK_FACTORS,
    QUOTA_MULTIPLIERS,
    get_model_weight,
)


def calculate_company_score(company: dict[str, Any]) -> float:
    """
    Calculate the AI Token Benefit Score (ATBS) for a company.

    Formula:
        model_value = model_weight × quota_multiplier × access_bonus × provider_stack_factor
        base_score = Σ model_value
        benefit_mode_bonus = BENEFIT_MODE_BONUS[benefit_mode]
        diversity_bonus = 1 + DIVERSITY_STEP × (num_unique_providers - 1)
        freshness = 1 + 0.05 × max(0, 1 - months_since_update / 12)
        final_score = base_score × benefit_mode_bonus × diversity_bonus × freshness
    """
    models = company.get("models", [])
    if not models:
        return 0.0

    # Calculate base score from each model. Additional models from the same
    # provider get diminishing credit so breadth does not overwhelm quality.
    base_score = 0.0
    providers = set()
    provider_counts: dict[str, int] = {}

    def raw_model_value(model_entry: dict[str, Any]) -> float:
        weight = get_model_weight(model_entry.get("model", ""))
        quota_mult = QUOTA_MULTIPLIERS.get(model_entry.get("quota", "low"), 1.0)
        access_mult = ACCESS_TYPE_BONUS.get(model_entry.get("type", "chat"), 1.0)
        return weight * quota_mult * access_mult

    for model_entry in sorted(models, key=raw_model_value, reverse=True):
        provider = model_entry.get("provider", "unknown").lower()
        stack_index = provider_counts.get(provider, 0)
        stack_factor = PROVIDER_STACK_FACTORS[
            min(stack_index, len(PROVIDER_STACK_FACTORS) - 1)
        ]

        base_score += raw_model_value(model_entry) * stack_factor
        providers.add(provider)
        provider_counts[provider] = stack_index + 1

    # Benefit mode bonus
    benefit_mode = company.get("benefit_mode", "tech_only")
    mode_bonus = BENEFIT_MODE_BONUS.get(benefit_mode, 1.0)

    # Provider diversity bonus: modest reward for true multi-provider coverage
    num_providers = len(providers)
    diversity_bonus = 1 + DIVERSITY_STEP * max(0, num_providers - 1)

    # Freshness factor based on last update
    freshness = 1.0
    updated_at = company.get("updated_at") or company.get("submitted_at")
    if updated_at:
        try:
            update_date = datetime.fromisoformat(updated_at).replace(
                tzinfo=timezone.utc
            )
            now = datetime.now(timezone.utc)
            months_old = (now - update_date).days / 30.0
            freshness = 1 + 0.05 * max(0, 1 - months_old / 12)
        except (ValueError, TypeError):
            pass

    final_score = base_score * mode_bonus * diversity_bonus * freshness
    return round(final_score, 2)


def rank_companies(companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rank companies by their AI Token Benefit Score."""
    scored = []
    for company in companies:
        score = calculate_company_score(company)
        scored.append({**company, "score": score})

    scored.sort(key=lambda x: x["score"], reverse=True)

    # Assign ranks (handle ties)
    for i, company in enumerate(scored):
        company["rank"] = i + 1

    return scored


def generate_tier(score: float) -> str:
    """Assign a tier label based on score."""
    if score >= 120:
        return "S"
    elif score >= 80:
        return "A"
    elif score >= 50:
        return "B"
    elif score >= 25:
        return "C"
    else:
        return "D"


def generate_leaderboard(
    data_dir: str = "data", output_dir: str = "docs"
) -> dict[str, Any]:
    """Generate leaderboard from all data files."""
    data_path = Path(data_dir)
    all_companies = []

    for json_file in data_path.glob("*.json"):
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                all_companies.extend(data)
            elif isinstance(data, dict) and "companies" in data:
                all_companies.extend(data["companies"])

    ranked = rank_companies(all_companies)

    # Add tier labels
    for company in ranked:
        company["tier"] = generate_tier(company["score"])

    # Split into regions
    cn_companies = [c for c in ranked if c.get("country") == "CN"]
    intl_companies = [c for c in ranked if c.get("country") != "CN"]

    # Re-rank within regions
    for i, c in enumerate(cn_companies):
        c["regional_rank"] = i + 1
    for i, c in enumerate(intl_companies):
        c["regional_rank"] = i + 1

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_companies": len(ranked),
        "global_ranking": ranked,
        "cn_ranking": cn_companies,
        "intl_ranking": intl_companies,
    }

    # Save leaderboard
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    with open(output_path / "leaderboard.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result
