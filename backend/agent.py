"""
Agent that converses with the user to produce a Bible reading plan spec.
Uses OpenAI chat completions; when the agent has enough info, it returns
a JSON plan spec that the backend turns into a Plan with PlanDays.
"""
import json
import re
from typing import Any

from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL
from schemas import AgentPlanSpec

SYSTEM_PROMPT = """You help users create personalized Bible reading plans. Your goal is to understand their theme and how many days they want, then output a structured plan.

Rules:
- Ask 1–2 short clarifying questions if you need more (e.g. theme focus, number of days, devotional vs study).
- Use only real Bible book names and references (e.g. John 3:16, Romans 8:1-17, Psalm 23).
- When you have enough information to create the plan, respond with ONLY a JSON code block and nothing else. No preamble or explanation outside the block.
- The JSON must have this exact shape:
  {"theme": "...", "duration_days": N, "references": ["Ref1", "Ref2", ...], "key_verses": ["Key1", "Key2", ...]}
  - theme: short title (e.g. "Peace", "Defending your faith")
  - duration_days: number of days (1–90)
  - references: array of Bible references, one per day. Length must equal duration_days. Use formats like "John 3:16", "Romans 8:1-17", "Psalm 23".
  - key_verses: optional array of one key verse per day (same length as references). Can be the same as the day's reference or a single verse from it.
- If the user has not specified duration, default to 7 days.
- Keep your questions brief and friendly. When outputting the plan, output only the JSON block."""


def _parse_spec_from_response(content: str) -> AgentPlanSpec | None:
    """Extract and parse a JSON plan spec from a markdown code block."""
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content.strip())
    if not match:
        return None
    raw = match.group(1).strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(data.get("references"), list) or len(data.get("references", [])) == 0:
        return None
    refs = [str(r).strip() for r in data["references"]]
    duration = int(data.get("duration_days", len(refs)))
    if len(refs) != duration:
        return None
    theme = str(data.get("theme", "")).strip() or "Bible reading plan"
    key_verses = data.get("key_verses")
    if key_verses is not None:
        if not isinstance(key_verses, list) or len(key_verses) != len(refs):
            key_verses = None
        else:
            key_verses = [str(k).strip() for k in key_verses]
    return AgentPlanSpec(
        theme=theme,
        duration_days=duration,
        references=refs,
        key_verses=key_verses,
    )


def run_agent(
    messages: list[dict[str, str]],
    theme_hint: str | None = None,
) -> dict[str, Any]:
    """
    Send conversation to the LLM and return either a follow-up message or a plan spec.

    Returns:
        {"action": "ask", "message": "..."}  or
        {"action": "create_plan", "message": "...", "plan_spec": AgentPlanSpec}
    """
    if not OPENAI_API_KEY:
        return {
            "action": "ask",
            "message": "Agent is not configured (missing OPENAI_API_KEY). Create a plan from the theme form instead.",
        }

    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt_messages: list[dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]
    if theme_hint:
        prompt_messages.append(
            {"role": "user", "content": f"[Initial context: user is interested in a plan about \"{theme_hint}\".]"}
        )
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        if role in ("user", "assistant") and content:
            prompt_messages.append({"role": role, "content": content})

    try:
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=prompt_messages,
            temperature=0.3,
        )
    except Exception as e:
        return {"action": "ask", "message": f"Sorry, I couldn't process that. ({e!s})"}

    content = (resp.choices[0].message.content or "").strip()
    spec = _parse_spec_from_response(content)
    if spec is not None:
        return {
            "action": "create_plan",
            "message": f"Here’s your {spec.duration_days}-day plan on “{spec.theme}.”",
            "plan_spec": spec,
        }
    return {"action": "ask", "message": content or "Could you tell me a bit more about what you’d like to focus on?"}
