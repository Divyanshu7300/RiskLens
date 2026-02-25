from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


def generate_remediation(message: str) -> str:
    """
    Generate concise remediation steps using Groq.
    Stable + cost-safe version.
    """

    if client is None:
        return _fallback_remediation()

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",  # fast + powerful
            messages=[
                {
                    "role": "system",
                    "content": "You are a strict compliance assistant."
                },
                {
                    "role": "user",
                    "content": f"""
Violation:
"{message}"

Provide ONLY 2-3 concise remediation steps.
Plain text only.
No markdown.
"""
                }
            ],
            temperature=0.2,
            max_tokens=150
        )

        text = response.choices[0].message.content.strip()

        if not text or len(text) < 10:
            return _fallback_remediation()

        return text

    except Exception as e:
        print("Groq Remediation Error:", e)
        return _fallback_remediation()


def _fallback_remediation():
    return (
        "1. Review the affected record.\n"
        "2. Correct the field to meet policy requirements.\n"
        "3. Re-run compliance scan."
    )