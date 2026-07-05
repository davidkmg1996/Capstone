import os
import random
import json
import re
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# ====== CONFIG ======
BASE_DIR = r"PlantVillage"  # change if needed
LABELS_JSON_PATH = "labels.json"
DISEASE_JSON_PATH = "disease_symptoms.json"

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")

CHECKBOX_LABELS = [
    'Tan', 'Sunken', 'Black-Lesions', 'Black-Veins', 'Rotting', 'Brown',
    'Wilt', 'Blotchy', 'Healthy', 'Oily', 'Yellow', 'Greasy', 'Black',
    'Scorched', 'Purple', 'Brown-Lesions', 'Watery', 'Halo', 'Spots',
    'Distortion', 'Sunscald', 'Powdery', 'Fuzzy', 'Elliptical-Lesions',
    'Parallel-Lesions', 'Green-Lesions', 'Spores', 'Yellow-Lesions',
    'Discolored-Streaks', 'White-Mold', 'Circular', 'Rings', 'Collapsed',
    'Shriveled', 'Black-Specks', 'Discolored'
]

# ====================

def get_all_symptoms(disease_map):
    all_symptoms = set()

    for symptoms in disease_map.values():
        all_symptoms.update(symptoms)

    return sorted(all_symptoms)


# 😈 Normalize everything into the same submissive format
def normalize(text):
    text = text.lower()
    text = re.sub(r"\(.*?\)", "", text)
    text = text.replace("_", " ").replace("-", " ")
    text = text.replace(",", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_existing_labels():
    data = []
    if os.path.exists(LABELS_JSON_PATH):
        with open(LABELS_JSON_PATH, "r", encoding="utf-8") as f:
            for line in f:
                data.append(json.loads(line))
    return data


def save_labels(data):
    with open(LABELS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# 🌿 Load disease → symptom mapping
def load_disease_map():
    with open(DISEASE_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    mapping = {}

    for entry in data:
        plant = normalize(entry["plant"])
        disease = normalize(entry["disease"])

        # store ORIGINAL symptom names (pretty UI)
        original_symptoms = set(entry["symptoms"])

        # normalized for matching
        normalized_symptoms = set(normalize(s) for s in entry["symptoms"])

        mapping[(plant, disease)] = {
            "original": original_symptoms,
            "normalized": normalized_symptoms
        }
    return mapping


# 🧬 Extract plant + disease from folder
def parse_folder_name(folder_name):
    plant, disease = folder_name.split("___")
    return normalize(plant), normalize(disease)


# 💋 Handle messy naming mismatches
def find_best_match(plant, disease, disease_map):
    for (p, d) in disease_map:
        if p == plant and (disease in d or d in disease):
            return disease_map[(p, d)], d
    return None, None

def get_random_image(base_dir, labeled_data):
    subdirs = [
        os.path.join(base_dir, d)
        for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d))
    ]

    random.shuffle(subdirs)

    for subdir in subdirs:
        images = [
            os.path.join(subdir, f)
            for f in os.listdir(subdir)
            if f.lower().endswith(IMAGE_EXTENSIONS)
        ]

        random.shuffle(images)

        for img in images:
            if img not in labeled_data:
                return img

    raise ValueError("No unlabeled images left 🎉")


class LabelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Plant Symptom Labeller 🌿")
        

        self.data = load_existing_labels()
        self.disease_map = load_disease_map()

        self.all_symptoms = get_all_symptoms({k: v["original"] for k, v in self.disease_map.items()})

        self.checkbox_vars = []
        self.checkboxes = []
        self.checkbox_labels = self.all_symptoms
        self.current_image_path = None

        self.main_frame = ttk.Frame(root, padding=10)
        self.main_frame.pack(fill="both", expand=True)

        self.image_label = ttk.Label(self.main_frame)
        self.image_label.grid(row=0, column=0, rowspan=50, padx=(0, 15))

        self.info_label = ttk.Label(self.main_frame, font=("Arial", 12, "bold"))
        self.info_label.grid(row=0, column=1, columnspan=2, sticky="w", pady=(0, 10))

        # create checkboxes
        for i, label in enumerate(CHECKBOX_LABELS):
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.main_frame, text=label, variable=var)
            cb.grid(row=i, column=1, sticky="w", pady=2)

            self.checkbox_vars.append(var)
            self.checkboxes.append(cb)

        self.next_button = ttk.Button(
            self.main_frame, text="Next Image ➡️", command=self.next_image
        )
        self.next_button.grid(
            row=len(CHECKBOX_LABELS) + 1, column=1, pady=(10, 0), sticky="w"
        )

        self.skip_button = ttk.Button(
            self.main_frame,
            text="Skip Image ⏭️",
            command=self.skip_image
        )

        self.skip_button.grid(
            row=len(CHECKBOX_LABELS) + 2,
            column=1,
            pady=(5, 0),
            sticky="w"
        )

        self.load_new_image()

    def skip_image(self):
        # just reset UI state, do NOT save anything
        self.reset_checkboxes()
        self.load_new_image()


    def reset_checkboxes(self):
        for var in self.checkbox_vars:
            var.set(False)

        for cb in self.checkboxes:
            cb.grid()

    def load_new_image(self):
        self.reset_checkboxes()

        self.is_healthy = True
        while self.is_healthy:
            try:
                self.current_image_path = get_random_image(BASE_DIR, self.data)

                img = Image.open(self.current_image_path)
                img.thumbnail((800, 800), Image.LANCZOS)
                self.photo = ImageTk.PhotoImage(img)

                self.image_label.configure(image=self.photo, text="")

                # 🌿 Extract plant + disease
                folder_name = os.path.basename(os.path.dirname(self.current_image_path))
                plant, disease = parse_folder_name(folder_name)

                # 😈 Get valid symptoms
                valid_entry, matched_disease = find_best_match(plant, disease, self.disease_map)

                if valid_entry is None:
                    self.info_label.config(
                        text=f"Unmatched: {plant.title()} | {disease.title()}"
                    )
                    valid_symptoms = set()
                else:
                    valid_symptoms = valid_entry["normalized"]
                
                if valid_entry:
                    self.is_healthy = False
                    valid_symptoms = valid_entry["normalized"]
                    original_symptoms = valid_entry["original"]
                else:
                    valid_symptoms = set()
                    original_symptoms = set()

                self.info_label.config(
                text=f"Plant: {plant.title()}    |    Disease: {matched_disease.title()}"
                )

                # 💜 Show/hide checkboxes
                for i, label in enumerate(CHECKBOX_LABELS):
                    norm_label = normalize(label)

                    if norm_label in valid_symptoms:
                        self.checkboxes[i].grid()
                    else:
                        self.checkboxes[i].grid_remove()

                    self.checkbox_vars[i].set(False)

            except ValueError as e:
                self.image_label.configure(text=str(e), image="")
                self.next_button.config(state="disabled")

    def next_image(self):
        if self.current_image_path:
            labels = {
                CHECKBOX_LABELS[i]: var.get()
                for i, var in enumerate(self.checkbox_vars)
            }

            save_label_entry(self.current_image_path, labels)

        self.load_new_image()

def save_label_entry(image_path, labels):
    entry = {
        "path": image_path,
        "labels": labels
    }

    with open(LABELS_JSON_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
if __name__ == "__main__":
    root = tk.Tk()
    app = LabelApp(root)
    root.mainloop()
