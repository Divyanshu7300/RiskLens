from groq import Groq
import os
import json
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

ALLOWED_OPERATORS = {"=", "==", "!=", "<", ">", "<=", ">="}


def extract_rules_with_ai(
    text: str,
    schema: Dict[str, List[str]],
    model: str = "llama-3.3-70b-versatile",
    max_retries: int = 2
) -> List[Dict[str, Any]]:
    """
    Extract structured filter rules from policy text using Groq LLM.

    Returns:
        List of validated rule dictionaries.
        Returns empty list if extraction fails.
    """

    if not text or not text.strip():
        return []

    if not schema:
        return []

    schema_string = json.dumps(schema, indent=2, ensure_ascii=False)

    prompt = f"""
You are an expert at converting business compliance policies into database filter rules.

Database Schema (ONLY use tables & columns from here):
{schema_string}

Allowed operators (must use exactly these): {', '.join(sorted(ALLOWED_OPERATORS))}

STRICT OUTPUT RULES:
- Return ONLY a valid JSON array of objects.
- No explanations.
- No markdown.
- No ```json blocks.
- No extra text.
- Each object MUST contain EXACTLY:
    "table_name", "field", "operator", "value"
- Do NOT invent tables or columns not present in schema.
- If policy cannot be represented → return []

Policy text:
{text}

Example output format:
[
  {{
    "table_name": "users",
    "field": "age",
    "operator": ">",
    "value": 30
  }}
]
"""

    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=800,
                top_p=1.0,
            )

            content = response.choices[0].message.content.strip()

            # 🔥 Clean markdown fences aggressively
            if content.startswith("```"):
                parts = content.split("```")
                if len(parts) >= 2:
                    content = parts[1].strip()

            content = content.strip("` \n\r")

            # Try JSON parsing
            try:
                rules = json.loads(content)
            except json.JSONDecodeError:
                print(f"[Attempt {attempt+1}] Invalid JSON returned by LLM")
                print(content[:500])
                if attempt == max_retries:
                    return []
                continue

            if not isinstance(rules, list):
                print(f"[Attempt {attempt+1}] Output not list")
                if attempt == max_retries:
                    return []
                continue

            # 🔎 Strict Validation
            cleaned = []

            for rule in rules:
                if not isinstance(rule, dict):
                    continue

                table = rule.get("table_name")
                field = rule.get("field")
                operator = rule.get("operator")
                value = rule.get("value")

                if (
                    isinstance(table, str)
                    and table in schema
                    and isinstance(field, str)
                    and field in schema.get(table, [])
                    and isinstance(operator, str)
                    and operator in ALLOWED_OPERATORS
                ):
                    cleaned.append({
                        "table_name": table,
                        "field": field,
                        "operator": operator,
                        "value": value
                    })

            if cleaned:
                return cleaned

            print(f"[Attempt {attempt+1}] No valid rules after validation")

            if attempt == max_retries:
                return []

        except Exception as e:
            print(f"Groq error (attempt {attempt+1}): {type(e).__name__} - {e}")
            if attempt == max_retries:
                return []

    return []