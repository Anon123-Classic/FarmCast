import streamlit as st
import pandas as pd
import pickle

# ---------------- CONFIG ---------------- #
st.set_page_config(page_title="FarmCast", layout="wide")

# ---------------- TITLE ---------------- #
st.title("🌽 FarmCast System")

# ---------------- LOAD MODEL ---------------- #
model = pickle.load(open("model.pkl", "rb"))

# ---------------- INFO ---------------- #
st.info("Enter values based on your farm conditions")

# ---------------- INPUT SECTION ---------------- #
col1, col2 = st.columns(2)

with col1:
    rainfall = st.number_input("Rainfall (mm)", min_value=0.0, max_value=1000.0, value=None, placeholder="Enter the rainfall")
    temperature = st.number_input("Temperature (°C)", min_value=0.0, max_value=50.0, value=None, placeholder="Enter the temperature")
    days = st.number_input("Days to Harvest", min_value=30, max_value=200, value=None, placeholder="Enter the number of days")

with col2:
    fertilizer = st.selectbox("Fertilizer Used", ["Select", "No", "Yes"])
    irrigation = st.selectbox("Irrigation Used", ["Select", "No", "Yes"])
    region = st.selectbox("Region", ["Select", "North", "South", "West"])

soil = st.selectbox("Soil Type", ["Select", "Clay", "Loam", "Peaty", "Sandy", "Silt"])
crop = st.selectbox("Crop Type", ["Select", "Cotton", "Maize", "Rice", "Soybean", "Wheat"])
weather = st.selectbox("Weather Condition", ["Select", "Sunny", "Rainy"])

# ---------------- PREDICTION ---------------- #
if st.button("Predict Yield"):

    # -------- VALIDATION -------- #
    if (
        rainfall is None or
        temperature is None or
        days is None or
        fertilizer == "Select" or
        irrigation == "Select" or
        region == "Select" or
        soil == "Select" or
        crop == "Select" or
        weather == "Select"
    ):
        st.error("⚠️ Please fill in all fields before predicting")
        st.stop()

    # Convert Yes/No
    fertilizer_val = 1 if fertilizer == "Yes" else 0
    irrigation_val = 1 if irrigation == "Yes" else 0

    # Base features
    input_dict = {
        'Rainfall_mm': rainfall,
        'Temperature_Celsius': temperature,
        'Fertilizer_Used': fertilizer_val,
        'Irrigation_Used': irrigation_val,
        'Days_to_Harvest': days
    }

    # Initialize encoded features
    encoded_features = [
        'Region_North', 'Region_South', 'Region_West',
        'Soil_Type_Clay', 'Soil_Type_Loam', 'Soil_Type_Peaty',
        'Soil_Type_Sandy', 'Soil_Type_Silt',
        'Crop_Cotton', 'Crop_Maize', 'Crop_Rice',
        'Crop_Soybean', 'Crop_Wheat',
        'Weather_Condition_Rainy', 'Weather_Condition_Sunny'
    ]

    for feature in encoded_features:
        input_dict[feature] = 0

    # Set selected categories
    input_dict[f"Region_{region}"] = 1
    input_dict[f"Soil_Type_{soil}"] = 1
    input_dict[f"Crop_{crop}"] = 1
    input_dict[f"Weather_Condition_{weather}"] = 1

    # Convert to DataFrame
    input_df = pd.DataFrame([input_dict])

    # Predict
    prediction = model.predict(input_df)[0]

    # ---------------- OUTPUT ---------------- #
    st.header("📈 Prediction Results")

    st.success(f"🌾 Predicted Yield: {prediction:.2f} tons/hectare")

    # Status indicator
    if prediction > 6:
        st.success("🚀 Excellent yield expected")
    elif prediction > 3:
        st.info("📊 Moderate yield expected")
    else:
        st.error("⚠️ Low yield expected")

    # ---------------- INSIGHTS ---------------- #
    st.subheader("📊 Key Factors Affecting Yield")

    importance = model.feature_importances_
    importance_df = pd.DataFrame({
        'Feature': input_df.columns,
        'Importance': importance
    }).sort_values(by='Importance', ascending=False)

    st.bar_chart(importance_df.set_index('Feature').head(10))

    # ---------------- RECOMMENDATIONS ---------------- #
    st.subheader("🧠 Recommendations")

    if fertilizer_val == 0:
        st.warning("🌱 Adding fertilizer can significantly increase yield")

    if irrigation_val == 0 and rainfall < 300:
        st.warning("💧 Consider irrigation due to low rainfall")

    if temperature > 35:
        st.warning("🌡️ High temperature may stress crops")

    if prediction < 3:
        st.error("⚠️ Low yield predicted — improve farming practices")

# ---------------- FOOTER ---------------- #
st.markdown("---")
st.caption("FarmCast © 2026 — Predict. Plan. Prosper.")