import joblib
import os

# Define the model and encoder paths
MODEL_PATH = "model"

# Function to load models
def load_model(model_name):
    return joblib.load(os.path.join(MODEL_PATH, f"{model_name}.pkl"))

# Load models
model_fever = load_model("model_fever")
model_dehydration = load_model("model_dehydration")
model_stress = load_model("model_stress")
model_flu = load_model("model_flu")
model_overall = load_model("model_overall")

# Load encoders
le_health = load_model("le_health")
le_activity = load_model("le_activity")
