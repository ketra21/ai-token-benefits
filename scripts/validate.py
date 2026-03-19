#!/usr/bin/env python3
"""
Validate company submission data against the schema.
Used in CI/CD to check pull requests.
"""

import json
import sys
from pathlib import Path

REQUIRED_FIELDS = ["company", "industry", "city", "country", "benefit_mode", "models"]
REQUIRED_MODEL_FIELDS = ["provider", "model", "quota", "type"]
VALID_QUOTAS = ["unlimited", "very_high", "high", "medium", "low"]
VALID_TYPES = ["api+chat", "api", "chat"]
VALID_COUNTRIES = [
    "CN", "US", "CA", "GB", "DE", "FR", "JP", "KR", "SG", "IN",
    "AU", "IL", "NL", "SE", "FI", "CH", "IE", "AE", "BR", "HK", "TW",
]
VALID_SIZES = ["1-50", "50-100", "100-500", "500-1000", "1000-5000", "5000-10000", "10000+"]
VALID_BENEFIT_MODES = ["all_employees", "tech_only", "reimbursement", "team_budget"]


def validate_company(company: dict, index: int) -> list[str]:
    """Validate a single company entry. Returns list of error messages."""
    errors = []
    prefix = f"Company #{index + 1} ({company.get('company', 'UNKNOWN')})"

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in company or not company[field]:
            errors.append(f"{prefix}: missing required field '{field}'")

    # Validate country
    country = company.get("country", "")
    if country and country not in VALID_COUNTRIES:
        errors.append(f"{prefix}: invalid country '{country}', must be one of {VALID_COUNTRIES}")

    # Validate benefit_mode
    benefit_mode = company.get("benefit_mode", "")
    if benefit_mode and benefit_mode not in VALID_BENEFIT_MODES:
        errors.append(f"{prefix}: invalid benefit_mode '{benefit_mode}', must be one of {VALID_BENEFIT_MODES}")

    # Validate size
    size = company.get("size", "")
    if size and size not in VALID_SIZES:
        errors.append(f"{prefix}: invalid size '{size}', must be one of {VALID_SIZES}")

    # Validate models
    models = company.get("models", [])
    if not models:
        errors.append(f"{prefix}: must have at least one model entry")

    for j, model in enumerate(models):
        model_prefix = f"{prefix} Model #{j + 1}"
        for field in REQUIRED_MODEL_FIELDS:
            if field not in model or not model[field]:
                errors.append(f"{model_prefix}: missing required field '{field}'")

        if model.get("quota") and model["quota"] not in VALID_QUOTAS:
            errors.append(f"{model_prefix}: invalid quota '{model['quota']}'")
        if model.get("type") and model["type"] not in VALID_TYPES:
            errors.append(f"{model_prefix}: invalid type '{model['type']}'")

    return errors


def validate_file(filepath: str) -> list[str]:
    """Validate a data file. Returns list of error messages."""
    errors = []
    path = Path(filepath)

    if not path.exists():
        return [f"File not found: {filepath}"]

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"Invalid JSON in {filepath}: {e}"]

    companies = []
    if isinstance(data, list):
        companies = data
    elif isinstance(data, dict) and "companies" in data:
        companies = data["companies"]
    else:
        return [f"Invalid format in {filepath}: expected list or dict with 'companies' key"]

    # Check for duplicate companies
    seen = set()
    for i, company in enumerate(companies):
        name = company.get("company", "")
        city = company.get("city", "")
        key = f"{name}|{city}"
        if key in seen:
            errors.append(f"Duplicate entry: {name} in {city}")
        seen.add(key)

        errors.extend(validate_company(company, i))

    return errors


def main():
    data_dir = Path(__file__).parent.parent / "data"
    all_errors = []

    json_files = list(data_dir.glob("*.json"))
    if not json_files:
        print("No data files found in data/ directory")
        sys.exit(1)

    for json_file in json_files:
        print(f"Validating {json_file.name}...")
        errors = validate_file(str(json_file))
        all_errors.extend(errors)

    if all_errors:
        print(f"\n❌ Found {len(all_errors)} error(s):\n")
        for error in all_errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print(f"\n✅ All {len(json_files)} file(s) validated successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
