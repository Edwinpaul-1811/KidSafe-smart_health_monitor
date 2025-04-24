from flask import Flask, request, jsonify, send_from_directory, redirect, url_for
from flask_cors import CORS
import pandas as pd
from model import load_models, load_encoders
from db import create_user, verify_user

app = Flask(__name__, static_folder="public")
CORS(app)

# Load models and encoders
models = load_models()
encoders = load_encoders()

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        features = pd.DataFrame([[
            float(data["BodyTemp"]),
            int(data["HeartRate"]),
            float(data["SpO2"]),
            encoders["activity"].transform([data["ActivityLevel"]])[0],
            float(data["SleepHours"])
        ]], columns=["BodyTemp", "HeartRate", "SpO2", "ActivityLevel", "SleepHours"])

        result = {
            "Fever": "Yes" if models["fever"].predict(features)[0] == 1 else "No",
            "Dehydration": "Yes" if models["dehydration"].predict(features)[0] == 1 else "No",
            "Stress": "Yes" if models["stress"].predict(features)[0] == 1 else "No",
            "Flu": "Yes" if models["flu"].predict(features)[0] == 1 else "No",
            "OverallHealth": encoders["health"].inverse_transform([models["overall"].predict(features)[0]])[0]
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if create_user(username, password):
            return redirect(url_for("login"))
        return "User already exists or error occurred."
    return send_from_directory(app.static_folder, "register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if verify_user(username, password):
            return redirect(url_for("index"))
        return "Invalid credentials"
    return send_from_directory(app.static_folder, "login.html")

if __name__ == "__main__":
    app.run(debug=True)
