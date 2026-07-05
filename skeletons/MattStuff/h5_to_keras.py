import tensorflow as tf
from tensorflow.keras import layers, models

IMG_SIZE = (224, 224)
NUM_CLASSES = 38   # 🔥 change this to your actual number of disease classes
H5_PATH = "plant_disease_model_sequence.h5"
KERAS_PATH = "plant_disease_model_sequence.keras"


# 🔮 Transformer encoder (same as training)
def transformer_encoder(x, embed_dim, num_heads, ff_dim, dropout=0.1):
    attn_output = layers.MultiHeadAttention(
        num_heads=num_heads,
        key_dim=embed_dim,
        dropout=dropout
    )(x, x)

    x = layers.Add()([x, attn_output])
    x = layers.LayerNormalization()(x)

    ffn = layers.Dense(ff_dim, activation="relu")(x)
    ffn = layers.Dense(embed_dim)(ffn)

    x = layers.Add()([x, ffn])
    x = layers.LayerNormalization()(x)
    return x


# 🌱 Rebuild the exact model architecture
def build_model(IMG_SIZE, num_classes):
    cnn_base = tf.keras.applications.MobileNetV2(
        include_top=False,
        input_shape=IMG_SIZE + (3,),
        weights="imagenet"
    )
    cnn_base.trainable = False

    cnn_features = cnn_base.output
    seq = layers.Reshape((-1, cnn_features.shape[-1]))(cnn_features)

    embed_dim = 256
    seq = layers.Dense(embed_dim)(seq)

    positions = tf.range(start=0, limit=49, delta=1)
    pos_embed = layers.Embedding(input_dim=49, output_dim=embed_dim)(positions)
    seq = seq + pos_embed

    x = transformer_encoder(seq, embed_dim, num_heads=4, ff_dim=512)
    x = transformer_encoder(x, embed_dim, num_heads=4, ff_dim=512)

    x = layers.GlobalAveragePooling1D()(x)
    x = layers.Dropout(0.3)(x)

    disease_out = layers.Dense(num_classes, activation='softmax', name="disease_output")(x)
    symptom_out = layers.Dense(10, activation='sigmoid', name="symptom_output")(x)

    model = models.Model(inputs=cnn_base.input, outputs=[disease_out, symptom_out])
    return model


# 🧪 Build model and load weights
model = build_model(IMG_SIZE, NUM_CLASSES)
model.load_weights(H5_PATH)

# 💎 Save in native Keras format
model.save(KERAS_PATH)

print(f"✅ Converted {H5_PATH} → {KERAS_PATH}")
