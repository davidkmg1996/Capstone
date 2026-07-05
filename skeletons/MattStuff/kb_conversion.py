import json

INPUT_FILE = "kb2.json"

OUTPUT_DISEASES = "disease_symptoms.json"
OUTPUT_SYMPTOMS = "symptom_index.json"


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

flat_entries = []
symptom_set = set()

# 🔍 Extract plant/disease/symptoms
for disease_name, entries in data["diseases"].items():
    for entry in entries:
        plant = entry["plant"]
        disease = entry["disease"]
        symptoms = entry["symptom"]

        flat_entries.append({
            "plant": plant,
            "disease": disease,
            "symptoms": symptoms
        })

        for s in symptoms:
            symptom_set.add(s)


# 🌿 Build symptom vocabulary
symptom_list = sorted(symptom_set)

symptom_index = {
    symptom: idx for idx, symptom in enumerate(symptom_list)
}


# 💾 Save flattened disease list
with open(OUTPUT_DISEASES, "w", encoding="utf-8") as f:
    json.dump(flat_entries, f, indent=2)


# 💾 Save symptom vocabulary
with open(OUTPUT_SYMPTOMS, "w", encoding="utf-8") as f:
    json.dump(symptom_index, f, indent=2)


print("✅ Conversion complete")
print(f"{len(flat_entries)} disease entries written to {OUTPUT_DISEASES}")
print(f"{len(symptom_index)} unique symptoms written to {OUTPUT_SYMPTOMS}")
