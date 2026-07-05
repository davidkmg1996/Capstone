import tensorflow as tf
import os
from tensorflow.keras import layers, models
import argparse
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.model_selection import train_test_split

class MacroF1(tf.keras.metrics.Metric):
    def __init__(self, num_classes, name="macro_f1", **kwargs):
        super().__init__(name=name, **kwargs)
        self.num_classes = num_classes
        self.confusion_matrix = self.add_weight(
            name="conf_matrix",
            shape=(num_classes, num_classes),
            initializer="zeros",
            dtype=tf.float32
        )

    def update_state(self, y_true, y_pred, sample_weight=None):
        y_true = tf.argmax(y_true, axis=1)
        y_pred = tf.argmax(y_pred, axis=1)
        cm = tf.math.confusion_matrix(
            y_true, y_pred, num_classes=self.num_classes, dtype=tf.float32
        )
        self.confusion_matrix.assign_add(cm)

    def result(self):
        cm = self.confusion_matrix

        tp = tf.linalg.diag_part(cm)
        fp = tf.reduce_sum(cm, axis=0) - tp
        fn = tf.reduce_sum(cm, axis=1) - tp

        precision = tp / (tp + fp + 1e-7)
        recall = tp / (tp + fn + 1e-7)

        f1 = 2 * precision * recall / (precision + recall + 1e-7)

        return tf.reduce_mean(f1)

    def reset_states(self):
        tf.keras.backend.set_value(
            self.confusion_matrix, tf.zeros_like(self.confusion_matrix)
        )



def add_dummy_symptom_labels(x, y):
    dummy_symptoms = tf.zeros((tf.shape(y)[0], 10))
    return x, {"disease_output": y, "symptom_output": dummy_symptoms}

        
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

    # 🔥 Stratified split
    train_paths, val_paths, train_labels, val_labels = train_test_split(
        filepaths,
        labels,
        test_size=0.2,
        stratify=labels,
        random_state=123
    )

    # Convert to tensors
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

    train_ds = train_ds.shuffle(1000).batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
    val_ds   = val_ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)

    return train_ds, val_ds, class_names

def get_cnn(IMG_SIZE):
    cnn_base = tf.keras.applications.MobileNetV2(
        include_top=False,
        input_shape=IMG_SIZE + (3,),
        weights="imagenet"
    )
    return cnn_base


def transformer_encoder(x, embed_dim, num_heads, ff_dim, dropout=0.1):
    # Self-attention
    attn_output = layers.MultiHeadAttention(
        num_heads=num_heads,
        key_dim=embed_dim,
        dropout=dropout
    )(x, x)

    x = layers.Add()([x, attn_output])
    x = layers.LayerNormalization()(x)

    # Feed-forward
    ffn = layers.Dense(ff_dim, activation="relu")(x)
    ffn = layers.Dense(embed_dim)(ffn)

    x = layers.Add()([x, ffn])
    x = layers.LayerNormalization()(x)

    return x

def main(IMG_SIZE = (224, 224), BATCH_SIZE = 32, DATASET_DIR="PlantVillage", epochs=100):

    IMG_SIZE = (224, 224)
    BATCH_SIZE = 32

    train_ds, val_ds, labels = load_data(IMG_SIZE,BATCH_SIZE,DATASET_DIR) 

    print("\nDisease Output Labels")
    for i, label in enumerate(labels):
        print(f"{i} → {label}")
    
    num_classes = train_ds.element_spec[1].shape[-1]


    # CNN feature extractor
    cnn_base = get_cnn(IMG_SIZE)
    cnn_base.trainable = False

    cnn_features = cnn_base.output  # (None, 7, 7, 1280)

    # Flatten spatial → tokens
    seq = layers.Reshape((-1, cnn_features.shape[-1]))(cnn_features)  # (None, 49, 1280)

    # Project to smaller embedding (faster + regularizes)
    embed_dim = 256
    seq = layers.Dense(embed_dim)(seq)

    positions = tf.range(start=0, limit=49, delta=1)
    pos_embed = layers.Embedding(input_dim=49, output_dim=embed_dim)(positions)
    seq = seq + pos_embed

    # Transformer encoder(s)
    x = transformer_encoder(seq, embed_dim, num_heads=4, ff_dim=512)
    x = transformer_encoder(x, embed_dim, num_heads=4, ff_dim=512)

    # Pool tokens → single vector
    x = layers.GlobalAveragePooling1D()(x)
    x = layers.Dropout(0.3)(x)



    disease_out = layers.Dense(
        num_classes,
        activation='softmax',
        name="disease_output"
    )(x)

    symptom_out = layers.Dense(
        10,
        activation='sigmoid',
        name="symptom_output"
    )(x)

    # Build model
    model = models.Model(inputs=cnn_base.input, outputs=[disease_out, symptom_out])

    # Compile (ignore symptom loss for now)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
        loss={
            "disease_output": "categorical_crossentropy",
            "symptom_output": "binary_crossentropy"
        },
        loss_weights={
            "disease_output": 1.0,
            "symptom_output": 0.0
        },
        metrics={
            "disease_output": [
                "accuracy",
                MacroF1(num_classes)
            ]
        }
    )

    preprocess = tf.keras.applications.mobilenet_v2.preprocess_input
    train_ds = train_ds.map(lambda x, y: (preprocess(x), y))
    val_ds = val_ds.map(lambda x, y: (preprocess(x), y))



    # Use dummy values for the symptom labels for now
    train_ds_with_dummy = train_ds.map(add_dummy_symptom_labels)
    val_ds_with_dummy = val_ds.map(add_dummy_symptom_labels)

    # Prefetching
    train_ds_with_dummy = train_ds_with_dummy.prefetch(buffer_size=tf.data.AUTOTUNE)
    val_ds_with_dummy = val_ds_with_dummy.prefetch(buffer_size=tf.data.AUTOTUNE)

    checkpoint_cb = ModelCheckpoint(
        filepath="best_plant_disease_model.h5",
        monitor="val_disease_output_macro_f1",
        save_best_only=True,
        save_weights_only=False,   # saves full model (architecture + weights)
        mode="max",
        verbose=1
    )

    earlystop_cb = EarlyStopping(
        monitor="val_disease_output_accuracy",
        patience=10,
        mode="max",
        restore_best_weights=True,
        verbose=1
    )

    # Train
    history = model.fit(
        train_ds_with_dummy,
        validation_data=val_ds_with_dummy,
        epochs=epochs,
        callbacks=[checkpoint_cb, earlystop_cb]
    )

    # Save
    model.save("plant_disease_model_sequence.h5")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a TensorFlow model on PlantVillage dataset.")
    parser.add_argument("--img-width", type=int, default=224, help="Width of input images.")
    parser.add_argument("--img-height", type=int, default=224, help="Height of input images.")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for training.")
    parser.add_argument("--dataset-dir", type=str, default="PlantVillage", help="Path to dataset directory.")
    parser.add_argument("--epochs", type=int, default=100, help="Number of epochs to train for.")

    args = parser.parse_args()

    IMG_SIZE = (args.img_width, args.img_height)
    main(IMG_SIZE=IMG_SIZE,
         BATCH_SIZE=args.batch_size,
         DATASET_DIR=args.dataset_dir,
         epochs=args.epochs)
