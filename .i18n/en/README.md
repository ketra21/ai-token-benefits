<div align="center">

# 🤖 AI Token Benefits Index

### Which companies give employees free AI model tokens?

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](../../CONTRIBUTING.md)
[![Data Validation](https://img.shields.io/badge/data-validated-blue.svg)](#)
[![Companies](https://img.shields.io/badge/companies-15+-orange.svg)](#-leaderboard)

[中文](../../README.md) | **English**

**A crowdsourced, open-source index of AI token benefits offered by companies worldwide.**

---

*In the AI era, the models your company gives you access to says a lot about how much they invest in your productivity.*

</div>

---

### Why This Project?

As AI becomes essential for software development, research, and creative work, **access to frontier AI models** is becoming a key employee benefit — just like free lunch or gym memberships.

This project tracks which companies provide free AI model tokens to their employees, creating a transparent, community-driven ranking. It serves as:

- **For job seekers**: A signal of how AI-forward a company is
- **For employees**: Benchmarking your company's AI benefits against the industry
- **For companies**: Motivation to invest more in AI tools for their teams
- **For the industry**: A unique lens on AI adoption across sectors and regions

### How the Ranking Works

Each company receives an **AI Token Benefit Score (ATBS)** calculated by:

```
Score = Σ(Model_Weight × Quota_Multiplier × Access_Bonus) × Diversity_Bonus × Freshness
```

| Factor | Description |
|--------|-------------|
| **Model Weight** | Frontier models (Claude Opus, GPT-4.5) score higher than lightweight models |
| **Quota Multiplier** | Unlimited usage = 3x, High = 2x, Medium = 1.5x, Low = 1x |
| **Access Bonus** | API + Chat = 1.5x, API only = 1.3x, Chat only = 1x |
| **Diversity Bonus** | +10% for each additional AI provider (multi-vendor = better) |
| **Freshness** | Slight bonus for recently updated data |

**Tier System:**

| Tier | Score | Description |
|------|-------|-------------|
| 🏆 S | 120+ | World-class AI benefits |
| 🥇 A | 80-119 | Excellent AI benefits |
| 🥈 B | 50-79 | Good AI benefits |
| 🥉 C | 25-49 | Basic AI benefits |
| 📋 D | <25 | Minimal AI benefits |

### 🏆 Leaderboard

#### 🌍 Global Top 10

| Rank | Tier | Company | City | Models | Score |
|:---:|:---:|:--------|:-----|:-------|------:|
| 1 | 🏆 S | **Anthropic** | San Francisco | Claude Opus/Sonnet/Haiku (∞) | 165.0 |
| 2 | 🏆 S | **OpenAI** | San Francisco | GPT-4.5/4o (∞) | 127.3 |
| 3 | 🏆 S | **Google DeepMind** | Mountain View | Gemini Ultra/Pro (∞) | 127.3 |
| 4 | 🥇 A | **ByteDance** | Beijing | Doubao + GPT-4o + Claude | 105.6 |
| 5 | 🥇 A | **DeepSeek** | Hangzhou | DeepSeek R1/V3 (∞) | 94.3 |
| 6 | 🥈 B | **Stripe** | San Francisco | Claude Opus + GPT-4o | 79.5 |
| 7 | 🥈 B | **Meta** | Menlo Park | Llama (∞) + GPT-4o + Claude | 77.3 |
| 8 | 🥈 B | **Alibaba** | Hangzhou | Qwen Max (∞) + GPT-4o | 62.2 |
| 9 | 🥈 B | **Tencent** | Shenzhen | Hunyuan (∞) + GPT-4o | 62.2 |
| 10 | 🥈 B | **Moonshot AI** | Beijing | Moonshot (∞) + GPT-4o | 62.2 |

> 📊 [Full leaderboard →](../../docs/LEADERBOARD.md)

### 🙋 How to Contribute

**Your company gives you free AI tokens? Tell us about it!**

#### Option 1: GitHub Issue (Easiest)

1. Go to [Issues](../../issues/new?template=submit_company.yml)
2. Select "Submit Company AI Token Benefits"
3. Fill in the form
4. We'll review and add your data

#### Option 2: Pull Request

1. Fork this repository
2. Edit the appropriate data file:
   - China companies → `data/companies_cn.json`
   - International companies → `data/companies_intl.json`
3. Add your company entry following this format:

```json
{
  "company": "Company Name",
  "company_en": "English Name (if applicable)",
  "industry": "Industry",
  "city": "City",
  "country": "US",
  "size": "1000-5000",
  "models": [
    {
      "provider": "anthropic",
      "model": "claude-sonnet-4",
      "quota": "high",
      "type": "api+chat"
    }
  ],
  "verified": false,
  "submitted_by": "your_github_username",
  "submitted_at": "2026-03-18",
  "source": "employee_report",
  "notes": "Any additional context"
}
```

4. Run validation: `python scripts/validate.py`
5. Submit your pull request

All submissions are **anonymous by default**.

### Data Field Reference

| Field | Required | Description |
|-------|----------|-------------|
| company | ✅ | Company name |
| company_en | ❌ | English name (for CN companies) |
| industry | ✅ | Industry sector |
| city | ✅ | City |
| country | ✅ | ISO country code (CN, US, etc.) |
| size | ❌ | Company size range |
| models | ✅ | Array of model entries |
| models[].provider | ✅ | Model provider (openai, anthropic, etc.) |
| models[].model | ✅ | Model ID |
| models[].quota | ✅ | Token quota: unlimited, very_high, high, medium, low |
| models[].type | ✅ | Access type: api+chat, api, chat |
| verified | ❌ | Will be set by maintainers |
| submitted_by | ❌ | Your GitHub username |
| notes | ❌ | Additional context |

### Guidelines

- **Be honest**: Only submit information you can verify as a current/former employee
- **Stay anonymous**: You can use "anonymous" as submitted_by
- **No secrets**: Do not include any confidential or proprietary information
- **One company per entry**: Don't combine multiple office locations

### Project Structure

```
free_token/
├── data/
│   ├── companies_cn.json      # China company data
│   └── companies_intl.json    # International company data
├── ranking/
│   ├── algorithm.py           # ATBS ranking algorithm
│   └── models.py              # Model weights & config
├── scripts/
│   ├── generate_leaderboard.py  # Generate rankings
│   └── validate.py            # Validate submissions
├── docs/
│   └── LEADERBOARD.md         # Full leaderboard
├── .github/
│   ├── ISSUE_TEMPLATE/        # Submission template
│   └── workflows/             # CI validation
└── README.md
```

### Run Locally

```bash
# Validate data
python scripts/validate.py

# Generate leaderboard
python scripts/generate_leaderboard.py
```

No external dependencies required — pure Python 3.10+.

### Dimensions & Filters

| Dimension | Examples |
|-----------|----------|
| **Region** | China (CN), International |
| **Country** | US, CN, CA, GB, FR, JP, KR, SG... |
| **City** | Beijing, Shanghai, San Francisco, London... |
| **Industry** | Internet, AI, FinTech, E-Commerce... |
| **Company Size** | 1-50, 50-100, ..., 10000+ |
| **Model Provider** | OpenAI, Anthropic, Google, Zhipu, Baidu... |
| **Access Type** | API+Chat, API only, Chat only |

### Roadmap

- [x] Core ranking algorithm
- [x] Data validation pipeline
- [x] GitHub Issue submission template
- [x] CI/CD auto-validation
- [ ] Interactive web dashboard
- [ ] Historical trend tracking
- [ ] City-level heatmap visualization
- [ ] Industry breakdown analytics
- [ ] Monthly auto-generated reports
- [ ] API endpoint for programmatic access
- [ ] Integration with job platforms

---

## Disclaimer

All data is crowdsourced and self-reported. We cannot guarantee accuracy. This project is for informational purposes only and does not represent any company's official policy. Do not include any confidential information.

## License

[MIT](../../LICENSE) — Free to use, modify, and distribute.
