import tensorflow as tf
import numpy as np
import json
import random
import os
from sklearn.model_selection import train_test_split

MODEL_PATH = "model.keras"
OUTPUT_MODEL = "model_symptom_pretrained.keras"

DATASET_DIR = "PlantVillage"
KNOWLEDGE_FILE = "disease_symptoms.json"
SYMPTOM_INDEX_FILE = "symptom_index.json"

IMG_SIZE = (224,224)
BATCH_SIZE = 32
EPOCHS = 10


# ---------------------------------------------------
# Utility: convert JSON names → folder names
# ---------------------------------------------------

def json_to_folder_name(plant, disease):

    disease = disease.replace(" ", "_")

    return f"{plant}___{disease}"


# ---------------------------------------------------
# Load knowledge base
# ---------------------------------------------------

with open(KNOWLEDGE_FILE) as f:
    disease_db = json.load(f)

with open(SYMPTOM_INDEX_FILE) as f:
    symptom_index = json.load(f)

NUM_SYMPTOMS = len(symptom_index)


disease_to_symptoms = {}

for entry in disease_db:

    folder_name = json_to_folder_name(
        entry["plant"],
        entry["disease"]
    )

    disease_to_symptoms[folder_name] = entry["symptoms"]


# ---------------------------------------------------
# Stratified Data Loader
# ---------------------------------------------------

def load_data(IMG_SIZE, BATCH_SIZE, DATASET_DIR):

    class_names = sorted([
        d for d in os.listdir(DATASET_DIR)
        if os.path.isdir(os.path.join(DATASET_DIR, d))
    ])

    filepaths = []
    labels = []

    for idx, class_name in enumerate(class_names):

        class_dir = os.path.join(DATASET_DIR, class_name)

        for fname in os.listdir(class_dir):

            filepaths.append(os.path.join(class_dir, fname))
            labels.append(idx)


    train_paths, val_paths, train_labels, val_labels = train_test_split(
        filepaths,
        labels,
        test_size=0.2,
        stratify=labels,
        random_state=123
    )

    train_paths = tf.constant(train_paths)
    val_paths   = tf.constant(val_paths)

    train_labels = tf.constant(train_labels)
    val_labels   = tf.constant(val_labels)

    num_classes = len(class_names)

    def load_image(path, label):

        img = tf.io.read_file(path)
        img = tf.image.decode_jpeg(img, channels=3)
        img = tf.image.resize(img, IMG_SIZE)

        label = tf.one_hot(label, num_classes)

        return img, label


    train_ds = tf.data.Dataset.from_tensor_slices((train_paths, train_labels))
    val_ds   = tf.data.Dataset.from_tensor_slices((val_paths, val_labels))


    train_ds = train_ds.map(load_image, num_parallel_calls=tf.data.AUTOTUNE)
    val_ds   = val_ds.map(load_image, num_parallel_calls=tf.data.AUTOTUNE)


    preprocess = tf.keras.applications.mobilenet_v2.preprocess_input

    train_ds = train_ds.map(lambda x, y: (preprocess(x), y))
    val_ds   = val_ds.map(lambda x, y: (preprocess(x), y))


    train_ds = train_ds.shuffle(1000).batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
    val_ds   = val_ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)

    return train_ds, val_ds, num_classes, class_names


train_ds, val_ds, num_classes, class_names = load_data(
    IMG_SIZE, BATCH_SIZE, DATASET_DIR
)


# ---------------------------------------------------
# Dummy symptom generator
# ---------------------------------------------------

SYMPTOM_PRESENT_PROB = 0.7

def generate_dummy_symptoms(class_index):

    class_name = class_names[class_index]

    symptoms = disease_to_symptoms.get(class_name, [])

    vec = np.zeros(NUM_SYMPTOMS)

    if len(symptoms) == 0:
        return vec.astype(np.float32)

    # probabilistically include each symptom
    for s in symptoms:
        if random.random() < SYMPTOM_PRESENT_PROB:
            vec[symptom_index[s]] = random.uniform(0.7, 0.9)

    # ensure at least one symptom exists
    if vec.sum() == 0:
        s = random.choice(symptoms)
        vec[symptom_index[s]] = random.uniform(0.7, 0.9)

    return vec.astype(np.float32)

# ---------------------------------------------------
# Add dummy symptoms to dataset
# ---------------------------------------------------

def attach_dummy_symptoms(x, y):

    label_index = tf.argmax(y, axis=-1)

    symptom_vec = tf.numpy_function(
        generate_dummy_symptoms,
        [label_index],
        tf.float32
    )

    symptom_vec.set_shape((NUM_SYMPTOMS,))

    return x, {
        "disease_output": y,
        "symptom_output": symptom_vec
    }


train_ds = train_ds.unbatch()
val_ds   = val_ds.unbatch()

train_ds = train_ds.map(attach_dummy_symptoms, num_parallel_calls=tf.data.AUTOTUNE)
val_ds   = val_ds.map(attach_dummy_symptoms, num_parallel_calls=tf.data.AUTOTUNE)

train_ds = train_ds.batch(BATCH_SIZE)
val_ds   = val_ds.batch(BATCH_SIZE)


# ---------------------------------------------------
# Load model
# ---------------------------------------------------

model = tf.keras.models.load_model(MODEL_PATH)

print("✅ Model loaded")


# ---------------------------------------------------
# Freeze CNN backbone
# ---------------------------------------------------

for layer in model.layers:
    if "mobilenet" in layer.name.lower():
        layer.trainable = False

print("🧊 CNN frozen")


# ---------------------------------------------------
# Compile (only train symptom head)
# ---------------------------------------------------

model.compile(

    optimizer=tf.keras.optimizers.Adam(1e-4),

    loss={
        "disease_output": "categorical_crossentropy",
        "symptom_output": "binary_crossentropy"
    },

    loss_weights={
        "disease_output": 0.0,
        "symptom_output": 1.0
    },

    metrics={
        "symptom_output": [tf.keras.metrics.BinaryCrossentropy()]
    }
)


# ---------------------------------------------------
# Train
# ---------------------------------------------------

model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS
)


# ---------------------------------------------------
# Save
# ---------------------------------------------------

model.save(OUTPUT_MODEL)

print("💾 Saved:", OUTPUT_MODEL)
