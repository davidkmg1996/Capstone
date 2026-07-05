import tensorflow as tf
import numpy as np
import json
import os
from sklearn.model_selection import train_test_split

MODEL_PATH = "model.keras"
OUTPUT_MODEL = "model_symptom_trained.keras"

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 15


import tensorflow as tf

class MultiLabelF1(tf.keras.metrics.Metric):
    def __init__(self, name="f1", threshold=0.5, **kwargs):
        super().__init__(name=name, **kwargs)
        self.threshold = threshold

        self.tp = self.add_weight(name="tp", initializer="zeros")
        self.fp = self.add_weight(name="fp", initializer="zeros")
        self.fn = self.add_weight(name="fn", initializer="zeros")

    def update_state(self, y_true, y_pred, sample_weight=None):
        y_pred = tf.cast(y_pred > self.threshold, tf.float32)
        y_true = tf.cast(y_true, tf.float32)

        tp = tf.reduce_sum(y_true * y_pred)
        fp = tf.reduce_sum((1 - y_true) * y_pred)
        fn = tf.reduce_sum(y_true * (1 - y_pred))

        self.tp.assign_add(tp)
        self.fp.assign_add(fp)
        self.fn.assign_add(fn)

    def result(self):
        precision = self.tp / (self.tp + self.fp + 1e-7)
        recall = self.tp / (self.tp + self.fn + 1e-7)
        return 2 * precision * recall / (precision + recall + 1e-7)

    def reset_state(self):
        for v in self.variables:
            v.assign(0.0)

# ---------------------------------------------------
# Load symptom index
# ---------------------------------------------------
with open("symptom_index.json", "r", encoding="utf-8") as f:
    symptom_index = json.load(f)

NUM_SYMPTOMS = len(symptom_index)

# ---------------------------------------------------
# Load data
# ---------------------------------------------------
def load_jsonl(path):
    data = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                obj = json.loads(line)
                data[obj["path"]] = obj
    return data


with open("healthy.json", "r", encoding="utf-8") as f:
    healthy_json = json.load(f)

diseased_json = load_jsonl("labels.json")

# ---------------------------------------------------
# Disease labels (DUMMY - not trained yet)
# ---------------------------------------------------
all_disease_names = sorted(set(
    os.path.basename(os.path.dirname(p))
    for p in list(diseased_json.keys()) + list(healthy_json.keys())
))

disease_index = {name: i for i, name in enumerate(all_disease_names)}
NUM_DISEASES = len(disease_index)

# ---------------------------------------------------
# Encoders
# ---------------------------------------------------
def encode_symptoms(label_dict):
    vec = np.zeros(NUM_SYMPTOMS, dtype=np.float32)
    for k, v in label_dict.items():
        if v and k in symptom_index:
            vec[symptom_index[k]] = 1.0
    return vec


def encode_disease_dummy(path):
    """
    Disease head is NOT trained yet.
    We still provide valid one-hot vectors so model stays structurally consistent.
    """
    folder = os.path.basename(os.path.dirname(path))
    idx = disease_index[folder]
    vec = np.zeros(NUM_DISEASES, dtype=np.float32)
    vec[idx] = 0.0   # 💀 intentionally zeroed
    return vec

# ---------------------------------------------------
# Build dataset
# ---------------------------------------------------
paths = []
symptom_labels = []
disease_labels = []

for path, entry in diseased_json.items():
    paths.append(path)
    symptom_labels.append(encode_symptoms(entry["labels"]))
    disease_labels.append(encode_disease_dummy(path))

for path, entry in healthy_json.items():
    paths.append(path)
    symptom_labels.append(np.zeros(NUM_SYMPTOMS, dtype=np.float32))
    disease_labels.append(encode_disease_dummy(path))

paths = np.array(paths)
symptom_labels = np.array(symptom_labels)
disease_labels = np.array(disease_labels)

# ---------------------------------------------------
# 90/10 split (your requirement)
# ---------------------------------------------------
train_p, val_p, train_s, val_s, train_d, val_d = train_test_split(
    paths,
    symptom_labels,
    disease_labels,
    test_size=0.1,
    random_state=42
)

# ---------------------------------------------------
# Dataset loader
# ---------------------------------------------------
def load_image(path, symptom_vec, disease_vec):

    img = tf.io.read_file(path)
    img = tf.image.decode_jpeg(img, channels=3)
    img = tf.image.resize(img, IMG_SIZE)

    return img, {
        "symptom_output": symptom_vec,
        "disease_output": disease_vec
    }


def make_dataset(paths, sym, dis):
    ds = tf.data.Dataset.from_tensor_slices((paths, sym, dis))
    ds = ds.map(load_image, num_parallel_calls=tf.data.AUTOTUNE)
    return ds

train_ds = make_dataset(train_p, train_s, train_d)
val_ds = make_dataset(val_p, val_s, val_d)

# ---------------------------------------------------
# Augmentation (train only)
# ---------------------------------------------------
augment = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal"),
    tf.keras.layers.RandomRotation(0.08),
    tf.keras.layers.RandomZoom(0.1),
    tf.keras.layers.RandomContrast(0.1),
])

def aug(x, y):
    return augment(x, training=True), y

train_ds = train_ds.map(aug, num_parallel_calls=tf.data.AUTOTUNE)

# ---------------------------------------------------
# Preprocess
# ---------------------------------------------------
preprocess = tf.keras.applications.mobilenet_v2.preprocess_input

train_ds = train_ds.map(lambda x, y: (preprocess(x), y))
val_ds   = val_ds.map(lambda x, y: (preprocess(x), y))

train_ds = train_ds.shuffle(1000).batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
val_ds = val_ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)

# ---------------------------------------------------
# Load model
# ---------------------------------------------------
model = tf.keras.models.load_model(MODEL_PATH)
print("✅ Model loaded")

# Freeze backbone (for now)
for layer in model.layers:
    if "mobilenet" in layer.name.lower():
        layer.trainable = False

print("🧊 Backbone frozen")

# ---------------------------------------------------
# Compile (symptom ONLY learning)
# ---------------------------------------------------
model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-4),
    loss={
        "symptom_output": "binary_crossentropy",
        "disease_output": "binary_crossentropy"
    },
    loss_weights={
        "symptom_output": 1.0,
        "disease_output": 0.0   # 💀 completely ignored
    },
    metrics={
        "symptom_output": [
            MultiLabelF1(),
            tf.keras.metrics.AUC()
        ]
    }
)

# ---------------------------------------------------
# Checkpoint: BEST MODEL ONLY
# ---------------------------------------------------
from tensorflow.keras.callbacks import ModelCheckpoint

checkpoint = ModelCheckpoint(
    filepath="best_model.keras",
    monitor="val_symptom_output_auc",  # best metric for symptoms
    save_best_only=True,
    verbose=1,
    mode="max"
)

# ---------------------------------------------------
# Train
# ---------------------------------------------------
model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS,
    callbacks=[checkpoint]
)

# ---------------------------------------------------
# Save final model
# ---------------------------------------------------
model.save(OUTPUT_MODEL)
print("💾 Saved:", OUTPUT_MODEL)
