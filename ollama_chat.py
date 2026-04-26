from __future__ import annotations

import json
import os
from typing import TypedDict

from ollama import Client

from validation import HouseFeatures, normalize_chat_features


class ChatTurn(TypedDict):
    role: str
    content: str


OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")


def _strip_json_fence(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()


def build_chat_prompt(user_message: str, history: list[ChatTurn]) -> str:
    recent_history = json.dumps(history[-6:], ensure_ascii=False)
    return f"""
You are a California housing assistant helping a house price predictor.

Return valid JSON only with this shape:
{{
  "assistant_reply": "short helpful natural-language answer",
  "completed_input": {{
    "longitude": number,
    "latitude": number,
    "housing_median_age": number,
    "total_rooms": number,
    "total_bedrooms": number,
    "population": number,
    "households": number,
    "median_income": number,
    "ocean_proximity": "INLAND | NEAR BAY | NEAR OCEAN | ISLAND | <1H OCEAN"
  }}
}}

Rules:
- Fill every field in completed_input.
- Use realistic California housing values.
- Keep assumptions hidden from the user.
- Do not expose completed_input values in assistant_reply.
- Do not mention guessed coordinates, incomes, room counts, or other filled values unless the user explicitly provided them.
- Do not mention assumptions, inferred defaults, or that you filled anything in behind the scenes.
- The user will only see assistant_reply.

Recent chat history:
{recent_history}

Latest user message:
{user_message}
""".strip()


def complete_chat_request(
    user_message: str,
    history: list[ChatTurn],
    client: Client | None = None,
    model_name: str = OLLAMA_MODEL,
) -> tuple[str, HouseFeatures]:
    active_client = client or Client(host=OLLAMA_HOST)

    try:
        response = active_client.generate(
            model=model_name,
            prompt=build_chat_prompt(user_message, history),
            format="json",
        )
        payload = json.loads(_strip_json_fence(response.response))
        assistant_reply = payload.get(
            "assistant_reply",
            "Here is a price estimate based on your request.",
        )
        completed_input = normalize_chat_features(payload.get("completed_input", {}))
        return assistant_reply, completed_input
    except Exception as exc:
        raise RuntimeError("Ollama chat completion failed") from exc
