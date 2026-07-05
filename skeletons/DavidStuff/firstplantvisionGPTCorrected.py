import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from PIL import Image
import joblib
from sklearn.preprocessing import LabelEncoder

# --------------------------------------------------------
# 1. LOAD DATASET
# --------------------------------------------------------
# Your dataset folder should look like:
# PlantVillage/
#    ├── Apple___Black_rot
#    ├── Apple___Cedar_apple_rust
#    ├── etc...

DATASET_DIR = "PlantVillage"   # Change this if needed
IMAGE_SIZE = (256, 256)
BATCH_SIZE = 32

train_ds = keras.preprocessing.image_dataset_from_directory(
    DATASET_DIR,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE
)

val_ds = keras.preprocessing.image_dataset_from_directory(
    DATASET_DIR,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE
)

class_names = train_ds.class_names
print("Detected Classes:", class_names)

# Save label encoder for later predictions
encoder = LabelEncoder()
encoder.fit(class_names)
joblib.dump(encoder, "label_encoder.joblib")
print("Saved label encoder → label_encoder.joblib")

# Prefetch for performance
AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.prefetch(AUTOTUNE)
val_ds = val_ds.prefetch(AUTOTUNE)

# --------------------------------------------------------
# 2. BUILD CNN MODEL
# --------------------------------------------------------
model = keras.Sequential([
    layers.Rescaling(1./255, input_shape=(256, 256, 3)),

    layers.Conv2D(32, 3, activation='relu'),
    layers.MaxPooling2D(),

    layers.Conv2D(64, 3, activation='relu'),
    layers.MaxPooling2D(),

    layers.Conv2D(128, 3, activation='relu'),
    layers.MaxPooling2D(),

    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.3),
    layers.Dense(len(class_names), activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

# --------------------------------------------------------
# 3. TRAIN MODEL
# --------------------------------------------------------
EPOCHS = 10  # Increase to 20–30 for better accuracy

history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS
)

# --------------------------------------------------------
# 4. SAVE MODEL
# --------------------------------------------------------
MODEL_PATH = "plant_disease_model.keras"
model.save(MODEL_PATH)
print(f"Saved model → {MODEL_PATH}")


# --------------------------------------------------------
# 5. SINGLE IMAGE PREDICTION FUNCTION
# --------------------------------------------------------
def predict_one_image(image_path,
                      model_path="plant_disease_model.keras",
                      encoder_path="label_encoder.joblib",
                      target_size=(256,256)):

    # Load model + encoder
    model = tf.keras.models.load_model(model_path)
    encoder = joblib.load(encoder_path)

    # Load and prepare image
    img = Image.open(image_path).convert("RGB").resize(target_size)
    arr = np.array(img) / 255.0
    arr = np.expand_dims(arr, axis=0)

    # Predict
    preds = model.predict(arr)[0]
    idx = int(np.argmax(preds))
    label = encoder.inverse_transform([idx])[0]
    confidence = float(preds[idx])

    # Build result object
    return {
        "predicted_label": label,
        "confidence": confidence,
        "probabilities": {
            cls: float(p) for cls, p in zip(encoder.classes_, preds)
        }
    }


# --------------------------------------------------------
# 6. OPTIONAL: TEST PREDICTION (replace path)
# --------------------------------------------------------
# Example usage after training:
# result = predict_one_image("test_leaf.jpg")
# print(result)
