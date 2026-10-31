"""Minutes generation: OpenAI GPT when configured; local heuristic fallback otherwise."""
from __future__ import annotations

import json
import re
from typing import Any

TASK_VERBS = re.compile(
    r"\b(i will|we will|will |needs? to |should |please |must |to-do:?|action:?|follow[- ]?up:?|responsible for )",
    re.I,
)
DECISION_MARKERS = re.compile(
    r"\b(decided|decision|agreed|approved|we will go with|let's go with|going with|target is|we'll use)\b",
    re.I,
)


def _sentences(text: str) -> list[str]:
    # Basic sentence split; preserve speaker labels and tolerate line-based transcripts.
    chunks = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [re.sub(r"\s+", " ", part).strip(" -\t") for part in chunks if part.strip(" -\t")]


def _offline_minutes(transcript: str, title: str) -> dict[str, Any]:
    sentences = _sentences(transcript)
    if not sentences:
        return {"summary": "No transcript text was provided.", "decisions": [], "action_items": [], "mode": "offline"}
    # Keep a short extractive overview. No unsupported facts are generated.
    summary = " ".join(sentences[:4])
    if len(summary) > 1100:
        summary = summary[:1097].rsplit(" ", 1)[0] + "…"
    decisions: list[str] = []
    actions: list[dict[str, str]] = []
    for sentence in sentences:
        clean = re.sub(r"^[A-Za-z][\w .'-]{0,30}:\s*", "", sentence)
        if DECISION_MARKERS.search(clean) and clean not in decisions:
            decisions.append(clean)
        if TASK_VERBS.search(sentence):
            owner_match = re.match(r"^([A-Z][A-Za-z .'-]{0,30}):\s*", sentence)
            owner = owner_match.group(1).strip() if owner_match else "Not specified"
            task = re.sub(r"^[A-Za-z][\w .'-]{0,30}:\s*", "", sentence)
            due_match = re.search(
                r"\b(by\s+[^,.!?;]+|this\s+(?:week|month)|next\s+\w+|first\s+week\s+of\s+next\s+month|tomorrow|today)\b",
                task,
                re.I,
            )
            due = due_match.group(0).strip() if due_match else "Not specified"
            if not any(a["task"] == task for a in actions):
                actions.append({"task": task, "owner": owner, "due": due})
    return {"summary": summary, "decisions": decisions[:10], "action_items": actions[:20], "mode": "offline"}


def _normalize(payload: Any, mode: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Minutes response was not a JSON object.")
    summary = str(payload.get("summary", "")).strip()
    decisions = payload.get("decisions", [])
    raw_actions = payload.get("action_items", [])
    if not isinstance(decisions, list) or not isinstance(raw_actions, list):
        raise ValueError("Minutes response contained invalid decisions or action items.")
    actions = []
    for item in raw_actions:
        if isinstance(item, dict):
            actions.append({k: str(item.get(k) or "Not specified") for k in ("task", "owner", "due")})
    return {"summary": summary, "decisions": [str(x) for x in decisions], "action_items": actions, "mode": mode}


def generate_minutes(
    transcript: str,
    api_key: str | None = None,
    model: str = "gpt-4o-mini",
    meeting_title: str = "Meeting Minutes",
) -> dict[str, Any]:
    """Generate structured minutes; fall back to local extraction if the API is unavailable."""
    if not transcript or not transcript.strip():
        raise ValueError("Transcript is empty.")
    if api_key:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key, timeout=45.0, max_retries=1)
            response = client.chat.completions.create(
                model=model,
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Create concise meeting minutes only from the supplied transcript. Do not invent facts. "
                            "Return JSON with keys summary (string), decisions (array of strings), action_items "
                            "(array of objects with task, owner, due). Use 'Not specified' when an owner or due date is absent."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Meeting title: {meeting_title}\n\nTranscript:\n{transcript[:80000]}",
                    },
                ],
            )
            content = response.choices[0].message.content
            return _normalize(json.loads(content or "{}"), "GPT")
        except Exception as exc:
            # Graceful fallback; disclose it to the UI.
            local = _offline_minutes(transcript, meeting_title)
            local["mode"] = f"offline fallback (GPT error: {type(exc).__name__})"
            return local
    return _offline_minutes(transcript, meeting_title)