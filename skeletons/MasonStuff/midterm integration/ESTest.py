import json
from experta import KnowledgeEngine, Fact, Rule, MATCH
from collections import Counter, defaultdict

class symptomatic(Fact):
    name = ""
    symptoms = []
    
class backChain(Fact):
    name = ""
    preDiagnosis = ""
class testTemp(Fact):
    name=""
    disease=""
class Environment(Fact):
    pass

class Disease(Fact):
    pass



    
def load_json(fPath):
    with open(fPath) as f:
        return json.load(f)


class MultiSymptom(KnowledgeEngine):
    def __init__(self, kb):
        super().__init__()
        self.kb = kb
        self.log = []
        self.valid_symptoms = set()
        self.symptomList = []
        self.currentPlant = None
        self.results = {}

        for symptomID, symptomInfo in self.kb.get('symptoms', {}).items():
            if 'name' in symptomInfo:
                self.valid_symptoms.add(symptomInfo['name'].lower())


    @Rule(symptomatic(name=MATCH.name, symptoms=MATCH.symptoms, temperature=MATCH.temperature, humidity=MATCH.humidity, lengthOfW=MATCH.lengthOfW))
    def getSymptoms(self, name, symptoms, temperature, humidity, lengthOfW):

        self.currentPlant = name
        self.getSymptomNames = list(symptoms.keys())
        symptomList = []
        totalSymptoms=[]
        for disease_name, entries in self.kb["diseases"].items():
            for entry in entries:
                for symptom in entry["symptom"]:
                    if symptom not in totalSymptoms:
                        totalSymptoms.append(symptom)

        for e2 in totalSymptoms:
            if e2 in self.getSymptomNames:
                symptomList.append(e2)

        # Validate symptoms
        for check in symptoms:
            if check not in symptomList:
                self.results = {"error": "One or more symptoms are invalid"}   

        # find possible diseases 
        dList = []
        for disease_name, entry_list in self.kb["diseases"].items():
            for entry in entry_list:
                # check if plant matches
                if entry.get("plant") == name:
            # check if ANY of the user's symptoms match this disease's symptoms
                    dList.append(entry)
      
        final_results={}
        for disease in dList:

            disease_symptoms = set(disease["symptom"])
            cf_symptoms = 0
            for symptom, confidence in symptoms.items():
                if symptom not in self.getSymptomNames:
            # User didn't report this symptom — don't fire the rule at all
                    continue
        
                if symptom in disease_symptoms:
            # User reported it AND it belongs to this disease → positive evidence
                    cf_symptoms = combine_cf(cf_symptoms, confidence)
                else:
            # User reported it AND it contradicts this disease → disbelief
                    cf_symptoms = combine_cf(cf_symptoms, -0.4)
              
              # get CF for each environmental factor
            env_values = []

            cf_temp = self.temperature_cf(disease.get("temperature"), temperature)
            cf_hum  = self.humidity_cf(disease.get("humidity"), humidity)
            cf_wet  = self.wetness_cf(disease.get("lengthOfWetness"), lengthOfW)

            # only include factors that returned a value
            for cf in [cf_temp, cf_hum, cf_wet]:
                if cf is not None:
                    env_values.append(cf)
            

            # combine environmental CFs
            cf_environment = 0
            for cf in env_values:
                cf_environment = combine_cf(cf_environment, cf)
            if len(env_values)==0:
                cf_environment=0
            else:
                cf_environment=sum(env_values)/len(env_values)

            # combine symptom and environment CFs
            cf_final = combine_cf(cf_symptoms, cf_environment)
            final_results[disease["disease"]] = cf_final

            top5 = sorted(final_results.items(), key=lambda x: x[1], reverse=True)[:5]
        #print("top5:",top5)

# Build a list of result entries with full disease info
        results_list = []
        for disease_name, cf_value in top5:
    # Find the matching disease entry to get management/type info
            disease_entry = next(
            (d for d in dList if d["disease"] == disease_name), 
            None
            )
            if disease_entry:
                entry = {
            "plant": name,
            "disease": disease_name,
            "probability": cf_value,
            "management": disease_entry["management"],
            "classification": disease_entry["type"]
            }
            results_list.append(entry)
        #with open("data.json", "w") as file:
        #    json.dump(results_list, file,indent=4)
        self.results = results_list

        

        

    # helper methods
    def temperature_cf(self, temp_range, userTemp):
        if temp_range == "None" or userTemp is None:
            return None
        lower, upper = temp_range[0], temp_range[1]
        if lower <= userTemp <= upper:
            return 0.8
        elif userTemp < lower - 5 or userTemp > upper + 5:
            return -0.2
        else:
            return 0.4

    def humidity_cf(self, kbHumidity, userHumidity):
        if kbHumidity == "None" or userHumidity is None:
            return None
        if userHumidity == kbHumidity:
            return 0.4
        else:
            return -0.2

    def wetness_cf(self, kbWetness, userWetness):
        if kbWetness == "None" or userWetness is None:
            return None
        if userWetness >= int(kbWetness):
            return 0.8
        else:
            return -0.2



def classify_humidity(relative_humidity: float )-> str:
    if relative_humidity >= 81:
        return "high"

    if 61 <= relative_humidity <= 80:
        return "moderate"

    if relative_humidity <= 60:
        return "low"

    return "unknown"
def combine_cf(cf1, cf2):
    if cf1>0 and cf2>0:
        return (cf1 + cf2) * (1 - cf1)
    elif cf1<0 and cf2<0:
        return (cf1 + cf2) * (1 + cf1)
    else:
        return (cf1+cf2)/(1-min(abs(cf1),abs(cf2)))
    

    #diagnose test
#    plant_name="Tomato"
#    symptoms={
#       "Sunscald": 0.80,
#        "Sunken": 0.80,
#        "Spots": 0.80,
#       "Blister": 0.80,   
#   }
#    engine = MultiSymptom(kb_data)
#    engine.reset()
#    engine.declare(symptomatic(name=plant_name, symptoms=symptoms, temperature=75,humidity=classify_humidity(90),lengthOfW=8))
#    engine.run()
#    print(engine.results)

   
         

