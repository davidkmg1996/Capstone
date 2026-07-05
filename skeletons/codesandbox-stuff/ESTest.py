# skeleton.py
import json
from experta import KnowledgeEngine, Fact, Rule, MATCH, P, Field
from fpdf import FPDF
import re


class Observation(Fact):
    pass

class symptomatic(Fact):
    name = ""
    symptoms = []


def load_json(fPath):
    with open(fPath) as f:
        return json.load(f)

class PlantDiagnosis(KnowledgeEngine):
    def __init__(self, kb):
        super().__init__()
        self.kb = kb
        self.log = []            
        self.pdf = FPDF()

    @Rule(Observation(plant=MATCH.plant, disease=MATCH.disease,
                      confidence=P(lambda c: c >= 0.7)))
    def diagnose(self, plant, disease):
        info = self.kb['Plants'].get(plant, {}).get(disease)
        self.log.append({"rule": "diagnose", "plant": plant,
                        "disease": disease, "kb_found": bool(info)})
        if not info:
            self.pdf.add_page()
            self.pdf.multi_cell(
                0, 10, f"Unknown disease {disease} for {plant}")
        else:
            self.pdf.add_page()
            text = f"Diagnosis: {info['name']}\n\nSymptoms:\n- " + \
                "\n- ".join(info['symptoms'])
            text += "\n\nRecommendations:\n- " + \
                "\n- ".join(info['treatments'])
            self.pdf.set_font("Arial", size=12)
            self.pdf.multi_cell(0, 10, text)
        self.pdf.output("diagnosis.pdf")

    @Rule(Observation(confidence=P(lambda c: c < 0.7)))
    def uncertain(self, confidence):
        self.log.append({"rule": "uncertain", "confidence": float(confidence)})
        self.pdf.add_page()
        self.pdf.set_font("Arial", size=12)
        self.pdf.multi_cell(
            0, 10, "Uncertain diagnosis. Please retake the photo or seek expert review.")
        self.pdf.output("diagnosis.pdf")

class MultiSymptom(KnowledgeEngine):
    def __init__(self, kb):
        super().__init__()
        self.kb = kb
        self.log = []            
        self.pdf = FPDF()

        self.valid_symptoms = set()

        self.symptomList = []
        self.currentPlant = None
        for symptomID, symptomInfo in self.kb.get('symptoms', {}).items():
            if 'name' in symptomInfo:
                self.valid_symptoms.add(symptomInfo['name'].lower())

        # print(f"Symptoms loaded: {self.valid_symptoms}")

        # print(f"Valid symptoms loaded: {self.valid_symptoms}")  

    @Rule(symptomatic(name=MATCH.name, symptoms = MATCH.symptoms))
    def getSymptoms(self, name, symptoms):
        # print(f"Rule with: name={name}, symptom={symptom}, symptom2={symptom2}")
        if self.currentPlant is None:
            self.currentPlant = name.lower()
            print(f"This is a {self.currentPlant}")

        if name.lower() != self.currentPlant:
            print(f"Ignoring symptom for plant '{name}' because current plant is '{self.currentPlant}'")
            return
        
        invalid = [s for s in symptoms if s.lower() not in self.valid_symptoms]
    
        if invalid:
            print(f"⚠️ Invalid symptoms provided: {invalid}")
            print(f"✅ Valid symptoms are: {sorted(self.valid_symptoms)}")
            return
    
        self.symptomList.extend(symptoms)
            # self.log.append({"rule": "collect_symptom", "symptom": symptom, "symptom 2": symptom2})
        print(f"You've indicated that the {self.currentPlant} has the symptoms {', '.join(symptoms)}")
            
            
            # for symptoms in collectedSymptoms:
            #     print(symptoms)
            
        diseases = self.kb.get('Plants', {}).get(name.lower(), {})
        userSymptoms = set(sym.lower() for sym in symptoms)
        for disease, info in diseases.items():
                dSymptoms = set(sym.lower() for sym in info.get('symptoms', []))
                # print(f"[DEBUG] for disease '{disease}': match1={match1} match2 = {match2}")
                if userSymptoms.issubset(dSymptoms):
                    print(f"Based on thse symptoms, the {self.currentPlant} has {disease}")
                else:
                    print("No match")



# class MultiSymptom(KnowledgeEngine):
#     def __init__(self, kb):
#         super().__init__()
#         self.kb = kb
#         self.log = []            # store fired-rule traces
#         self.pdf = FPDF()

#         self.valid_symptoms = set()

#         for symptomID, symptomInfo in self.kb.get('symptoms', {}).items():
#             if 'name' in symptomInfo:
#                 self.valid_symptoms.add(symptomInfo['name'])
            
#             self.symptomList = []
#             self.currentPlant = None

#     @Rule(symptomatic(name = MATCH.name, symptom = MATCH.symptom))
#     def getSymptoms(self, name, symptom):   
#         if self.currentPlant is None:
#             self.currentPlant = name
        
#         if name != self.currentPlant:
#             return
#         if symptom in self.valid_symptoms:
#             self.symptomList.append(symptom)
#             self.log.append({"rule": "collect_symptom", "symptom": symptom})
#         else:
#             print(f"Symptom '{symptom}' is invalid.")

    


    


# # Usage
# kb = load_json("KB.json")

# engine = PlantDiagnosis(kb)
# engine2 = MultiSymptom(kb)
# engine.reset()
# engine2.reset()
# # after model predicts:
# engine.declare(Observation(plant="Cassava",
#                disease="CassavaBlight", confidence=0.87))

# engine2.declare(symptomatic(name = "Tomato", symptom = "wilted"))

# engine.run()
# print(engine.log)   # show why the system decided what it did
