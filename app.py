from flask import Flask, request, jsonify, send_from_directory, redirect, url_for, session
from flask_cors import CORS
import pandas as pd
import os
import db  # Your db.py module
import model  # Your model.py module

app = Flask(__name__, static_folder="public")
app.secret_key = "your_secret_key_here"  # Needed for session support
CORS(app)

# Initialize MySQL connection
db.init_app(app)

@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for("index"))
    else:
        return redirect(url_for("login"))

@app.route("/index")
def index():
    if "username" in session:
        return send_from_directory(app.static_folder, "index.html")
    else:
        return redirect(url_for("login"))

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

        # Extra features
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

        return jsonify({
            "Fever": "Yes" if pred_fever == 1 else "No",
            "Dehydration": "Yes" if pred_dehydration == 1 else "No",
            "Stress": "Yes" if pred_stress == 1 else "No",
            "Flu": "Yes" if pred_flu == 1 else "No",
            "OverallHealth": overall_label
        })

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return send_from_directory(app.static_folder, "register.html")
    
    if request.method == "POST":
        try:
            data = request.get_json()
            username = data["username"]
            password = data["password"]

            if db.create_user(username, password):
                return jsonify({"message": "User registered successfully!"}), 201
            else:
                return jsonify({"message": "Username already exists!"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return send_from_directory(app.static_folder, "login.html")
    
    if request.method == "POST":
        try:
            data = request.get_json()
            username = data["username"]
            password = data["password"]

            if db.verify_user(username, password):
                session["username"] = username
                return jsonify({"message": "Login successful!"})
            else:
                return jsonify({"message": "Invalid username or password!"}), 401
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
