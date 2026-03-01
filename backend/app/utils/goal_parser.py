import re
from datetime import date
from decimal import Decimal
from typing import Any, Dict, Optional


def _parse_amount(text: str) -> Optional[Decimal]:
    """Extract a dollar amount from text, e.g. $12,000 or 12000 or 12k."""
    # $1,234.56 or $1234 or 1234.56 or 12k
    text = text.replace(",", "")
    m = re.search(r"\$?\s*(\d+(?:\.\d{1,2})?)\s*k\b", text, re.I)
    if m:
        return Decimal(m.group(1)) * 1000
    m = re.search(r"\$?\s*(\d+(?:\.\d{1,2})?)", text)
    if m:
        return Decimal(m.group(1))
    return None


def _parse_date(text: str) -> Optional[date]:
    """Extract a date from text, e.g. August 2026, 2026-08-31, end of 2026, next year."""
    text = text.strip().lower()
    today = date.today()

    # ISO-style: 2026-08-31 or 2026/08/31
    m = re.search(r"\b(20\d{2})[-/](\d{1,2})[-/](\d{1,2})\b", text)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass

    # "August 2026", "Aug 2026", "8/2026"
    months = {
        "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
        "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
        "august": 8, "aug": 8, "september": 9, "sep": 9, "sept": 9,
        "october": 10, "oct": 10, "november": 11, "nov": 11, "december": 12, "dec": 12,
    }
    m = re.search(r"\b(" + "|".join(months.keys()) + r")\s+(20\d{2})\b", text)
    if m:
        try:
            return date(int(m.group(2)), months[m.group(1)], 1)
        except (ValueError, KeyError):
            pass
    m = re.search(r"\b(\d{1,2})[-/](20\d{2})\b", text)
    if m:
        try:
            return date(int(m.group(2)), int(m.group(1)), 1)
        except ValueError:
            pass

    # "end of 2026", "by 2026"
    m = re.search(r"(?:end of|by|in)\s+(20\d{2})\b", text)
    if m:
        return date(int(m.group(1)), 12, 31)
    m = re.search(r"\b(20\d{2})\b", text)
    if m:
        y = int(m.group(1))
        if y >= today.year:
            return date(y, 12, 31)

    # "next year"
    if "next year" in text:
        return date(today.year + 1, 12, 31)
    if "this year" in text:
        return date(today.year, 12, 31)

    return None


def parse_goal_from_message(message: str) -> Dict[str, Any]:
    """
    Extract goal-related numbers from a message.
    Returns dict with target_amount, deadline, current_savings, monthly_surplus (None if not found).
    """
    if not message or not message.strip():
        return {}
    text = message.strip()
    result: Dict[str, Any] = {}

    amount = _parse_amount(text)
    if amount is not None and amount > 0:
        result["target_amount"] = amount

    d = _parse_date(text)
    if d is not None:
        result["deadline"] = d

    # Optional: "I have $X saved" / "current savings 2000"
    for pattern in [
        r"(?:I have|current savings?|saved)\s*\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:saved|already)?",
        r"(?:savings?|saved)\s*[:=]\s*\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)",
    ]:
        m = re.search(pattern, text, re.I)
        if m:
            result["current_savings"] = Decimal(m.group(1).replace(",", ""))
            break

    # Optional: "monthly surplus 500" / "I can save $300 per month" (must have "per month" or "monthly" to avoid matching main goal amount)
    for pattern in [
        r"(?:monthly surplus|surplus)\s*\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:per month|/month|monthly)?",
        r"(?:can save|save)\s*\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:per month|/month|monthly)\b",
        r"\$?\s*(\d+)\s*(?:per month|/month|monthly)\b",
    ]:
        m = re.search(pattern, text, re.I)
        if m:
            result["monthly_surplus"] = Decimal(m.group(1).replace(",", ""))
            break

    return result
