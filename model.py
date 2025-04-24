import joblib
import os

def load_models(model_path="model"):
    models = {
        "fever": joblib.load(os.path.join(model_path, "model_fever.pkl")),
        "dehydration": joblib.load(os.path.join(model_path, "model_dehydration.pkl")),
        "stress": joblib.load(os.path.join(model_path, "model_stress.pkl")),
        "overall": joblib.load(os.path.join(model_path, "model_overall.pkl")),
        "flu": joblib.load(os.path.join(model_path, "model_flu.pkl"))
    }
    return models

def load_encoders(model_path="model"):
    encoders = {
        "health": joblib.load(os.path.join(model_path, "le_health.pkl")),
        "activity": joblib.load(os.path.join(model_path, "le_activity.pkl"))
    }
    return encoders
