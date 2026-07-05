import tensorflow as tf
from tensorflow.keras import layers, models
import argparse

def add_dummy_symptom_labels(ds):
    for x, y in ds:
        dummy_symptoms = tf.zeros((tf.shape(y)[0], 10))
        yield x, {"disease_output": y, "symptom_output": dummy_symptoms}

def add_dummies_to_data(train_ds, val_ds, num_classes, IMG_SIZE):
    train_ds_with_dummy = tf.data.Dataset.from_generator(
        lambda: add_dummy_symptom_labels(train_ds),
        output_signature=(
            tf.TensorSpec(shape=(None, *IMG_SIZE, 3), dtype=tf.float32),
            {
                "disease_output": tf.TensorSpec(shape=(None, num_classes), dtype=tf.float32),
                "symptom_output": tf.TensorSpec(shape=(None, 10), dtype=tf.float32)
            }
        )
    )

    val_ds_with_dummy = tf.data.Dataset.from_generator(
        lambda: add_dummy_symptom_labels(val_ds),
        output_signature=(
            tf.TensorSpec(shape=(None, *IMG_SIZE, 3), dtype=tf.float32),
            {
                "disease_output": tf.TensorSpec(shape=(None, num_classes), dtype=tf.float32),
                "symptom_output": tf.TensorSpec(shape=(None, 10), dtype=tf.float32)
            }
        )
    )
    return train_ds_with_dummy, val_ds_with_dummy
    

        
def load_data(IMG_SIZE,BATCH_SIZE,DATASET_DIR):
    train_ds = tf.keras.preprocessing.image_dataset_from_directory(
        DATASET_DIR,
        validation_split=0.2,
        subset="training",
        seed=123,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="categorical"
    )

    val_ds = tf.keras.preprocessing.image_dataset_from_directory(
        DATASET_DIR,
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="categorical"
    )

    return train_ds, val_ds

def get_cnn(IMG_SIZE):
    cnn_base = tf.keras.applications.MobileNetV2(
        include_top=False,
        input_shape=IMG_SIZE + (3,),
        weights="imagenet"
    )
    return cnn_base

def main(IMG_SIZE = (224, 224), BATCH_SIZE = 32, DATASET_DIR="PlantVillage", epochs=100):

    IMG_SIZE = (224, 224)
    BATCH_SIZE = 32

    train_ds, val_ds = load_data(IMG_SIZE,BATCH_SIZE,DATASET_DIR)
    num_classes = train_ds.element_spec[1].shape[-1]

    
    # Preprocessing
    train_ds = train_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
    val_ds = val_ds.prefetch(buffer_size=tf.data.AUTOTUNE)


    # CNN feature extractor
    cnn_base = get_cnn(IMG_SIZE)
    cnn_base.trainable = False

    # Convert CNN spatial output to a sequence for the rnn
    cnn_features = cnn_base.output                                    
    seq = layers.Reshape((-1, cnn_features.shape[-1]))(cnn_features)

    # RNN analyzes the sequence of spatial features
    rnn_out = layers.GRU(128)(seq)

    # Disease classification head
    disease_out = layers.Dense(num_classes, activation='softmax', name="disease_output")(rnn_out)

    # Symptom prediction head (placeholder for future use)
    symptom_out = layers.Dense(10, activation='sigmoid', name="symptom_output")(rnn_out)

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
        metrics={"disease_output": "accuracy"}
    )


    # Use dummy values for the symptom labels for now
    train_ds_with_dummy, val_ds_with_dummy = add_dummies_to_data(train_ds, val_ds, num_classes, IMG_SIZE)

    # Train
    history = model.fit(
        train_ds_with_dummy,
        validation_data=val_ds_with_dummy,
        epochs=epochs
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
