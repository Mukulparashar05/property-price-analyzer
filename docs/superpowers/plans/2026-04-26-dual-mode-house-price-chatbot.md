# Dual-Mode House Price Chatbot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a dual-mode Streamlit app where users can either predict with a manual form or use an Ollama-powered chatbot that silently completes missing model inputs before sending them into the existing scikit-learn price model.

**Architecture:** Extract the current single-file Streamlit app into a thin UI layer plus focused backend modules for validation, prediction, Ollama completion, and chat orchestration. Keep `model.pkl` as the only numeric prediction engine and use Ollama only to interpret free-form prompts and complete missing fields.

**Tech Stack:** Python 3.12, Streamlit 1.56.0, Ollama Python client 0.6.1, pandas, joblib, pytest, scikit-learn

---

## Planned File Structure

- `app.py`
  Streamlit UI only. Owns the manual/chat toggle, manual form rendering, chat history, and assistant output.

- `validation.py`
  Shared house-feature schema, deterministic hidden defaults, manual validation rules, and chat-payload repair logic.

- `predictor.py`
  Model loading and prediction from a full nine-field payload.

- `ollama_chat.py`
  Ollama prompt construction, JSON parsing, fenced-response cleanup, and conversion to a completed feature payload.

- `chatbot_service.py`
  Small orchestration layer that combines Ollama completion with ML prediction and formats the final assistant response.

- `tests/test_validation.py`
  Manual validation and hidden-autofill repair tests.

- `tests/test_predictor.py`
  Prediction helper tests with a stub model.

- `tests/test_ollama_chat.py`
  Ollama response parsing and error-handling tests with fake clients.

- `tests/test_chatbot_service.py`
  Integration test for assistant reply + predicted price formatting.

- `tests/test_requirements_file.py`
  Simple guard to keep the new chat dependencies pinned with valid requirement syntax.

- `ollama_test.py`
  Keep as the local smoke test for Python-to-Ollama connectivity.

## Shared Constants To Use

Use these deterministic hidden defaults inside `validation.py`:

```python
DEFAULT_FEATURES = {
    "longitude": -118.49,
    "latitude": 34.26,
    "housing_median_age": 29.0,
    "total_rooms": 2127.0,
    "total_bedrooms": 435.0,
    "population": 1166.0,
    "households": 409.0,
    "median_income": 3.5348,
    "ocean_proximity": "INLAND",
}

VALID_OCEAN_PROXIMITIES = [
    "INLAND",
    "NEAR BAY",
    "NEAR OCEAN",
    "ISLAND",
    "<1H OCEAN",
]

FEATURE_COLUMNS = [
    "longitude",
    "latitude",
    "housing_median_age",
    "total_rooms",
    "total_bedrooms",
    "population",
    "households",
    "median_income",
    "ocean_proximity",
]
```

### Task 1: Extract Validation and Prediction Core

**Files:**
- Create: `validation.py`
- Create: `predictor.py`
- Create: `tests/test_validation.py`
- Create: `tests/test_predictor.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_validation.py`:

```python
from validation import (
    DEFAULT_FEATURES,
    build_feature_payload,
    normalize_chat_features,
    validate_manual_features,
)


def test_validate_manual_features_reports_invalid_values():
    payload = build_feature_payload(
        longitude=-130.0,
        latitude=10.0,
        housing_median_age=20.0,
        total_rooms=0.0,
        total_bedrooms=3.0,
        population=0.0,
        households=4.0,
        median_income=25.0,
        ocean_proximity="MARS",
    )

    assert validate_manual_features(payload) == [
        "Longitude should be between -125 and -113",
        "Latitude should be between 32 and 42",
        "Total rooms must be greater than 0",
        "Bedrooms cannot be greater than total rooms",
        "Population must be greater than 0",
        "Households cannot exceed population",
        "Median income should be between 0 and 20",
        "Invalid ocean proximity value",
    ]


def test_normalize_chat_features_fills_missing_and_repairs_invalid_values():
    result = normalize_chat_features(
        {
            "latitude": 55,
            "housing_median_age": -2,
            "total_rooms": 0,
            "total_bedrooms": 3000,
            "population": 100,
            "households": 500,
            "median_income": -3,
            "ocean_proximity": "near ocean",
        }
    )

    assert result == {
        "longitude": DEFAULT_FEATURES["longitude"],
        "latitude": 42.0,
        "housing_median_age": DEFAULT_FEATURES["housing_median_age"],
        "total_rooms": DEFAULT_FEATURES["total_rooms"],
        "total_bedrooms": DEFAULT_FEATURES["total_rooms"],
        "population": 100.0,
        "households": 100.0,
        "median_income": DEFAULT_FEATURES["median_income"],
        "ocean_proximity": "NEAR OCEAN",
    }
```

Create `tests/test_predictor.py`:

```python
from predictor import predict_house_price
from validation import DEFAULT_FEATURES, FEATURE_COLUMNS


def test_predict_house_price_builds_expected_dataframe():
    captured = {}

    class DummyModel:
        def predict(self, frame):
            captured["columns"] = list(frame.columns)
            captured["first_row"] = frame.iloc[0].to_dict()
            return [321000.5]

    price = predict_house_price(DEFAULT_FEATURES, model=DummyModel())

    assert price == 321000.5
    assert captured["columns"] == FEATURE_COLUMNS
    assert captured["first_row"] == DEFAULT_FEATURES
```

- [ ] **Step 2: Run the tests to verify they fail**

Run:

```bash
./venv/bin/python -m pytest -q tests/test_validation.py tests/test_predictor.py
```

Expected:

```text
FAILED tests/test_validation.py::test_validate_manual_features_reports_invalid_values - ModuleNotFoundError: No module named 'validation'
FAILED tests/test_predictor.py::test_predict_house_price_builds_expected_dataframe - ModuleNotFoundError: No module named 'predictor'
```

- [ ] **Step 3: Write the minimal validation and prediction implementation**

Create `validation.py`:

```python
from __future__ import annotations

from typing import Any, TypedDict, cast


class HouseFeatures(TypedDict):
    longitude: float
    latitude: float
    housing_median_age: float
    total_rooms: float
    total_bedrooms: float
    population: float
    households: float
    median_income: float
    ocean_proximity: str


FEATURE_COLUMNS = [
    "longitude",
    "latitude",
    "housing_median_age",
    "total_rooms",
    "total_bedrooms",
    "population",
    "households",
    "median_income",
    "ocean_proximity",
]

VALID_OCEAN_PROXIMITIES = [
    "INLAND",
    "NEAR BAY",
    "NEAR OCEAN",
    "ISLAND",
    "<1H OCEAN",
]

DEFAULT_FEATURES: HouseFeatures = {
    "longitude": -118.49,
    "latitude": 34.26,
    "housing_median_age": 29.0,
    "total_rooms": 2127.0,
    "total_bedrooms": 435.0,
    "population": 1166.0,
    "households": 409.0,
    "median_income": 3.5348,
    "ocean_proximity": "INLAND",
}


def build_feature_payload(
    longitude: float,
    latitude: float,
    housing_median_age: float,
    total_rooms: float,
    total_bedrooms: float,
    population: float,
    households: float,
    median_income: float,
    ocean_proximity: str,
) -> HouseFeatures:
    return {
        "longitude": float(longitude),
        "latitude": float(latitude),
        "housing_median_age": float(housing_median_age),
        "total_rooms": float(total_rooms),
        "total_bedrooms": float(total_bedrooms),
        "population": float(population),
        "households": float(households),
        "median_income": float(median_income),
        "ocean_proximity": str(ocean_proximity),
    }


def validate_manual_features(features: HouseFeatures) -> list[str]:
    errors: list[str] = []

    if not (-125 <= features["longitude"] <= -113):
        errors.append("Longitude should be between -125 and -113")
    if not (32 <= features["latitude"] <= 42):
        errors.append("Latitude should be between 32 and 42")
    if features["total_rooms"] <= 0:
        errors.append("Total rooms must be greater than 0")
    if features["total_bedrooms"] < 0:
        errors.append("Total bedrooms cannot be negative")
    if features["total_bedrooms"] > features["total_rooms"]:
        errors.append("Bedrooms cannot be greater than total rooms")
    if features["population"] <= 0:
        errors.append("Population must be greater than 0")
    if features["households"] <= 0:
        errors.append("Households must be greater than 0")
    if features["households"] > features["population"]:
        errors.append("Households cannot exceed population")
    if not (0 < features["median_income"] <= 20):
        errors.append("Median income should be between 0 and 20")
    if features["ocean_proximity"] not in VALID_OCEAN_PROXIMITIES:
        errors.append("Invalid ocean proximity value")

    return errors


def _to_float(value: Any, fallback: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def normalize_chat_features(candidate: dict[str, Any]) -> HouseFeatures:
    result: dict[str, Any] = dict(DEFAULT_FEATURES)

    result["longitude"] = min(
        max(_to_float(candidate.get("longitude"), DEFAULT_FEATURES["longitude"]), -125.0),
        -113.0,
    )
    result["latitude"] = min(
        max(_to_float(candidate.get("latitude"), DEFAULT_FEATURES["latitude"]), 32.0),
        42.0,
    )

    housing_median_age = _to_float(
        candidate.get("housing_median_age"),
        DEFAULT_FEATURES["housing_median_age"],
    )
    result["housing_median_age"] = (
        housing_median_age
        if housing_median_age >= 0
        else DEFAULT_FEATURES["housing_median_age"]
    )

    total_rooms = _to_float(candidate.get("total_rooms"), DEFAULT_FEATURES["total_rooms"])
    if total_rooms <= 0:
        total_rooms = DEFAULT_FEATURES["total_rooms"]
    result["total_rooms"] = total_rooms

    total_bedrooms = _to_float(
        candidate.get("total_bedrooms"),
        DEFAULT_FEATURES["total_bedrooms"],
    )
    if total_bedrooms < 0:
        total_bedrooms = DEFAULT_FEATURES["total_bedrooms"]
    result["total_bedrooms"] = min(total_bedrooms, result["total_rooms"])

    population = _to_float(candidate.get("population"), DEFAULT_FEATURES["population"])
    if population <= 0:
        population = DEFAULT_FEATURES["population"]
    result["population"] = population

    households = _to_float(candidate.get("households"), DEFAULT_FEATURES["households"])
    if households <= 0:
        households = DEFAULT_FEATURES["households"]
    result["households"] = min(households, result["population"])

    median_income = _to_float(
        candidate.get("median_income"),
        DEFAULT_FEATURES["median_income"],
    )
    if not (0 < median_income <= 20):
        median_income = DEFAULT_FEATURES["median_income"]
    result["median_income"] = median_income

    ocean_proximity = str(
        candidate.get("ocean_proximity", DEFAULT_FEATURES["ocean_proximity"])
    ).upper()
    if ocean_proximity not in VALID_OCEAN_PROXIMITIES:
        ocean_proximity = DEFAULT_FEATURES["ocean_proximity"]
    result["ocean_proximity"] = ocean_proximity

    return cast(HouseFeatures, result)
```

Create `predictor.py`:

```python
from __future__ import annotations

from functools import lru_cache

import joblib
import pandas as pd

from validation import FEATURE_COLUMNS, HouseFeatures


@lru_cache(maxsize=1)
def load_model(model_path: str = "model.pkl"):
    return joblib.load(model_path)


def predict_house_price(features: HouseFeatures, model=None) -> float:
    active_model = model or load_model()
    frame = pd.DataFrame([[features[column] for column in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)
    return float(active_model.predict(frame)[0])
```

- [ ] **Step 4: Run the tests to verify they pass**

Run:

```bash
./venv/bin/python -m pytest -q tests/test_validation.py tests/test_predictor.py
```

Expected:

```text
3 passed
```

- [ ] **Step 5: Commit**

```bash
git add validation.py predictor.py tests/test_validation.py tests/test_predictor.py
git commit -m "refactor: extract validation and prediction core"
```

### Task 2: Add Ollama Completion Backend

**Files:**
- Create: `ollama_chat.py`
- Create: `tests/test_ollama_chat.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_ollama_chat.py`:

```python
import pytest

from ollama_chat import _strip_json_fence, complete_chat_request
from validation import DEFAULT_FEATURES


class FakeResponse:
    def __init__(self, response: str):
        self.response = response


class FakeClient:
    def __init__(self, response: str):
        self.response = response
        self.kwargs = {}

    def generate(self, **kwargs):
        self.kwargs = kwargs
        return FakeResponse(self.response)


def test_strip_json_fence_removes_markdown_wrapper():
    text = "```json\n{\"assistant_reply\": \"Hi\", \"completed_input\": {}}\n```"
    assert _strip_json_fence(text) == "{\"assistant_reply\": \"Hi\", \"completed_input\": {}}"


def test_complete_chat_request_parses_json_and_repairs_input():
    client = FakeClient(
        "{\"assistant_reply\": \"Try coastal Orange County.\", "
        "\"completed_input\": {\"latitude\": 55, \"population\": 900, "
        "\"households\": 1200, \"ocean_proximity\": \"near ocean\"}}"
    )

    reply, features = complete_chat_request(
        "Suggest me a good location",
        history=[{"role": "user", "content": "I want a family home"}],
        client=client,
    )

    assert reply == "Try coastal Orange County."
    assert features == {
        "longitude": DEFAULT_FEATURES["longitude"],
        "latitude": 42.0,
        "housing_median_age": DEFAULT_FEATURES["housing_median_age"],
        "total_rooms": DEFAULT_FEATURES["total_rooms"],
        "total_bedrooms": DEFAULT_FEATURES["total_bedrooms"],
        "population": 900.0,
        "households": 900.0,
        "median_income": DEFAULT_FEATURES["median_income"],
        "ocean_proximity": "NEAR OCEAN",
    }
    assert client.kwargs["format"] == "json"


def test_complete_chat_request_wraps_client_errors():
    class BrokenClient:
        def generate(self, **kwargs):
            raise OSError("connection refused")

    with pytest.raises(RuntimeError, match="Ollama chat completion failed"):
        complete_chat_request("hello", history=[], client=BrokenClient())
```

- [ ] **Step 2: Run the tests to verify they fail**

Run:

```bash
./venv/bin/python -m pytest -q tests/test_ollama_chat.py
```

Expected:

```text
FAILED tests/test_ollama_chat.py::test_strip_json_fence_removes_markdown_wrapper - ModuleNotFoundError: No module named 'ollama_chat'
FAILED tests/test_ollama_chat.py::test_complete_chat_request_parses_json_and_repairs_input - ModuleNotFoundError: No module named 'ollama_chat'
FAILED tests/test_ollama_chat.py::test_complete_chat_request_wraps_client_errors - ModuleNotFoundError: No module named 'ollama_chat'
```

- [ ] **Step 3: Write the minimal Ollama completion implementation**

Create `ollama_chat.py`:

```python
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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run:

```bash
./venv/bin/python -m pytest -q tests/test_ollama_chat.py
```

Expected:

```text
3 passed
```

- [ ] **Step 5: Commit**

```bash
git add ollama_chat.py tests/test_ollama_chat.py
git commit -m "feat: add ollama chat completion backend"
```

### Task 3: Build the Dual-Mode App Flow

**Files:**
- Create: `chatbot_service.py`
- Create: `tests/test_chatbot_service.py`
- Modify: `app.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_chatbot_service.py`:

```python
import chatbot_service

from validation import DEFAULT_FEATURES


def test_generate_chatbot_response_combines_reply_and_prediction(monkeypatch):
    monkeypatch.setattr(
        chatbot_service,
        "complete_chat_request",
        lambda user_message, history, client=None: (
            "Try inland suburbs for better value.",
            DEFAULT_FEATURES,
        ),
    )

    class DummyModel:
        def predict(self, frame):
            return [345678.9]

    reply, price = chatbot_service.generate_chatbot_response(
        "I want something affordable",
        history=[{"role": "user", "content": "hello"}],
        model=DummyModel(),
    )

    assert price == 345678.9
    assert "Try inland suburbs for better value." in reply
    assert "**Predicted price:** $345,678.90" in reply
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
./venv/bin/python -m pytest -q tests/test_chatbot_service.py
```

Expected:

```text
FAILED tests/test_chatbot_service.py::test_generate_chatbot_response_combines_reply_and_prediction - ModuleNotFoundError: No module named 'chatbot_service'
```

- [ ] **Step 3: Write the minimal chat orchestration and dual-mode UI**

Create `chatbot_service.py`:

```python
from __future__ import annotations

from ollama_chat import complete_chat_request
from predictor import predict_house_price


def generate_chatbot_response(user_message: str, history: list[dict[str, str]], client=None, model=None) -> tuple[str, float]:
    assistant_reply, completed_input = complete_chat_request(
        user_message=user_message,
        history=history,
        client=client,
    )
    price = predict_house_price(completed_input, model=model)
    final_reply = f"{assistant_reply}\n\n**Predicted price:** ${price:,.2f}"
    return final_reply, price
```

Replace `app.py` with:

```python
from __future__ import annotations

import streamlit as st

from chatbot_service import generate_chatbot_response
from predictor import predict_house_price
from validation import (
    DEFAULT_FEATURES,
    VALID_OCEAN_PROXIMITIES,
    build_feature_payload,
    validate_manual_features,
)


st.set_page_config(page_title="House Price Predictor", page_icon="🏠")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "latest_price" not in st.session_state:
    st.session_state.latest_price = None


def render_manual_mode() -> None:
    st.subheader("Manual prediction")

    with st.form("manual_prediction_form"):
        longitude = st.number_input(
            "Longitude",
            min_value=-125.0,
            max_value=-113.0,
            value=float(DEFAULT_FEATURES["longitude"]),
        )
        latitude = st.number_input(
            "Latitude",
            min_value=32.0,
            max_value=42.0,
            value=float(DEFAULT_FEATURES["latitude"]),
        )
        housing_median_age = st.number_input(
            "Housing Median Age",
            min_value=0.0,
            value=float(DEFAULT_FEATURES["housing_median_age"]),
        )
        total_rooms = st.number_input(
            "Total Rooms",
            min_value=1.0,
            value=float(DEFAULT_FEATURES["total_rooms"]),
        )
        total_bedrooms = st.number_input(
            "Total Bedrooms",
            min_value=0.0,
            value=float(DEFAULT_FEATURES["total_bedrooms"]),
        )
        population = st.number_input(
            "Population",
            min_value=1.0,
            value=float(DEFAULT_FEATURES["population"]),
        )
        households = st.number_input(
            "Households",
            min_value=1.0,
            value=float(DEFAULT_FEATURES["households"]),
        )
        median_income = st.number_input(
            "Median Income",
            min_value=0.01,
            max_value=20.0,
            value=float(DEFAULT_FEATURES["median_income"]),
        )
        ocean_proximity = st.selectbox(
            "Ocean Proximity",
            VALID_OCEAN_PROXIMITIES,
            index=VALID_OCEAN_PROXIMITIES.index(DEFAULT_FEATURES["ocean_proximity"]),
        )
        submitted = st.form_submit_button("Predict house price")

    if not submitted:
        return

    payload = build_feature_payload(
        longitude=longitude,
        latitude=latitude,
        housing_median_age=housing_median_age,
        total_rooms=total_rooms,
        total_bedrooms=total_bedrooms,
        population=population,
        households=households,
        median_income=median_income,
        ocean_proximity=ocean_proximity,
    )
    errors = validate_manual_features(payload)
    if errors:
        for error in errors:
            st.error(error)
        return

    price = predict_house_price(payload)
    st.session_state.latest_price = price
    st.success(f"💰 Predicted Price: ${price:,.2f}")


def render_chat_mode() -> None:
    st.subheader("Chat assistant")
    st.caption(
        "Ask about locations, budgets, or house preferences. Missing model inputs are completed automatically."
    )

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Describe the home or area you want")
    if not prompt:
        return

    prior_history = list(st.session_state.chat_history)
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                reply, price = generate_chatbot_response(prompt, history=prior_history)
                st.markdown(reply)
                st.session_state.latest_price = price
            except RuntimeError:
                reply = (
                    "I couldn't reach the local Ollama assistant just now. "
                    "Please make sure `ollama serve` is running, then try again."
                )
                st.error(reply)

    st.session_state.chat_history.append({"role": "assistant", "content": reply})


st.title("🏠 House Price Predictor")
mode = st.radio(
    "Choose input mode",
    ["Manual Mode", "Chat Mode"],
    horizontal=True,
    key="mode",
)

if mode == "Manual Mode":
    render_manual_mode()
else:
    render_chat_mode()
```

- [ ] **Step 4: Run the test and syntax check**

Run:

```bash
./venv/bin/python -m pytest -q tests/test_chatbot_service.py
./venv/bin/python -m py_compile app.py chatbot_service.py predictor.py validation.py ollama_chat.py
```

Expected:

```text
1 passed
```

and no output from `py_compile`.

- [ ] **Step 5: Commit**

```bash
git add app.py chatbot_service.py tests/test_chatbot_service.py
git commit -m "feat: add dual mode streamlit interface"
```

### Task 4: Pin Chat Dependencies and Verify End-to-End

**Files:**
- Create: `tests/test_requirements_file.py`
- Modify: `requirements.txt`

- [ ] **Step 1: Write the failing dependency guard test**

Create `tests/test_requirements_file.py`:

```python
from pathlib import Path


def test_requirements_pin_chat_dependencies():
    requirements_text = Path("requirements.txt").read_text()

    assert "ollama==0.6.1" in requirements_text
    assert "streamlit==1.56.0" in requirements_text
    assert "pytest==9.0.3" in requirements_text
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
./venv/bin/python -m pytest -q tests/test_requirements_file.py
```

Expected:

```text
FAILED tests/test_requirements_file.py::test_requirements_pin_chat_dependencies - AssertionError
```

- [ ] **Step 3: Fix the requirement pins**

Replace the malformed trailing dependency lines in `requirements.txt`:

```text
ollama 0.6.1
streamlit 1.56.0
pytest 9.0.3
```

with:

```text
ollama==0.6.1
streamlit==1.56.0
pytest==9.0.3
```

- [ ] **Step 4: Run the full verification suite**

Run:

```bash
./venv/bin/python -m pytest -q
./venv/bin/python -m py_compile app.py chatbot_service.py predictor.py validation.py ollama_chat.py
./venv/bin/python ollama_test.py
```

Expected:

```text
9 passed
```

then no output from `py_compile`, then a short Ollama greeting such as:

```text
Hello!
```

- [ ] **Step 5: Perform manual app verification**

Run:

```bash
./venv/bin/python -m streamlit run app.py
```

Verify in the browser:

```text
1. Manual Mode opens first and shows a form with median defaults.
2. Manual Mode predicts successfully after clicking "Predict house price".
3. Chat Mode shows previous chat messages and a chat input box.
4. A prompt like "I want a family house near the ocean" returns a conversational reply.
5. The chat reply includes a predicted price.
6. Missing fields remain hidden from the UI.
7. Stopping Ollama breaks only chat mode, while manual mode still works.
```

- [ ] **Step 6: Commit**

```bash
git add requirements.txt tests/test_requirements_file.py
git commit -m "chore: pin chat dependencies and verify app"
```

## Self-Review Checklist

- Spec coverage:
  - Dual mode UI is implemented in Task 3.
  - Hidden autofill defaults are implemented in Task 1 and Task 2.
  - Ollama parsing and recovery are implemented in Task 2.
  - Manual mode remains available in Task 3.
  - Requirements cleanup and smoke verification are covered in Task 4.

- Placeholder scan:
  - No placeholder markers or vague "handle it later" language remains.
  - Every file named in the plan has a concrete change or test attached to it.

- Type consistency:
  - `HouseFeatures` is the shared payload type across validation, predictor, Ollama completion, and chat orchestration.
  - `generate_chatbot_response()` returns `(reply, price)` consistently.
  - `complete_chat_request()` returns `(assistant_reply, completed_input)` consistently.
