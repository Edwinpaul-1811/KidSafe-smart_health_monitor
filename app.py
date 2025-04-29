from flask import Flask, request, jsonify, render_template, redirect, session
import pandas as pd
from model import model_fever, model_dehydration, model_stress, model_flu, model_overall, le_health, le_activity
import numpy as np
from db import init_app, create_user, verify_user, close_connection  # Import your database functions

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize the database connection
init_app(app)

# Optional: Load dataset if you want to use or display it somewhere
df = pd.read_csv("full_kids_health_dataset.csv")

# Home route
@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')  # Redirect to login if not logged in
    return render_template('index.html')  # Show the main form if logged in

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()  # Get the JSON data from the request

        username = data.get('username')
        password = data.get('password')

        if verify_user(username, password):
            session['user'] = username  # Store user in session
            return jsonify({"message": "Login successful!"}), 200  # Return success message
        else:
            return jsonify({"message": "Invalid credentials, please try again"}), 401  # 401 Unauthorized

    return render_template('login.html')  # Display login page for GET request

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"message": "Username and password are required."}), 400

        if create_user(username, password):
            return jsonify({"message": "User registered successfully!"}), 201
        else:
            return jsonify({"message": "Registration failed. Username may already exist."}), 409 # 409 Conflict

    return render_template('register.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove the user from session
    return redirect('/login')  # Redirect to login page after logging out

# Prediction route
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        # Try this combination of 5 features
        features = [
            float(data['BodyTemp']),
            int(data['HeartRate']),
            float(data['SpO2']),
            float(data['SleepHours']),
            int(data['WaterIntake'])
        ]

        # Reshape input for model
        input_data = np.array(features).reshape(1, -1)

        # Predictions
        pred_fever = "Yes" if model_fever.predict(input_data)[0] == 1 else "No"
        pred_dehydration = "Yes" if model_dehydration.predict(input_data)[0] == 1 else "No"
        pred_stress = "Yes" if model_stress.predict(input_data)[0] == 1 else "No"
        pred_flu = "Yes" if model_flu.predict(input_data)[0] == 1 else "No"
        pred_overall = model_overall.predict(input_data)[0]
        pred_overall_label = le_health.inverse_transform([pred_overall])[0]

        # Return prediction results as a JSON response
        return jsonify({
            "Fever": pred_fever,
            "Dehydration": pred_dehydration,
            "Stress": pred_stress,
            "Flu": pred_flu,
            "OverallHealth": pred_overall_label
        })

    except Exception as e:
        return jsonify({"error": str(e)})

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)

# Consider adding this to close the database connection when the app shuts down
@app.teardown_appcontext
def shutdown_session(exception=None):
    close_connection()