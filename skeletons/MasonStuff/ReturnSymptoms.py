import json

def main():
    #open knowledge base
    with open("KB.json", "r") as file:
        kb = json.load(file)
    plant= input("Enter plant name: ").strip()
    disease = input("Enter a disease name: ").strip()

    disease_symptoms = {}

    #Loop through symptoms
    for symptom, entries in kb["symptoms"].items():
        for entry in entries:

            if "disease" not in entry:
                continue

            if entry["disease"].lower() == disease.lower() and entry["plant"].lower()==plant.lower():
                # Add to result dictionary
                if disease not in disease_symptoms:
                    disease_symptoms[disease] = set()
                disease_symptoms[disease].add(symptom)

    #Print results
    if disease_symptoms:
        print(f"\n Symptoms for {disease}:")
        for symptom in disease_symptoms[disease]:
            print(f"- {symptom}")
    else:
        print(f"\n No symptoms found for '{disease}' in KB.json")

    

if __name__ == "__main__":
    main()
