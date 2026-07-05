import tensorflow as tf
import json

MODEL_PATH = "model.keras"
SYMPTOM_INDEX_FILE = "symptom_index.json"
OUTPUT_MODEL = "model_fixed_symptoms.keras"


# ---------------------------------------------------
# Load symptom vocabulary
# ---------------------------------------------------

with open(SYMPTOM_INDEX_FILE) as f:
    symptom_index = json.load(f)

NUM_SYMPTOMS = len(symptom_index)

print("🌿 Number of symptoms:", NUM_SYMPTOMS)


# ---------------------------------------------------
# Load model
# ---------------------------------------------------

model = tf.keras.models.load_model(MODEL_PATH, compile=False)

print("✅ Model loaded")


# ---------------------------------------------------
# Get existing layers
# ---------------------------------------------------

disease_layer = model.get_layer("disease_output")

# The shared feature layer feeding both heads
shared_input = disease_layer.input


# ---------------------------------------------------
# Build new symptom head
# ---------------------------------------------------

new_symptom_output = tf.keras.layers.Dense(
    NUM_SYMPTOMS,
    activation="sigmoid",
    name="symptom_output"
)(shared_input)


# ---------------------------------------------------
# Create new model
# ---------------------------------------------------

new_model = tf.keras.Model(
    inputs=model.input,
    outputs=[disease_layer.output, new_symptom_output]
)

print("✨ Symptom head rebuilt")


# ---------------------------------------------------
# Copy weights for all compatible layers
# ---------------------------------------------------

for layer in new_model.layers:
    try:
        old_layer = model.get_layer(layer.name)
        layer.set_weights(old_layer.get_weights())
    except:
        # New symptom head has no old weights
        pass


# ---------------------------------------------------
# Save model
# ---------------------------------------------------

new_model.save(OUTPUT_MODEL)

print("💾 Saved new model:", OUTPUT_MODEL)
