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
