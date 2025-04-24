from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd

app = Flask(__name__)
CORS(app)

# Load models
model_fever = joblib.load("model_fever.pkl")
model_dehydration = joblib.load("model_dehydration.pkl")
model_stress = joblib.load("model_stress.pkl")
model_overall = joblib.load("model_overall.pkl")

# Load label encoders
le_health = joblib.load("le_health.pkl")
le_activity = joblib.load("le_activity.pkl")

@app.route("/")
def home():
    return "<h2>Smart Health Monitoring API is running 🩺</h2>"

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        # Extract user inputs
        body_temp = float(data["BodyTemp"])
        heart_rate = int(data["HeartRate"])
        spo2 = float(data["SpO2"])
        activity = data["ActivityLevel"]
        sleep_hours = float(data["SleepHours"])

        # Encode activity
        activity_encoded = le_activity.transform([activity])[0]

        # Use the correct feature names used during model training
        feature_columns = ["BodyTemp", "HeartRate", "SpO2", "ActivityLevel", "SleepHours"]
        features = pd.DataFrame([[body_temp, heart_rate, spo2, activity_encoded, sleep_hours]], columns=feature_columns)

        # Predictions using the models
        pred_fever = model_fever.predict(features)[0]
        pred_dehydration = model_dehydration.predict(features)[0]
        pred_stress = model_stress.predict(features)[0]
        pred_overall = model_overall.predict(features)[0]
        overall_label = le_health.inverse_transform([pred_overall])[0]

        # Return predictions as a JSON response
        return jsonify({
            "Fever": "Yes" if pred_fever == 1 else "No",
            "Dehydration": "Yes" if pred_dehydration == 1 else "No",
            "Stress": "Yes" if pred_stress == 1 else "No",
            "OverallHealth": overall_label
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
