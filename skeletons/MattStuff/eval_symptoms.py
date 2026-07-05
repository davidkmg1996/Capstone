import tensorflow as tf
import numpy as np
import json
import os
from sklearn.model_selection import train_test_split

MODEL_PATH = "model_symptom_trained.keras"

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
THRESHOLD = 0.5

# ------------------------------------------
# LOAD SYMPTOMS
# ------------------------------------------
with open("symptom_index.json", "r", encoding="utf-8") as f:
    symptom_index = json.load(f)

NUM_SYMPTOMS = len(symptom_index)

# ------------------------------------------
# LOAD DATA (same as training)
# ------------------------------------------
with open("clip_labels_cleaned.json", "r", encoding="utf-8") as f:
    clip_data = json.load(f)

with open("healthy.json", "r", encoding="utf-8") as f:
    healthy_json = json.load(f)

# ------------------------------------------
# ENCODERS
# ------------------------------------------
def encode_symptoms(entry):
    vec = np.zeros(NUM_SYMPTOMS, dtype=np.float32)

    for item in entry:
        sym = item["symptom"]
        if sym in symptom_index:
            vec[symptom_index[sym]] = 1.0

    return vec

# ------------------------------------------
# BUILD DATASET
# ------------------------------------------
paths = []
labels = []

for item in clip_data:
    paths.append(item["image"])
    labels.append(encode_symptoms(item["labels"]))

for path in healthy_json.keys():
    paths.append(path)
    labels.append(np.zeros(NUM_SYMPTOMS, dtype=np.float32))

paths = np.array(paths)
labels = np.array(labels)

# ------------------------------------------
# SAME SPLIT STRATEGY (CRITICAL)
# ------------------------------------------
train_p, val_p, train_y, val_y = train_test_split(
    paths,
    labels,
    test_size=0.1,
    random_state=42
)

# ------------------------------------------
# DATASET PIPELINE
# ------------------------------------------
def load_image(path, label):
    img = tf.io.read_file(path)
    img = tf.image.decode_jpeg(img, channels=3)
    img = tf.image.resize(img, IMG_SIZE)
    img = tf.keras.applications.mobilenet_v2.preprocess_input(img)
    return img, label


def make_ds(paths, labels):
    ds = tf.data.Dataset.from_tensor_slices((paths, labels))
    ds = ds.map(load_image, num_parallel_calls=tf.data.AUTOTUNE)
    ds = ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
    return ds

val_ds = make_ds(val_p, val_y)

# ------------------------------------------
# CUSTOM METRICS (TRUE EVAL, NOT TRAIN TIME)
# ------------------------------------------
def compute_metrics(y_true, y_pred):
    y_pred_bin = (y_pred > THRESHOLD).astype(np.float32)

    tp = np.sum(y_true * y_pred_bin)
    fp = np.sum((1 - y_true) * y_pred_bin)
    fn = np.sum(y_true * (1 - y_pred_bin))
    tn = np.sum((1 - y_true) * (1 - y_pred_bin))

    precision = tp / (tp + fp + 1e-7)
    recall = tp / (tp + fn + 1e-7)
    f1 = 2 * precision * recall / (precision + recall + 1e-7)
    accuracy = (tp + tn) / (tp + tn + fp + fn + 1e-7)

    return precision, recall, f1, accuracy

# ------------------------------------------
# LOAD MODEL
# ------------------------------------------
model = tf.keras.models.load_model(MODEL_PATH)
print("✅ Model loaded")

# ------------------------------------------
# EVALUATE
# ------------------------------------------
print("\n🔮 Running evaluation...\n")

y_true_all = []
y_pred_all = []

for batch_x, batch_y in val_ds:
    preds = model.predict(batch_x, verbose=0)

    y_true_all.append(batch_y.numpy())
    y_pred_all.append(preds)

y_true = np.vstack(y_true_all)
y_pred = np.vstack(y_pred_all)

precision, recall, f1, acc = compute_metrics(y_true, y_pred)

# ------------------------------------------
# RESULTS
# ------------------------------------------
print("\n💜 FINAL METRICS")
print("-------------------")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1 Score:  {f1:.4f}")
print(f"Accuracy:  {acc:.4f}")

# Optional: per-symptom breakdown
print("\n📊 Per-symptom frequency (ground truth)")
counts = y_true.sum(axis=0)

for sym, idx in symptom_index.items():
    print(f"{sym:30s}: {int(counts[idx])}")
