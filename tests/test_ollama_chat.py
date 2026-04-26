import pytest

from ollama_chat import _strip_json_fence, build_chat_prompt, complete_chat_request
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


def test_build_chat_prompt_requires_hidden_assumptions():
    prompt = build_chat_prompt(
        "Suggest me a good location",
        history=[{"role": "user", "content": "I want a family home"}],
    )

    assert "Do not expose completed_input values" in prompt
    assert "Do not mention guessed coordinates" in prompt
    assert "Do not mention assumptions" in prompt


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
