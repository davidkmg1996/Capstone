import os
import random
import json
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# ====== CONFIG ======
BASE_DIR = r"PlantVillage"  # change this
JSON_PATH = "labels.json"
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")

CHECKBOX_LABELS = ['Tan', 'Sunken', 'Black-Lesions', 'Black-Veins', 'Rotting', 'Brown', 'Wilt', 'Blotchy', 'Healthy', 'Oily', 'Yellow', 'Greasy', 'Black', 'Scorched', 'Purple', 'Brown-Lesions', 'Watery', 'Halo', 'Spots', 'Distortion', 'Sunscald', 'Powdery', 'Fuzzy', 'Elliptical-Lesions', 'Parallel-Lesions', 'Green-Lesions', 'Spores', 'Yellow-Lesions', 'Discolored-Streaks', 'White-Mold', 'Circular', 'Rings', 'Collapsed', 'Shriveled', 'Black-Specks', 'Discolored']

# ====================


def load_existing_labels():
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_labels(data):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


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

        self.checkbox_vars = []
        self.current_image_path = None

        self.main_frame = ttk.Frame(root, padding=10)
        self.main_frame.pack(fill="both", expand=True)

        self.image_label = ttk.Label(self.main_frame)
        self.image_label.grid(row=0, column=0, rowspan=20, padx=(0, 15))

        for i, label in enumerate(CHECKBOX_LABELS):
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.main_frame, text=label, variable=var)
            cb.grid(row=i, column=1, sticky="w", pady=2)
            self.checkbox_vars.append(var)

        self.next_button = ttk.Button(
            self.main_frame, text="Next Image ➡️", command=self.next_image
        )
        self.next_button.grid(
            row=len(CHECKBOX_LABELS) + 1, column=1, pady=(10, 0), sticky="w"
        )

        self.load_new_image()

    def load_new_image(self):
        try:
            self.current_image_path = get_random_image(BASE_DIR, self.data)

            img = Image.open(self.current_image_path)
            img.thumbnail((800, 800), Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)

            self.image_label.configure(image=self.photo)

            for var in self.checkbox_vars:
                var.set(False)

        except ValueError as e:
            self.image_label.configure(text=str(e), image="")
            self.next_button.config(state="disabled")

    def next_image(self):
        if self.current_image_path:
            labels = {
                CHECKBOX_LABELS[i]: var.get()
                for i, var in enumerate(self.checkbox_vars)
            }

            self.data[self.current_image_path] = labels
            save_labels(self.data)

        self.load_new_image()


if __name__ == "__main__":
    root = tk.Tk()
    app = LabelApp(root)
    root.mainloop()
