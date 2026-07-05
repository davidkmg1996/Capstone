#!/usr/bin/env python3
"""
Evaluate a trained PlantVillage model (.h5) on the validation split and report
accuracy, precision, recall, f1 (macro + weighted), plus a per-class report.

Matches the training data loader:
- image_dataset_from_directory(... validation_split=0.2, subset="validation", seed=123)
- label_mode="categorical"
"""

import argparse
import numpy as np
import tensorflow as tf


def load_val_data(dataset_dir: str, img_size=(224, 224), batch_size=32, seed=123):
    val_ds = tf.keras.preprocessing.image_dataset_from_directory(
        dataset_dir,
        validation_split=0.2,
        subset="validation",
        seed=seed,
        image_size=img_size,
        batch_size=batch_size,
        label_mode="categorical",
        shuffle=False,  # IMPORTANT: keep deterministic order for evaluation
    )
    class_names = val_ds.class_names
    val_ds = val_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
    return val_ds, class_names


def add_dummy_symptom_labels(ds, num_symptoms=10):
    # Same dummy wrapper style you used in training
    for x, y in ds:
        dummy_symptoms = tf.zeros((tf.shape(y)[0], num_symptoms), dtype=tf.float32)
        yield x, {"disease_output": y, "symptom_output": dummy_symptoms}


def wrap_with_dummies(ds, num_classes, img_size, num_symptoms=10):
    return tf.data.Dataset.from_generator(
        lambda: add_dummy_symptom_labels(ds, num_symptoms=num_symptoms),
        output_signature=(
            tf.TensorSpec(shape=(None, img_size[0], img_size[1], 3), dtype=tf.float32),
            {
                "disease_output": tf.TensorSpec(shape=(None, num_classes), dtype=tf.float32),
                "symptom_output": tf.TensorSpec(shape=(None, num_symptoms), dtype=tf.float32),
            },
        ),
    )


def confusion_matrix(y_true, y_pred, num_classes):
    cm = np.zeros((num_classes, num_classes), dtype=np.int64)
    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1
    return cm


def precision_recall_f1_from_cm(cm):
    # cm rows = true, cols = pred
    tp = np.diag(cm).astype(np.float64)
    fp = cm.sum(axis=0) - tp
    fn = cm.sum(axis=1) - tp
    support = cm.sum(axis=1).astype(np.float64)

    precision = np.divide(tp, tp + fp, out=np.zeros_like(tp), where=(tp + fp) != 0)
    recall = np.divide(tp, tp + fn, out=np.zeros_like(tp), where=(tp + fn) != 0)
    f1 = np.divide(
        2 * precision * recall,
        precision + recall,
        out=np.zeros_like(tp),
        where=(precision + recall) != 0,
    )

    return precision, recall, f1, support


def macro_avg(x):
    return float(np.mean(x)) if len(x) else 0.0


def weighted_avg(x, w):
    wsum = np.sum(w)
    return float(np.sum(x * w) / wsum) if wsum != 0 else 0.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", type=str, default="plant_disease_model_sequence.h5",
                        help="Path to the saved .h5 model")
    parser.add_argument("--dataset-dir", type=str, default="PlantVillage",
                        help="PlantVillage dataset directory (same structure as training)")
    parser.add_argument("--img-width", type=int, default=224)
    parser.add_argument("--img-height", type=int, default=224)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--num-symptoms", type=int, default=10)
    parser.add_argument("--topk", type=int, default=0,
                        help="If >0, also compute top-k accuracy for this k.")
    args = parser.parse_args()

    img_size = (args.img_width, args.img_height)

    # Load model
    model = tf.keras.models.load_model(args.model_path, compile=False)

    # Load validation data (same split as training)
    val_ds, class_names = load_val_data(
        args.dataset_dir, img_size=img_size, batch_size=args.batch_size, seed=args.seed
    )
    num_classes = len(class_names)

    # Wrap with dummy symptom labels so model can run with the same I/O structure
    val_ds_with_dummy = wrap_with_dummies(
        val_ds, num_classes=num_classes, img_size=img_size, num_symptoms=args.num_symptoms
    )

    # Collect predictions + true labels
    y_true = []
    y_pred = []

    for x_batch, y_dict in val_ds_with_dummy:
        y_true_batch = tf.argmax(y_dict["disease_output"], axis=1).numpy()

        outputs = model.predict(x_batch, verbose=0)
        # outputs could be list [disease, symptom] or dict; handle both
        if isinstance(outputs, dict):
            disease_probs = outputs["disease_output"]
        else:
            disease_probs = outputs[0]

        y_pred_batch = np.argmax(disease_probs, axis=1)

        y_true.extend(y_true_batch.tolist())
        y_pred.extend(y_pred_batch.tolist())

    y_true = np.array(y_true, dtype=np.int64)
    y_pred = np.array(y_pred, dtype=np.int64)

    # Accuracy
    acc = float(np.mean(y_true == y_pred))

    # Optional top-k accuracy
    topk_acc = None
    if args.topk and args.topk > 0:
        k = int(args.topk)
        # Need probs again for top-k; easiest is a second pass.
        correct = 0
        total = 0
        for x_batch, y_dict in val_ds_with_dummy:
            true_idx = tf.argmax(y_dict["disease_output"], axis=1).numpy()
            outputs = model.predict(x_batch, verbose=0)
            probs = outputs["disease_output"] if isinstance(outputs, dict) else outputs[0]
            topk = np.argsort(probs, axis=1)[:, -k:]
            for t, tk in zip(true_idx, topk):
                correct += int(t in tk)
            total += len(true_idx)
        topk_acc = float(correct / total) if total else 0.0

    # Confusion matrix + PRF
    cm = confusion_matrix(y_true, y_pred, num_classes=num_classes)
    precision, recall, f1, support = precision_recall_f1_from_cm(cm)

    macro_p = macro_avg(precision)
    macro_r = macro_avg(recall)
    macro_f1 = macro_avg(f1)

    weighted_p = weighted_avg(precision, support)
    weighted_r = weighted_avg(recall, support)
    weighted_f1 = weighted_avg(f1, support)

    # Print summary
    print("\n=== Overall Metrics (disease_output) ===")
    print(f"Accuracy: {acc:.4f}")
    if topk_acc is not None:
        print(f"Top-{args.topk} Accuracy: {topk_acc:.4f}")
    print(f"Macro Precision:   {macro_p:.4f}")
    print(f"Macro Recall:      {macro_r:.4f}")
    print(f"Macro F1:          {macro_f1:.4f}")
    print(f"Weighted Precision:{weighted_p:.4f}")
    print(f"Weighted Recall:   {weighted_r:.4f}")
    print(f"Weighted F1:       {weighted_f1:.4f}")

    # Per-class report
    print("\n=== Per-class Metrics ===")
    header = f"{'Class':40s} {'Prec':>8s} {'Rec':>8s} {'F1':>8s} {'Support':>10s}"
    print(header)
    print("-" * len(header))
    for i, name in enumerate(class_names):
        print(f"{name[:40]:40s} {precision[i]:8.4f} {recall[i]:8.4f} {f1[i]:8.4f} {int(support[i]):10d}")

    # Confusion matrix (optional: big!)
    print("\n=== Confusion Matrix (rows=true, cols=pred) ===")
    print(cm)


if __name__ == "__main__":
    main()
