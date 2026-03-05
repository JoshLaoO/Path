"""
Client for bible-api.com. Fetches verse text by reference (e.g. "John 3:16").
No API key required. Rate limit: 15 requests per 30 seconds per IP.
"""
import json
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://bible-api.com"
DEFAULT_TRANSLATION = "web"


def fetch_verse(
    reference: str,
    translation: str = DEFAULT_TRANSLATION,
) -> str:
    """
    Fetch verse(s) from bible-api.com by reference.

    Args:
        reference: e.g. "John 3:16", "Philippians 4:7", "Psalm 23:1"
        translation: bible-api.com translation id (web, kjv, asv, etc.)

    Returns:
        Combined verse text, or "{reference} (text unavailable)" on error.
    """
    path = reference.strip()
    if not path:
        return "(no reference)"
    url = f"{BASE_URL}/{urllib.parse.quote(path)}?translation={translation}"
    req = urllib.request.Request(url, headers={"User-Agent": "Path-Backend/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError):
        return f"{reference} (text unavailable)"

    text = data.get("text", "").strip()
    if not text:
        return f"{reference} (text unavailable)"
    ref = data.get("reference", reference)
    return f"{ref} — {text}" if ref else text
