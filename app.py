from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import model  # Your existing model.py

app = Flask(__name__, static_folder="public")
CORS(app)

@app.route("/")
def home():
    return send_from_directory(app.static_folder, "index.html")

def get_health_recommendations(fever, dehydration, stress, flu, overall_health):
    result = {
        "Fever": "Yes" if fever == 1 else "No",
        "Dehydration": "Yes" if dehydration == 1 else "No",
        "Stress": "Yes" if stress == 1 else "No",
        "Flu": "Yes" if flu == 1 else "No",
        "OverallHealth": overall_health,
        "Recommendations": {}
    }

    if fever == 1:
        result["Recommendations"]["Fever"] = {
            "Food": ["Lukewarm soup", "Plenty of fluids", "Fresh fruits"],
            "TimeToCure": "3–5 days with proper rest and hydration.",
            "Cause": "Most commonly caused by viral infections such as cold or flu."
        }

    if dehydration == 1:
        result["Recommendations"]["Dehydration"] = {
            "Food": ["Electrolyte drinks", "Coconut water", "Watery fruits (e.g., watermelon, cucumber)"],
            "TimeToCure": "1–2 days with adequate fluid intake.",
            "Cause": "Insufficient water intake or excessive sweating."
        }

    if stress == 1:
        result["Recommendations"]["Stress"] = {
            "Food": ["Warm milk", "Bananas", "Dark chocolate", "Nuts"],
            "TimeToCure": "Varies depending on cause and support given.",
            "Cause": "Could be due to school pressure, lack of sleep, or poor diet."
        }

    if flu == 1:
        result["Recommendations"]["Flu"] = {
            "Food": ["Broth", "Herbal tea", "Ginger", "Garlic"],
            "TimeToCure": "Usually 5–7 days with adequate care.",
            "Cause": "Viral infection, often seasonal."
        }

    if overall_health == "Unhealthy":
        result["Recommendations"]["Overall"] = {
            "Advice": "Ensure regular meals, hydration, enough sleep, and physical activity."
        }

    return result

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        body_temp = float(data["BodyTemp"])
        heart_rate = int(data["HeartRate"])
        spo2 = float(data["SpO2"])
        activity = data["ActivityLevel"]
        sleep_hours = float(data["SleepHours"])
        activity_encoded = model.le_activity.transform([activity])[0]

        # Additional inputs (optional features)
        mood = data.get("Mood")
        concentration = data.get("Concentration")
        social_interaction = data.get("SocialInteraction")
        meals_skipped = int(data.get("MealsSkipped", 0))
        water_intake = int(data.get("WaterIntake", 0))
        appetite = data.get("Appetite")
        snacking = data.get("Snacking")
        night_awakenings = int(data.get("NightAwakenings", 0))
        trouble_sleep = data.get("TroubleSleep")
        hand_hygiene = data.get("HandHygiene")
        mask_use = data.get("MaskUse")
        outdoor_play = float(data.get("OutdoorPlay", 0))
        screen_time = float(data.get("ScreenTime", 0))
        fatigue = data.get("Fatigue")

        features = pd.DataFrame([[body_temp, heart_rate, spo2, activity_encoded, sleep_hours]],
                                columns=["BodyTemp", "HeartRate", "SpO2", "ActivityLevel", "SleepHours"])

        pred_fever = model.model_fever.predict(features)[0]
        pred_dehydration = model.model_dehydration.predict(features)[0]
        pred_stress = model.model_stress.predict(features)[0]
        pred_flu = model.model_flu.predict(features)[0]
        pred_overall = model.model_overall.predict(features)[0]
        overall_label = model.le_health.inverse_transform([pred_overall])[0]

        response = get_health_recommendations(
            fever=pred_fever,
            dehydration=pred_dehydration,
            stress=pred_stress,
            flu=pred_flu,
            overall_health=overall_label
        )

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
