from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
import pandas as pd
import os

app = Flask(__name__, static_folder="public")
CORS(app)

# Path to models
model_path = "model"

# Load models
model_fever = joblib.load(os.path.join(model_path, "model_fever.pkl"))
model_dehydration = joblib.load(os.path.join(model_path, "model_dehydration.pkl"))
model_stress = joblib.load(os.path.join(model_path, "model_stress.pkl"))
model_overall = joblib.load(os.path.join(model_path, "model_overall.pkl"))
model_flu = joblib.load(os.path.join(model_path, "model_flu.pkl"))  # ✅ New

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

        # Extract inputs
        body_temp = float(data["BodyTemp"])
        heart_rate = int(data["HeartRate"])
        spo2 = float(data["SpO2"])
        activity = data["ActivityLevel"]
        sleep_hours = float(data["SleepHours"])

        # Encode activity level
        activity_encoded = le_activity.transform([activity])[0]

        # Create feature DataFrame
        feature_columns = ["BodyTemp", "HeartRate", "SpO2", "ActivityLevel", "SleepHours"]
        features = pd.DataFrame([[body_temp, heart_rate, spo2, activity_encoded, sleep_hours]],
                                columns=feature_columns)

        # Predict health risks
        pred_fever = model_fever.predict(features)[0]
        pred_dehydration = model_dehydration.predict(features)[0]
        pred_stress = model_stress.predict(features)[0]
        pred_flu = model_flu.predict(features)[0]  # ✅ New
        pred_overall = model_overall.predict(features)[0]
        overall_label = le_health.inverse_transform([pred_overall])[0]

        return jsonify({
            "Fever": "Yes" if pred_fever == 1 else "No",
            "Dehydration": "Yes" if pred_dehydration == 1 else "No",
            "Stress": "Yes" if pred_stress == 1 else "No",
            "Flu": "Yes" if pred_flu == 1 else "No",  # ✅ New
            "OverallHealth": overall_label
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
