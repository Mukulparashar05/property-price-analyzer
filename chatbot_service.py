from __future__ import annotations

from ollama_chat import complete_chat_request
from predictor import predict_house_price


def generate_chatbot_response(
    user_message: str,
    history: list[dict[str, str]],
    client=None,
    model=None,
) -> tuple[str, float]:
    assistant_reply, completed_input = complete_chat_request(
        user_message=user_message,
        history=history,
        client=client,
    )
    price = predict_house_price(completed_input, model=model)
    final_reply = f"{assistant_reply}\n\n**Predicted price:** ${price:,.2f}"
    return final_reply, price
