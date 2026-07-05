import os
import json

# ====== CONFIG ======
BASE_DIR = r"PlantVillage"
JSON_PATH = "labels.json"

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")

ALL_SYMPTOMS = ['Tan', 'Sunken', 'Black-Lesions', 'Black-Veins', 'Rotting', 'Brown', 'Wilt', 'Blotchy', 'Healthy', 'Oily', 'Yellow', 'Greasy', 'Black', 'Scorched', 'Purple', 'Brown-Lesions', 'Watery', 'Halo', 'Spots', 'Distortion', 'Sunscald', 'Powdery', 'Fuzzy', 'Elliptical-Lesions', 'Parallel-Lesions', 'Green-Lesions', 'Spores', 'Yellow-Lesions', 'Discolored-Streaks', 'White-Mold', 'Circular', 'Rings', 'Collapsed', 'Shriveled', 'Black-Specks', 'Discolored']

# ====================


def load_labels():
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_labels(data):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def is_healthy_folder(folder_name):
    return "healthy" in folder_name.lower()


def find_healthy_images(base_dir):
    healthy_images = []

    for root, dirs, files in os.walk(base_dir):
        folder_name = os.path.basename(root)

        if is_healthy_folder(folder_name):
            for file in files:
                if file.lower().endswith(IMAGE_EXTENSIONS):
                    healthy_images.append(os.path.join(root, file))

    return healthy_images


def main():
    labels = load_labels()

    healthy_images = find_healthy_images(BASE_DIR)

    added = 0
    skipped = 0

    for img_path in healthy_images:
        if img_path in labels:
            skipped += 1
            continue

        labels[img_path] = {symptom: False for symptom in ALL_SYMPTOMS}
        added += 1

    save_labels(labels)

    print(f"Added {added} healthy images.")
    print(f"Skipped {skipped} already labeled images.")
    print("All symptoms set to False 🌱")


if __name__ == "__main__":
    main()
