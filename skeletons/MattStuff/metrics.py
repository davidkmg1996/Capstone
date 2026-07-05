import os
import numpy as np
import tensorflow as tf
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from sklearn.model_selection import train_test_split

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
DATASET_DIR = "PlantVillage"
MODEL_PATH = "model.keras"


# 🔁 Same stratified loader you used for training
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

    val_paths = tf.constant(val_paths)
    val_labels = tf.constant(val_labels)

    num_classes = len(class_names)

    def load_image(path, label):
        img = tf.io.read_file(path)
        img = tf.image.decode_jpeg(img, channels=3)
        img = tf.image.resize(img, IMG_SIZE)
        img = tf.keras.applications.mobilenet_v2.preprocess_input(img)
        label = tf.one_hot(label, num_classes)
        return img, label

    val_ds = tf.data.Dataset.from_tensor_slices((val_paths, val_labels))
    val_ds = val_ds.map(load_image, num_parallel_calls=tf.data.AUTOTUNE)
    val_ds = val_ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)

    return val_ds, class_names


# 🌿 Load model
model = tf.keras.models.load_model(MODEL_PATH)

# 🍃 Load validation data
val_ds, class_names = load_data(IMG_SIZE, BATCH_SIZE, DATASET_DIR)

y_true = []
y_pred = []

# 🔮 Run inference
for images, labels in val_ds:
    preds = model.predict(images, verbose=0)

    # multi-head → take disease output
    disease_preds = preds[0]

    y_true.extend(np.argmax(labels.numpy(), axis=1))
    y_pred.extend(np.argmax(disease_preds, axis=1))

y_true = np.array(y_true)
y_pred = np.array(y_pred)

# 🌟 Metrics
accuracy = accuracy_score(y_true, y_pred)
precision = precision_score(y_true, y_pred, average="macro", zero_division=0)
recall = recall_score(y_true, y_pred, average="macro", zero_division=0)
f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)

print("\n🌿 Validation Metrics")
print(f"Accuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"Macro F1 : {f1:.4f}")

print("\n🍄 Per-class report")
print(classification_report(y_true, y_pred, target_names=class_names, zero_division=0))
