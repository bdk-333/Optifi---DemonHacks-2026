import os
from typing import Any, Dict, List, Optional

INTENT_LABELS = [
    "budget",
    "goal",
    "loan",
    "tax",
    "weekly_review",
    "purchase_optimize",
    "card_import",
    "general",
]


def _classify_with_ollama(message: str) -> str:
    """Use local Ollama API to classify intent. No API key required."""
    base_url = (os.environ.get("OLLAMA_BASE_URL") or "http://localhost:11434").strip().rstrip("/")
    model = (os.environ.get("OLLAMA_MODEL") or "llama3.2").strip()
    labels_str = "|".join(INTENT_LABELS)
    system = f"Output exactly one word from this list, nothing else: {labels_str}"
    try:
        import httpx
        with httpx.Client(timeout=30.0) as client:
            r = client.post(
                f"{base_url}/api/chat",
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": message},
                    ],
                    "stream": False,
                },
            )
            r.raise_for_status()
            data = r.json()
            raw = (data.get("message") or {}).get("content") or ""
            raw = raw.strip().lower()
            for label in INTENT_LABELS:
                if label in raw or raw == label:
                    return label
            return "general"
    except Exception:
        return "general"


def _classify_with_openai(message: str) -> str:
    """Use OpenAI to classify intent (optional, when API key is set)."""
    api_key = (os.environ.get("OPENAI_API_KEY") or "").strip()
    if not api_key:
        return "general"
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        labels_str = "|".join(INTENT_LABELS)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Output exactly one label from this list, nothing else: {labels_str}"},
                {"role": "user", "content": message},
            ],
            max_tokens=20,
        )
        raw = (response.choices[0].message.content or "").strip().lower()
        for label in INTENT_LABELS:
            if label in raw or raw == label:
                return label
        return "general"
    except Exception:
        return "general"


def classify_intent(message: str) -> str:
    """
    Classify user message into a single intent label.
    Uses Ollama (local) by default. Set OPENAI_API_KEY to use OpenAI instead.
    """
    if (os.environ.get("OPENAI_API_KEY") or "").strip():
        return _classify_with_openai(message)
    return _classify_with_ollama(message)


def review_goal_plan(
    months_remaining: int,
    target_amount: str,
    current_savings: str,
    monthly_required: str,
    feasible: bool,
    recommendation_summary: str,
) -> Optional[Dict[str, Any]]:
    """
    Ask the LLM for an intelligent review: short summary, analysis, and 2-3 next steps.
    Uses only the numbers we pass (no math by the LLM). Returns None if LLM unavailable.
    """
    user_content = f"""These are the computed numbers for a savings goal (do not recalculate, use them as fact):
- Months remaining: {months_remaining}
- Target amount: {target_amount}
- Current savings: {current_savings}
- Monthly required: {monthly_required}
- Feasible with current surplus: {feasible}
- Recommendations from system: {recommendation_summary or "None"}

Respond in exactly this JSON format, no other text:
{{"summary": "One sentence summary for the user.", "analysis": "One or two sentences of analysis.", "next_questions": ["First suggested next question.", "Second question."]}}
"""
    base_url = (os.environ.get("OLLAMA_BASE_URL") or "http://localhost:11434").strip().rstrip("/")
    model = (os.environ.get("OLLAMA_MODEL") or "llama3.1").strip()
    try:
        import json
        import httpx
        with httpx.Client(timeout=45.0) as client:
            r = client.post(
                f"{base_url}/api/chat",
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are a helpful financial assistant. Output only valid JSON."},
                        {"role": "user", "content": user_content},
                    ],
                    "stream": False,
                },
            )
            r.raise_for_status()
            raw = (r.json().get("message") or {}).get("content") or ""
            # Extract JSON from response (in case there's markdown or extra text)
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(raw[start:end])
                if isinstance(data.get("next_questions"), list):
                    return data
                return {
                    "summary": data.get("summary") or "",
                    "analysis": data.get("analysis") or "",
                    "next_questions": data.get("next_questions") or [],
                }
            return None
    except Exception:
        return None


if __name__ == "__main__":
    print(classify_intent("I want to save $1000 by next month"))