import json
import os
import re
#This relies on the folder being structured as plantName__diseaseName
#Disease name on the folder needs to be exactly what is in the knowledgebase 
# Ex: folder named corn__common_rust would need to be changed to corn__rust, capitlization does not affect it
#create a backup copy of the folders before running or comment out line 40 (os.rename) to test before running


def main():
    dataset_path = input("Enter the path to your dataset folders: ").strip()

    if not os.path.exists(dataset_path):
        print("Path not found.")
        return
    #loop every folder in the dataset
    for folder_name in os.listdir(dataset_path):
        old_path=os.path.join(dataset_path,folder_name)

        if not os.path.isdir(old_path):
            continue
        if "__" not in folder_name:
            continue
        #seperate the plant from the disease name
        plant, disease=folder_name.split("__",1)
        disease=disease.strip()
        #return the symptoms of the disease
        disease=disease.replace("_"," ")
        symptoms=getSymptoms(disease)
        if not symptoms:
            print("No symptoms found for "+disease)
            continue
        #create new folder name
        
        symptom_string="_".join(symptoms)
        
        new_name = f"{plant}__{symptom_string}"
        new_path = os.path.join(dataset_path, new_name)
        #renames files, commented out for testing
        os.rename(old_path,new_path)
        print(f"renamed: {folder_name} to {new_name}")


        

#change pass disease from file name
def getSymptoms(disease):
     #open knowledge base
    with open("KB.json", "r") as file:
        kb = json.load(file)

    disease_symptoms = {}

    #Loop through symptoms
    for symptom, entries in kb["symptoms"].items():
        for entry in entries:

            if "disease" not in entry:
                continue

            if entry["disease"].lower() == disease.lower():
                # Add to result dictionary
                if disease not in disease_symptoms:
                    disease_symptoms[disease] = set()
                disease_symptoms[disease].add(symptom)

    #Print results
    if disease_symptoms:
        symptoms=[]
        print(f"\n Symptoms for {disease}:")
        for symptom in disease_symptoms[disease]:
            #removes all instances of white space with - and adds to list
            symptom = re.sub(r"\s+", "-", symptom.strip())
            print(f"- {symptom}")
            symptoms.append(symptom)
        return symptoms
    else:
        print(f"\n No symptoms found for '{disease}' in KB.json")

if __name__ == "__main__":
    main()
