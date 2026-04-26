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
