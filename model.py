import joblib
from sklearn.ensemble import RandomForestClassifier
import numpy as np

# Dummy data
X = np.random.rand(100, 5)  # 5 features: BodyTemp, HeartRate, SpO2, ActivityLevel, SleepHours
y = np.random.randint(0, 2, 100)  # Binary classification: Flu (1) or Not (0)

# Train dummy model
model = RandomForestClassifier()
model.fit(X, y)

# Save model
joblib.dump(model, "model/model_flu.pkl")

print("✅ Dummy Flu model saved as model/model_flu.pkl")
