#!/usr/bin/env python3
"""
Generate leaderboard rankings and output markdown tables.
"""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ranking.algorithm import generate_leaderboard, generate_tier


TIER_EMOJI = {"S": "🏆", "A": "🥇", "B": "🥈", "C": "🥉", "D": "📋"}
TIER_COLORS = {"S": "ff0000", "A": "ff8c00", "B": "ffd700", "C": "4169e1", "D": "808080"}


def format_models_brief(models: list) -> str:
    """Format model list for table display."""
    names = []
    for m in models:
        quota_icon = "∞" if m.get("quota") == "unlimited" else "●"
        names.append(f"{m['model']}({quota_icon})")
    return ", ".join(names[:3]) + ("..." if len(names) > 3 else "")


def generate_markdown_table(companies: list, title: str, lang: str = "en") -> str:
    """Generate a markdown ranking table."""
    lines = []
    lines.append(f"## {title}\n")

    if lang == "cn":
        lines.append("| 排名 | 等级 | 公司 | 行业 | 城市 | 模型福利 | 得分 |")
        lines.append("|:---:|:---:|:-----|:-----|:-----|:---------|-----:|")
    else:
        lines.append("| Rank | Tier | Company | Industry | City | Model Benefits | Score |")
        lines.append("|:---:|:---:|:--------|:---------|:-----|:---------------|------:|")

    for c in companies:
        tier = c.get("tier", generate_tier(c.get("score", 0)))
        emoji = TIER_EMOJI.get(tier, "")
        rank = c.get("regional_rank", c.get("rank", "-"))
        company_name = c.get("company", "Unknown")
        if lang == "en" and c.get("company_en"):
            company_name = c["company_en"]
        industry = c.get("industry", "-")
        city = c.get("city", "-")
        models_str = format_models_brief(c.get("models", []))
        score = c.get("score", 0)

        lines.append(
            f"| {rank} | {emoji} {tier} | **{company_name}** | {industry} | {city} | {models_str} | {score} |"
        )

    lines.append("")
    return "\n".join(lines)


def generate_stats(result: dict) -> str:
    """Generate statistics summary."""
    total = result["total_companies"]
    cn = len(result["cn_ranking"])
    intl = len(result["intl_ranking"])

    # Count tiers
    tiers = {}
    for c in result["global_ranking"]:
        t = c.get("tier", "D")
        tiers[t] = tiers.get(t, 0) + 1

    lines = [
        f"- Total companies tracked: **{total}**",
        f"- China: **{cn}** | International: **{intl}**",
        f"- Tier distribution: " + " | ".join(
            f"{TIER_EMOJI.get(t, '')} {t}: {tiers.get(t, 0)}" for t in ["S", "A", "B", "C", "D"]
        ),
    ]
    return "\n".join(lines)


def generate_formula_summary() -> str:
    """Generate a short formula summary for the leaderboard page."""
    lines = [
        "Scoring formula:",
        "`score = Σ(model_weight × quota_multiplier × access_bonus × provider_stack_factor) × benefit_mode_bonus × diversity_bonus × freshness`",
        "",
        "- `unlimited = 2.5x`",
        "- same-provider stack factors: `100% / 70% / 40%`",
        "- diversity bonus: `+5%` per additional provider",
    ]
    return "\n".join(lines)


def main():
    project_root = Path(__file__).parent.parent
    data_dir = str(project_root / "data")
    output_dir = str(project_root / "docs")

    print("Generating leaderboard...")
    result = generate_leaderboard(data_dir, output_dir)

    print(f"Total companies: {result['total_companies']}")
    print(f"CN companies: {len(result['cn_ranking'])}")
    print(f"INTL companies: {len(result['intl_ranking'])}")

    # Generate markdown
    md_lines = ["# AI Token Benefits Leaderboard\n"]
    md_lines.append(f"*Last updated: {result['generated_at'][:10]}*\n")
    md_lines.append(generate_formula_summary())
    md_lines.append("")
    md_lines.append(generate_stats(result))
    md_lines.append("")

    md_lines.append(generate_markdown_table(
        result["global_ranking"], "🌍 Global Ranking / 全球排名", "en"
    ))
    md_lines.append(generate_markdown_table(
        result["cn_ranking"], "🇨🇳 China Ranking / 中国排名", "cn"
    ))
    md_lines.append(generate_markdown_table(
        result["intl_ranking"], "🌎 International Ranking / 国际排名", "en"
    ))

    output_path = Path(output_dir) / "LEADERBOARD.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"Leaderboard saved to {output_path}")

    # Also print to console
    print("\n" + "=" * 60)
    print("\n".join(md_lines))


if __name__ == "__main__":
    main()
