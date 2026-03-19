#!/usr/bin/env python3
"""
Evaluate the scoring method with reproducible sensitivity tests.

This script does not change the ranking algorithm. It exercises the current
formula against a small battery of tests and prints a concise report.
"""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ranking.algorithm import calculate_company_score, rank_companies
from ranking.models import (
    ACCESS_TYPE_BONUS,
    BENEFIT_MODE_BONUS,
    DIVERSITY_STEP,
    PROVIDER_STACK_FACTORS,
    QUOTA_MULTIPLIERS,
    get_model_weight,
)


def load_companies(data_dir: str = "data") -> list[dict[str, Any]]:
    companies: list[dict[str, Any]] = []
    for json_file in Path(data_dir).glob("*.json"):
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            companies.extend(data)
        elif isinstance(data, dict) and "companies" in data:
            companies.extend(data["companies"])
    return companies


def variant_score(
    company: dict[str, Any],
    *,
    diversity_step: float = DIVERSITY_STEP,
    unlimited_mult: float = QUOTA_MULTIPLIERS["unlimited"],
    access_api_chat: float = ACCESS_TYPE_BONUS["api+chat"],
    access_api: float = ACCESS_TYPE_BONUS["api"],
    use_mode_bonus: bool = True,
    use_freshness: bool = True,
    stack_factors: list[float] | None = None,
) -> float:
    quota_map = dict(QUOTA_MULTIPLIERS)
    access_map = {
        "api+chat": access_api_chat,
        "api": access_api,
        "chat": 1.0,
    }
    stack_factors = stack_factors or PROVIDER_STACK_FACTORS

    base_score = 0.0
    providers = set()
    provider_counts: dict[str, int] = {}

    models = list(company.get("models", []))
    models.sort(
        key=lambda model: (
            get_model_weight(model.get("model", ""))
            * (unlimited_mult if model.get("quota") == "unlimited" else quota_map[model.get("quota", "low")])
            * access_map[model.get("type", "chat")]
        ),
        reverse=True,
    )

    for model in models:
        quota = model.get("quota", "low")
        quota_mult = unlimited_mult if quota == "unlimited" else quota_map[quota]
        raw_value = (
            get_model_weight(model.get("model", ""))
            * quota_mult
            * access_map[model.get("type", "chat")]
        )
        provider = model.get("provider", "").lower()
        stack_index = provider_counts.get(provider, 0)
        stack_factor = stack_factors[min(stack_index, len(stack_factors) - 1)]
        base_score += raw_value * stack_factor
        providers.add(provider)
        provider_counts[provider] = stack_index + 1

    final_score = base_score
    if use_mode_bonus:
        final_score *= BENEFIT_MODE_BONUS.get(company.get("benefit_mode"), 1.0)
    final_score *= 1 + diversity_step * max(0, len(providers) - 1)

    # Keep freshness simple for stable comparisons across variants.
    if use_freshness:
        final_score *= 1.05

    return round(final_score, 2)


def print_top_rankings(companies: list[dict[str, Any]]) -> None:
    print("== Current Top 10 ==")
    for company in rank_companies(companies)[:10]:
        print(f'{company["rank"]:>2}. {company["company"]:<18} {company["score"]:>7}')
    print()


def print_monotonicity_test() -> None:
    print("== Monotonicity Test: one GPT-4.5 benefit ==")
    base = {
        "company": "Case",
        "benefit_mode": "tech_only",
        "submitted_at": "2026-03-19",
        "models": [
            {
                "provider": "openai",
                "model": "gpt-4.5",
                "quota": "low",
                "type": "chat",
            }
        ],
    }
    for quota in ["low", "medium", "high", "very_high", "unlimited"]:
        row = []
        for access_type in ["chat", "api", "api+chat"]:
            item = deepcopy(base)
            item["models"][0]["quota"] = quota
            item["models"][0]["type"] = access_type
            row.append(f"{access_type}={calculate_company_score(item):.2f}")
        print(f"{quota:<10} " + "  ".join(row))
    print()


def print_tradeoff_test() -> None:
    print("== Tradeoff Test: model quality vs quota/access ==")
    cases = {
        "frontier-medium-chat": {
            "provider": "openai",
            "model": "gpt-4.5",
            "quota": "medium",
            "type": "chat",
        },
        "frontier-low-api+chat": {
            "provider": "openai",
            "model": "gpt-4.5",
            "quota": "low",
            "type": "api+chat",
        },
        "mid-unlimited-chat": {
            "provider": "alibaba",
            "model": "qwen-max",
            "quota": "unlimited",
            "type": "chat",
        },
        "mid-unlimited-api+chat": {
            "provider": "alibaba",
            "model": "qwen-max",
            "quota": "unlimited",
            "type": "api+chat",
        },
    }
    for name, model in cases.items():
        company = {
            "company": name,
            "benefit_mode": "tech_only",
            "submitted_at": "2026-03-19",
            "models": [model],
        }
        print(f"{name:<24} {calculate_company_score(company):>7.2f}")
    print()


def print_scenario_test() -> None:
    print("== Scenario Test: concentration vs breadth ==")
    scenarios = {
        "single frontier unlimited": [
            {
                "provider": "openai",
                "model": "gpt-4.5",
                "quota": "unlimited",
                "type": "api+chat",
            }
        ],
        "two flagships high": [
            {
                "provider": "openai",
                "model": "gpt-4o",
                "quota": "high",
                "type": "chat",
            },
            {
                "provider": "anthropic",
                "model": "claude-sonnet-4",
                "quota": "high",
                "type": "chat",
            },
        ],
        "three mids unlimited multi-provider": [
            {
                "provider": "alibaba",
                "model": "qwen-max",
                "quota": "unlimited",
                "type": "api+chat",
            },
            {
                "provider": "deepseek",
                "model": "deepseek-v3",
                "quota": "unlimited",
                "type": "api+chat",
            },
            {
                "provider": "zhipu",
                "model": "glm-4",
                "quota": "unlimited",
                "type": "api+chat",
            },
        ],
        "same provider triple stack": [
            {
                "provider": "anthropic",
                "model": "claude-opus-4",
                "quota": "unlimited",
                "type": "api+chat",
            },
            {
                "provider": "anthropic",
                "model": "claude-sonnet-4",
                "quota": "unlimited",
                "type": "api+chat",
            },
            {
                "provider": "anthropic",
                "model": "claude-haiku-4",
                "quota": "unlimited",
                "type": "api+chat",
            },
        ],
    }
    for name, models in scenarios.items():
        company = {
            "company": name,
            "benefit_mode": "all_employees",
            "submitted_at": "2026-03-19",
            "models": models,
        }
        print(f"{name:<34} {calculate_company_score(company):>7.2f}")
    print()


def print_variant_rankings(companies: list[dict[str, Any]]) -> None:
    print("== Sensitivity Test: top 8 under variant settings ==")
    variants = [
        ("current_v2", {}),
        ("legacy_v1", {"diversity_step": 0.1, "unlimited_mult": 3.0, "stack_factors": [1.0]}),
        ("no_diversity", {"diversity_step": 0.0}),
        ("unlimited_3.0x", {"unlimited_mult": 3.0}),
        ("no_stack_decay", {"stack_factors": [1.0]}),
        ("no_mode_no_freshness", {"use_mode_bonus": False, "use_freshness": False}),
    ]
    for variant_name, kwargs in variants:
        ranked = sorted(
            (
                {
                    "company": company["company"],
                    "score": variant_score(company, **kwargs),
                }
                for company in companies
            ),
            key=lambda item: item["score"],
            reverse=True,
        )
        print(f"[{variant_name}]")
        for i, item in enumerate(ranked[:8], start=1):
            print(f'{i:>2}. {item["company"]:<18} {item["score"]:>7.2f}')
        print()


def main() -> None:
    companies = load_companies()
    print_top_rankings(companies)
    print_monotonicity_test()
    print_tradeoff_test()
    print_scenario_test()
    print_variant_rankings(companies)


if __name__ == "__main__":
    main()
