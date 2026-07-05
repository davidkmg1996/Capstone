import os
import json
import torch
import clip
from PIL import Image
from tqdm import tqdm

# -----------------------------
# CONFIG
# -----------------------------
ROOT_DIR = "Plantvillage"
OUTPUT_FILE = "clip_labels.json"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

SYMPTOMS = [
  "Black",
  "Black Specks",
  "Blister",
  "Brown",
  "Brown Lesions",
  "Canker",
  "Circular",
  "Cluster",
  "Concentric",
  "Cracked",
  "Death",
  "Fuzzy",
  "Gray",
  "Greasy",
  "Green",
  "Green Lesions",
  "Growth",
  "Halo",
  "Pale",
  "Patches",
  "Powdery",
  "Purple",
  "Red",
  "Rings",
  "Rotting",
  "Shriveled",
  "Spores",
  "Spots",
  "Streaking",
  "Stunted",
  "Sunken",
  "Sunscald",
  "Tan",
  "Twisting",
  "Yellow"
]

THRESHOLD = 0.25  # adjust if needed



# ---------------------------------
# LOAD MODEL
# ---------------------------------
model, preprocess = clip.load("ViT-B/32", device=DEVICE)

# ---------------------------------
# PAIRED PROMPTS (KEY FIX 🔥)
# ---------------------------------
positive_prompts = [
    f"a close-up photo of a plant leaf showing {s}"
    for s in SYMPTOMS
]

negative_prompts = [
    f"a healthy plant leaf without any sign of {s}"
    for s in SYMPTOMS
]

with torch.no_grad():
    pos_tokens = clip.tokenize(positive_prompts).to(DEVICE)
    neg_tokens = clip.tokenize(negative_prompts).to(DEVICE)

    pos_features = model.encode_text(pos_tokens)
    neg_features = model.encode_text(neg_tokens)

    pos_features /= pos_features.norm(dim=-1, keepdim=True)
    neg_features /= neg_features.norm(dim=-1, keepdim=True)

# ---------------------------------
# INFERENCE
# ---------------------------------
results = []

image_files = []

for folder in os.listdir(ROOT_DIR):
    folder_path = os.path.join(ROOT_DIR, folder)

    if not os.path.isdir(folder_path):
        continue

    image_files_in_folder = [
        (folder, f)
        for f in os.listdir(folder_path)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    image_files.extend(image_files_in_folder)

for folder, fname in tqdm(image_files):
    img_path = os.path.join(ROOT_DIR, folder, fname)

    try:
        image = preprocess(Image.open(img_path).convert("RGB")).unsqueeze(0).to(DEVICE)

        with torch.no_grad():
            image_features = model.encode_image(image)
            image_features /= image_features.norm(dim=-1, keepdim=True)

            # ---------------------------------
            # PAIRWISE CONTRAST LOGITS
            # ---------------------------------
            pos_logits = image_features @ pos_features.T
            neg_logits = image_features @ neg_features.T

            logits = pos_logits - neg_logits

            probs = logits.sigmoid().cpu().numpy()[0]

        labels = []

        for symptom, prob in zip(SYMPTOMS, probs):
            if prob >= THRESHOLD:
                labels.append({
                    "symptom": symptom,
                    "confidence": float(prob)
                })

        results.append({
            "image": img_path,
            "disease_folder": folder,
            "labels": labels
        })

    except Exception as e:
        print(f"Error on {img_path}: {e}")

# ---------------------------------
# SAVE OUTPUT
# ---------------------------------
with open(OUTPUT_FILE, "w") as f:
    json.dump(results, f, indent=2)

print(f"💾 Saved to {OUTPUT_FILE}")
