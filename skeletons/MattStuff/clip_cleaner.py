import json
import re
from collections import Counter

CLIP_FILE = "clip_labels.json"
SCHEMA_FILE = "disease_symptoms.json"
OUTPUT_FILE = "clip_labels_cleaned.json"


# ---------------------------------
# NORMALIZE ONLY TEXT PARTS
# (NOT STRUCTURE)
# ---------------------------------
def norm_text(s):
    s = s.lower()

    # 🔥 STEP 1: convert underscores INTO spaces FIRST
    s = s.replace("_", " ")

    # 🔥 STEP 2: remove punctuation but keep spaces
    s = re.sub(r"[^a-z0-9 ]+", " ", s)

    # 🔥 STEP 3: collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()

    return s


def norm_folder(folder):
    if "___" in folder:
        plant, disease = folder.split("___", 1)
    else:
        plant, disease = folder, ""

    return f"{norm_text(plant)}___{norm_text(disease)}"


# ---------------------------------
# LOAD
# ---------------------------------
with open(CLIP_FILE, "r", encoding="utf-8") as f:
    clip_data = json.load(f)

with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
    schema = json.load(f)


# ---------------------------------
# BUILD SCHEMA MAP (CORRECTED)
# ---------------------------------
allowed = {}

for entry in schema:
    plant = norm_text(entry["plant"])
    disease = norm_text(entry["disease"])

    key = f"{plant}___{disease}"

    allowed[key] = set(norm_text(s) for s in entry["symptoms"])


print("\n💜 SCHEMA KEYS SAMPLE:")
for k in list(allowed.keys())[:10]:
    print(" ", k)


# ---------------------------------
# CLEAN
# ---------------------------------
cleaned = []
missing = Counter()

for item in clip_data:

    raw_folder = item["disease_folder"]
    folder = norm_folder(raw_folder)

    print("\n---------------------------------")
    print("RAW:", raw_folder)
    print("NORM:", folder)

    if folder not in allowed:
        print("❌ NO MATCH")
        missing[folder] += 1
        cleaned.append(item)
        continue

    valid = allowed[folder]

    print(f"✅ MATCH ({len(valid)} symptoms)")

    filtered = []

    for label in item["labels"]:
        sym = norm_text(label["symptom"])

        if sym in valid:
            filtered.append(label)
        else:
            print("   🗑️ DROP:", label["symptom"])

    print(f"KEPT {len(filtered)} / {len(item['labels'])}")

    cleaned.append({
        "image": item["image"],
        "disease_folder": item["disease_folder"],
        "labels": filtered
    })


# ---------------------------------
# SUMMARY
# ---------------------------------
print("\n💜 SUMMARY")
print("Missing matches:", len(missing))
print("Top:", missing.most_common(5))

# ---------------------------------
# SAVE
# ---------------------------------
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(cleaned, f, indent=2)

print("\n💾 Saved:", OUTPUT_FILE)
