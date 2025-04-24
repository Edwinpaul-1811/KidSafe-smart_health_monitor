from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
import pandas as pd
import os

app = Flask(__name__, static_folder="public")
CORS(app)

# Load models
model_path = "model"
model_fever = joblib.load(os.path.join(model_path, "model_fever.pkl"))
model_dehydration = joblib.load(os.path.join(model_path, "model_dehydration.pkl"))
model_stress = joblib.load(os.path.join(model_path, "model_stress.pkl"))
model_flu = joblib.load(os.path.join(model_path, "model_flu.pkl"))
model_overall = joblib.load(os.path.join(model_path, "model_overall.pkl"))

# Load encoders
le_health = joblib.load(os.path.join(model_path, "le_health.pkl"))
le_activity = joblib.load(os.path.join(model_path, "le_activity.pkl"))

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        # Basic required features
        body_temp = float(data["BodyTemp"])
        heart_rate = int(data["HeartRate"])
        spo2 = float(data["SpO2"])
        activity = data["ActivityLevel"]
        sleep_hours = float(data["SleepHours"])
        activity_encoded = le_activity.transform([activity])[0]

        # NEW FIELDS: received as string/numeric
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

        # Log for now (you can save this to DB or CSV later)
        print("Extra inputs received:")
        print({
            "Mood": mood,
            "Concentration": concentration,
            "SocialInteraction": social_interaction,
            "MealsSkipped": meals_skipped,
            "WaterIntake": water_intake,
            "Appetite": appetite,
            "Snacking": snacking,
            "NightAwakenings": night_awakenings,
            "TroubleSleep": trouble_sleep,
            "HandHygiene": hand_hygiene,
            "MaskUse": mask_use,
            "OutdoorPlay": outdoor_play,
            "ScreenTime": screen_time,
            "Fatigue": fatigue
        })

        # Feature set for current model
        feature_columns = ["BodyTemp", "HeartRate", "SpO2", "ActivityLevel", "SleepHours"]
        features = pd.DataFrame([[body_temp, heart_rate, spo2, activity_encoded, sleep_hours]],
                                columns=feature_columns)

        # Predictions
        pred_fever = model_fever.predict(features)[0]
        pred_dehydration = model_dehydration.predict(features)[0]
        pred_stress = model_stress.predict(features)[0]
        pred_flu = model_flu.predict(features)[0]
        pred_overall = model_overall.predict(features)[0]
        overall_label = le_health.inverse_transform([pred_overall])[0]

        return jsonify({
            "Fever": "Yes" if pred_fever == 1 else "No",
            "Dehydration": "Yes" if pred_dehydration == 1 else "No",
            "Stress": "Yes" if pred_stress == 1 else "No",
            "Flu": "Yes" if pred_flu == 1 else "No",
            "OverallHealth": overall_label
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
