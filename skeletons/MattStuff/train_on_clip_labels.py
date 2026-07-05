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

# ------------------------------------------
# Custom F1 metric
# ------------------------------------------
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

# ------------------------------------------
# Load symptom index
# ------------------------------------------
with open("symptom_index.json", "r", encoding="utf-8") as f:
    symptom_index = json.load(f)

NUM_SYMPTOMS = len(symptom_index)

# ------------------------------------------
# Load CLIP + healthy data
# ------------------------------------------
with open("clip_labels_cleaned.json", "r", encoding="utf-8") as f:
    clip_data = json.load(f)

with open("healthy.json", "r", encoding="utf-8") as f:
    healthy_json = json.load(f)

# ------------------------------------------
# Build disease index (for stratification)
# ------------------------------------------
all_paths = [entry["image"] for entry in clip_data] + list(healthy_json.keys())

all_disease_names = sorted(set(
    os.path.basename(os.path.dirname(p))
    for p in all_paths
))

disease_index = {name: i for i, name in enumerate(all_disease_names)}
NUM_DISEASES = len(disease_index)

# ------------------------------------------
# Encoders
# ------------------------------------------
CONF_THRESHOLD = 0.3  # 🔥 tweak if needed

def encode_symptoms_from_clip(label_list):
    vec = np.zeros(NUM_SYMPTOMS, dtype=np.float32)

    for item in label_list:
        if item["confidence"] >= CONF_THRESHOLD:
            symptom = item["symptom"]
            if symptom in symptom_index:
                vec[symptom_index[symptom]] = 1.0

    return vec

def encode_disease_for_strat(path):
    folder = os.path.basename(os.path.dirname(path))
    return disease_index[folder]

# ------------------------------------------
# Build dataset
# ------------------------------------------
paths = []
symptom_labels = []
disease_labels = []

# Diseased (CLIP)
for entry in clip_data:
    path = entry["image"]
    paths.append(path)

    symptom_labels.append(
        encode_symptoms_from_clip(entry["labels"])
    )

    disease_labels.append(
        encode_disease_for_strat(path)
    )

# Healthy (zero symptoms)
for path in healthy_json.keys():
    paths.append(path)

    symptom_labels.append(
        np.zeros(NUM_SYMPTOMS, dtype=np.float32)
    )

    disease_labels.append(
        encode_disease_for_strat(path)
    )

paths = np.array(paths)
symptom_labels = np.array(symptom_labels)
disease_labels = np.array(disease_labels)

# ------------------------------------------
# Stratified split
# ------------------------------------------
train_p, val_p, train_s, val_s, train_d, val_d = train_test_split(
    paths,
    symptom_labels,
    disease_labels,
    test_size=0.2,
    stratify=disease_labels,
    random_state=123
)

# ------------------------------------------
# Dataset loader
# ------------------------------------------
def load_image(path, symptom_vec, disease_label):
    img = tf.io.read_file(path)
    img = tf.image.decode_jpeg(img, channels=3)
    img = tf.image.resize(img, IMG_SIZE)

    disease_vec = tf.zeros(NUM_DISEASES)

    return img, {
        "symptom_output": symptom_vec,
        "disease_output": disease_vec
    }

def make_dataset(paths, sym, dis):
    ds = tf.data.Dataset.from_tensor_slices((paths, sym, dis))
    ds = ds.map(load_image, num_parallel_calls=tf.data.AUTOTUNE)
    return ds

train_ds = make_dataset(train_p, train_s, train_d)
val_ds   = make_dataset(val_p, val_s, val_d)

# ------------------------------------------
# Augmentation
# ------------------------------------------
augment = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal"),
    tf.keras.layers.RandomRotation(0.08),
    tf.keras.layers.RandomZoom(0.1),
    tf.keras.layers.RandomContrast(0.1),
])

def aug(x, y):
    return augment(x, training=True), y

train_ds = train_ds.map(aug, num_parallel_calls=tf.data.AUTOTUNE)

# ------------------------------------------
# Preprocess
# ------------------------------------------
preprocess = tf.keras.applications.mobilenet_v2.preprocess_input

train_ds = train_ds.map(lambda x, y: (preprocess(x), y))
val_ds   = val_ds.map(lambda x, y: (preprocess(x), y))

train_ds = train_ds.shuffle(1000).batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
val_ds   = val_ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)

# ------------------------------------------
# Load model
# ------------------------------------------
model = tf.keras.models.load_model(MODEL_PATH)
print("✅ Model loaded")

# Freeze backbone
for layer in model.layers:
    if "mobilenet" in layer.name.lower():
        layer.trainable = False

print("🧊 Backbone frozen")

# ------------------------------------------
# Compile
# ------------------------------------------
model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-4),
    loss={
        "symptom_output": "binary_crossentropy",
        "disease_output": "binary_crossentropy"
    },
    loss_weights={
        "symptom_output": 1.0,
        "disease_output": 0.0
    },
    metrics={
        "symptom_output": [
            MultiLabelF1(),
            tf.keras.metrics.AUC()
        ]
    }
)

# ------------------------------------------
# Checkpoint
# ------------------------------------------
from tensorflow.keras.callbacks import ModelCheckpoint

checkpoint = ModelCheckpoint(
    filepath="best_model.keras",
    monitor="val_symptom_output_auc",
    save_best_only=True,
    verbose=1,
    mode="max"
)

# ------------------------------------------
# Train
# ------------------------------------------
model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS,
    callbacks=[checkpoint]
)

# ------------------------------------------
# Save
# ------------------------------------------
model.save(OUTPUT_MODEL)
print("💾 Saved:", OUTPUT_MODEL)
