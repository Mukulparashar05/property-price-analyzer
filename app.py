import streamlit as st
import joblib
import pandas as pd
import numpy as np

# Load model
model = joblib.load("model.pkl")

# Correct function
def predict_house_price(
    model,
    longitude: float,
    latitude: float,
    housing_median_age: float,
    total_rooms: float,
    total_bedrooms: float,
    population: float,
    households: float,
    median_income: float,
    ocean_proximity: str
) -> float:
    
    new_row = pd.DataFrame([{
        "longitude": longitude,
        "latitude": latitude,
        "housing_median_age": housing_median_age,
        "total_rooms": total_rooms,
        "total_bedrooms": total_bedrooms,
        "population": population,
        "households": households,
        "median_income": median_income,
        "ocean_proximity": ocean_proximity
    }])

    return float(model.predict(new_row)[0])


# UI
st.title("🏠 House Price Predictor")
longitude = st.number_input("Longitude", min_value=-125.0, max_value=-113.0)
latitude = st.number_input("Latitude")
housing_median_age = st.number_input("Housing Median Age")
total_rooms = st.number_input("Total Rooms")
total_bedrooms = st.number_input("Total Bedrooms")
population = st.number_input("Population")
households = st.number_input("Households")
median_income = st.number_input("Median Income", min_value=0.0, max_value=20.0)

ocean_proximity = st.selectbox(
    "Ocean Proximity",
    ["INLAND", "NEAR BAY", "NEAR OCEAN", "ISLAND", "<1H OCEAN"]
)

errors = []

# Longitude & Latitude (California dataset range approx)
if not (-125 <= longitude <= -113):
    errors.append("Longitude should be between -125 and -113")

if not (32 <= latitude <= 42):
    errors.append("Latitude should be between 32 and 42")

# Rooms & Bedrooms
if total_rooms <= 0:
    errors.append("Total rooms must be greater than 0")

if total_bedrooms < 0:
    errors.append("Total bedrooms cannot be negative")

if total_bedrooms > total_rooms:
    errors.append("Bedrooms cannot be greater than total rooms")

# Population & Households
if population <= 0:
    errors.append("Population must be greater than 0")

if households <= 0:
    errors.append("Households must be greater than 0")

if households > population:
    errors.append("Households cannot exceed population")

# Median Income (dataset is in tens of thousands approx)
if not (0 < median_income <= 20):
    errors.append("Median income should be between 0 and 20")

# Ocean Proximity check
valid_categories = ["INLAND", "NEAR BAY", "NEAR OCEAN", "ISLAND", "<1H OCEAN"]
if ocean_proximity not in valid_categories:
    errors.append("Invalid ocean proximity value")

# Final check
if errors:
    for error in errors:
        st.error(error)
else:
    price = predict_house_price(
        model=model,
        longitude=longitude,
        latitude=latitude,
        housing_median_age=housing_median_age,
        total_rooms=total_rooms,
        total_bedrooms=total_bedrooms,
        population=population,
        households=households,
        median_income=median_income,
        ocean_proximity=ocean_proximity
    )

    st.success(f"💰 Predicted Price: ${price:,.2f}")
    