"""
AI Model Definitions and Weight Configuration

Each model is assigned a weight based on:
- Capability tier (reasoning, coding, creative ability)
- Market pricing (as a proxy for computational cost)
- Scarcity and exclusivity
"""

# Model weight tiers - higher weight = more valuable benefit
MODEL_WEIGHTS = {
    # === Tier S (weight 15) - Frontier models, most expensive ===
    "claude-opus-4": 15,
    "claude-opus-4-6": 15,
    "gpt-4.5": 15,
    "gemini-ultra-2": 15,

    # === Tier A (weight 12) - Flagship models ===
    "claude-sonnet-4": 12,
    "claude-sonnet-4-6": 12,
    "gpt-4o": 12,
    "gemini-2.5-pro": 12,
    "gpt-4-turbo": 12,
    "deepseek-r1": 12,

    # === Tier B (weight 8) - Strong mid-tier models ===
    "claude-haiku-4": 8,
    "gpt-4o-mini": 8,
    "gemini-2.0-flash": 8,
    "glm-4": 8,
    "qwen-max": 8,
    "doubao-pro": 8,
    "ernie-4.0": 8,
    "moonshot-v1-128k": 8,
    "step-2": 8,
    "yi-large": 8,
    "minimax-abab6.5": 8,
    "deepseek-v3": 8,
    "hunyuan-pro": 8,

    # === Tier C (weight 5) - Lightweight / older models ===
    "claude-haiku-3.5": 5,
    "gpt-3.5-turbo": 5,
    "gemini-1.5-flash": 5,
    "glm-3-turbo": 5,
    "qwen-turbo": 5,
    "doubao-lite": 5,
    "ernie-3.5": 5,
    "moonshot-v1-8k": 5,
    "yi-medium": 5,
    "deepseek-chat": 5,
    "hunyuan-standard": 5,

    # === Tier D (weight 3) - Open source self-hosted ===
    "llama-3.1-405b": 3,
    "llama-3.1-70b": 3,
    "qwen-2.5-72b": 3,
    "mixtral-8x22b": 3,
    "yi-34b": 3,
}

# Quota multipliers
QUOTA_MULTIPLIERS = {
    "unlimited": 3.0,
    "very_high": 2.5,    # > 10M tokens/month
    "high": 2.0,         # 1M - 10M tokens/month
    "medium": 1.5,       # 100K - 1M tokens/month
    "low": 1.0,          # < 100K tokens/month
}

# Access type bonus
ACCESS_TYPE_BONUS = {
    "api+chat": 1.5,     # Both API and chat access
    "api": 1.3,          # API access only
    "chat": 1.0,         # Chat interface only
}

# Benefit mode bonus - how the benefit is provided
BENEFIT_MODE_BONUS = {
    "all_employees": 1.2,    # Company-wide, best signal
    "tech_only": 1.0,        # Tech/engineering only
    "team_budget": 0.8,      # Team budget, needs approval
    "reimbursement": 0.6,    # Self-purchase then reimburse
}

# Provider diversity thresholds
PROVIDER_NAMES = {
    "anthropic": "Anthropic",
    "openai": "OpenAI",
    "google": "Google",
    "zhipu": "Zhipu AI (智谱)",
    "baidu": "Baidu (百度)",
    "alibaba": "Alibaba (阿里巴巴)",
    "bytedance": "ByteDance (字节跳动)",
    "moonshot": "Moonshot AI (月之暗面)",
    "stepfun": "StepFun (阶跃星辰)",
    "01ai": "01.AI (零一万物)",
    "minimax": "MiniMax",
    "deepseek": "DeepSeek (深度求索)",
    "tencent": "Tencent (腾讯)",
    "meta": "Meta",
    "mistral": "Mistral AI",
}


def get_model_weight(model_id: str) -> int:
    """Get the weight for a model, with fuzzy matching fallback."""
    if model_id in MODEL_WEIGHTS:
        return MODEL_WEIGHTS[model_id]

    model_lower = model_id.lower()
    for known_model, weight in MODEL_WEIGHTS.items():
        if known_model in model_lower or model_lower in known_model:
            return weight

    return 3  # Default weight for unknown models
