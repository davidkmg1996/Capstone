import os
import tensorflow as tf
from sklearn.model_selection import train_test_split

# -----------------------------
# 🔥 USER CONFIG
# -----------------------------
DATASET_DIR = "PlantVillage"
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 10
INPUT_KERAS_MODEL = "plant_disease_model_sequence.keras"
OUTPUT_KERAS_MODEL = "plant_disease_model_finetuned.keras"

# -----------------------------
# 🍃 DATA LOADER
# -----------------------------
def load_data(IMG_SIZE, BATCH_SIZE, DATASET_DIR):
    class_names = sorted([d for d in os.listdir(DATASET_DIR)
                          if os.path.isdir(os.path.join(DATASET_DIR, d))])

    filepaths = []
    labels = []

    for idx, class_name in enumerate(class_names):
        class_dir = os.path.join(DATASET_DIR, class_name)
        for fname in os.listdir(class_dir):
            filepaths.append(os.path.join(class_dir, fname))
            labels.append(idx)

    # Stratified split
    train_paths, val_paths, train_labels, val_labels = train_test_split(
        filepaths, labels, test_size=0.2, stratify=labels, random_state=123
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

    # Load + preprocess
    train_ds = train_ds.map(load_image, num_parallel_calls=tf.data.AUTOTUNE)
    val_ds   = val_ds.map(load_image, num_parallel_calls=tf.data.AUTOTUNE)

    preprocess = tf.keras.applications.mobilenet_v2.preprocess_input
    train_ds = train_ds.map(lambda x, y: (preprocess(x), y))
    val_ds   = val_ds.map(lambda x, y: (preprocess(x), y))

    # Batch + prefetch
    train_ds = train_ds.shuffle(1000).batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
    val_ds   = val_ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)

    return train_ds, val_ds, num_classes, class_names

# -----------------------------
# 🔹 Dummy symptom labels for multi-headed model
# -----------------------------
def add_dummy_symptom_labels(x, y):
    dummy_symptoms = tf.zeros((tf.shape(y)[0], 10))
    return x, {"disease_output": y, "symptom_output": dummy_symptoms}

# -----------------------------
# ⚡ Load model & unfreeze CNN
# -----------------------------
model = tf.keras.models.load_model(INPUT_KERAS_MODEL)
print("✅ Model loaded.")

for layer in model.layers:
    if 'mobilenetv2' in layer.name:
        layer.trainable = True
print("💪 CNN backbone unfrozen for fine-tuning.")

# -----------------------------
# 🔥 Load dataset
# -----------------------------
train_ds, val_ds, num_classes, class_names = load_data(IMG_SIZE, BATCH_SIZE, DATASET_DIR)

train_ds_with_dummy = train_ds.map(add_dummy_symptom_labels)
val_ds_with_dummy   = val_ds.map(add_dummy_symptom_labels)

# -----------------------------
# ✨ Compile
# -----------------------------
model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-5),  # low LR for fine-tuning
    loss={
        "disease_output": "categorical_crossentropy",
        "symptom_output": "binary_crossentropy"
    },
    loss_weights={
        "disease_output": 1.0,
        "symptom_output": 0.0
    },
    metrics={"disease_output": ["accuracy"]}
)

# -----------------------------
# 💾 Checkpoint callback
# -----------------------------
checkpoint_cb = tf.keras.callbacks.ModelCheckpoint(
    OUTPUT_KERAS_MODEL,
    monitor='val_disease_output_accuracy',
    mode='max',
    save_best_only=True,
    save_weights_only=False,
    verbose=1
)

# -----------------------------
# 🏋️ Train
# -----------------------------
history = model.fit(
    train_ds_with_dummy,
    validation_data=val_ds_with_dummy,
    epochs=EPOCHS,
    callbacks=[checkpoint_cb]
)
