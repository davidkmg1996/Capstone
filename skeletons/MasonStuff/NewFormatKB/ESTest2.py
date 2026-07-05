import json
from experta import KnowledgeEngine, Fact, Rule, MATCH,AS,NOT
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

class DiseaseProfile(Fact):
    pass

class Confidence(Fact):
    pass
class HumidityChecked(Fact):
    pass
class temperatureChecked(Fact):
    pass
class wetnessChecked(Fact):
    pass
    
def load_json(fPath):
    with open(fPath) as f:
        return json.load(f)

def getPriors(kb):
    dCounts = Counter()
    for disease_name, entry_list in kb.get("diseases", {}).items():
        for entry in entry_list:
            symptomCount = len(entry.get("symptom", []))
            dCounts[disease_name] += symptomCount

    total = sum(dCounts.values())

    return {disease: dCounts[disease] / total for disease in dCounts}

def getLikelihood(kb):
    DSCounts = defaultdict(Counter)
    DTotals = Counter()
    totalSymptoms = []

    for disease_name, entries in kb["diseases"].items():
        for entry in entries:
            for symptom in entry["symptom"]:
                if symptom not in totalSymptoms:
                    totalSymptoms.append(symptom)
                

                DSCounts[disease_name][symptom]+=1
                DTotals[disease_name]+=1

    V = len(totalSymptoms)

    likelihood = {}

    for disease, sCounts in DSCounts.items():
        total = DTotals[disease]
        likelihood[disease] = {symptom: (sCounts.get(symptom, 0) + 1) / (total + V)
        for symptom in totalSymptoms
        }

    return likelihood

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
        
        self.priors = getPriors(self.kb)
        self.likelihood = getLikelihood(self.kb)

    @Rule(symptomatic(name=MATCH.name, symptoms=MATCH.symptoms))
    def getSymptoms(self, name, symptoms):
        self.currentPlant = name
        self.getSymptomNames = symptoms
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

        # Calculate possible diseases
        dList = []
        for disease_name, entry_list in self.kb["diseases"].items():
            for entry in entry_list:
                # check if plant matches
                if entry.get("plant") == name:
            # check if ANY of the user's symptoms match this disease's symptoms
                    if any(sListItem in entry.get("symptom", []) for sListItem in symptomList):
                        dList.append(entry.get("disease"))

        posteriors = {}
        for disease, prior in self.priors.items():
            prob = prior
            for s in symptoms:
                prob *= self.likelihood[disease].get(s, 1e-6)
            posteriors[disease] = prob

        # normalize after the loop
        totalProb = sum(posteriors.values())
        posteriors = {d: round(p/totalProb * 100, 2) for d, p in posteriors.items()}


        # Calculate probabilities
        #cDisease = [disease for disList in dList for disease in disList]
        #total_count = len(cDisease)
        #count = Counter(cDisease)
        #probabilities = {d: round(total / total_count * 100, 2) for d, total in count.items()}
        #pString = ", ".join([f"{p}%" for p in probabilities.values()])
        count = Counter(dList)
        total = len(dList)
        probability = sorted(posteriors.items(), key=lambda x: x[1], reverse=True)[:5]
        #lookup managment and classification for highest probability disease
        highest_prob = max(posteriors.items(), key=lambda x: x[1])
        disease_name = highest_prob[0].lower().strip()
        plant_name = self.currentPlant.lower().strip()
        management="No managment information is currently known"
        classification="unknown"
        found=False
        for disease_key, entry_list in self.kb["diseases"].items():
            if disease_key.lower().strip() == disease_name:
                for entry in entry_list:
            # Skip empty dicts like {}
                    if not entry:
                        continue

                    if entry.get("plant", "").lower().strip() == plant_name:
                        if "management" in entry:
                            management = entry.get("management", "")
                        if "type" in entry:
                            classification = entry.get("type", "")
                    found = True
                    break
            if found:
                break

        self.results = {
            "Plant": name,
            "Probability": probability,
            "Management": management,
            "Classification": classification
        }

        #return {"plant": name, "diseases": list(set(cDisease)), "probabilities": probabilities}

class confirmDiagnosis(KnowledgeEngine):
    def __init__(self, kb):
        super().__init__()
        self.kb = kb
        self.currentPlant = None
        self.currentDiagnosis = None

    @Rule(backChain(name=MATCH.name, preDiagnosis=MATCH.preDiagnosis))
    def getDiagnosis(self, name, preDiagnosis):
        self.currentPlant = name
        self.currentDiagnosis = preDiagnosis
        symptoms = self.kb.get("symptoms", {})
        symptomList = []
        for disease_key, entry_list in self.kb.get("diseases", {}).items():
        # check if disease key matches preDiagnosis
            if disease_key.lower().strip() == preDiagnosis.lower().strip():
                for entry in entry_list:
                    if not entry:
                        continue
                # check if plant matches
                    if entry.get("plant", "").lower().strip() == name.lower().strip():
                        symptomList.extend(entry.get("symptom", []))
        print(symptomList)
        return {
        "plant": name, 
        "diagnosis": preDiagnosis, 
        "symptoms": list(set(symptomList))
        }
class confirmEnvironment(KnowledgeEngine):
    def __init__(self, kb):
        super().__init__()
        self.kb=kb
        self.results={
            "Temperature": False,
            "Humidity": False,
            "Wetness": False,
            }
    @Rule(Disease(name=MATCH.name, plant=MATCH.plant))
    def load_profiles(self, name, plant):
        diseases=self.kb["diseases"]
     #   print(diseases)
        if name not in diseases:
            print("Disease not in KB")
            return
        for entry in diseases[name]:
            if entry["plant"]==plant:
                self.declare(DiseaseProfile(
                    name=name,
                    plant=plant,
                    temperature=entry.get("temperature"),
                    humidity=entry.get("humidity"),
                    wetness=entry.get("lengthOfWetness")
                ))
               # print(entry)
                #print(entry.get("temperature"))
                self.declare(Confidence(score=0))
                return
        print("Disease exists but not for this plant")
        return
    #temperature rule
    @Rule(
    DiseaseProfile(name=MATCH.name,
                    temperature=MATCH.temp_range),
    Environment(temperature=MATCH.userTemp),
    AS.c<<Confidence(score=MATCH.score),
    NOT(temperatureChecked())
    )
    def check_temperature(self, name, temp_range, userTemp,c, score):
        if userTemp is None:
            print("No user data for temperature")
            self.results["Temperature"]=None
            return
        if temp_range == "None":
            print("Disease is not affected by temperature")
            self.results["Temperature"]=None
            return
        
        lower=temp_range[0]
        upper=temp_range[1]
        #    lower, upper = temp_range
        print(lower)
        print(upper)
        if lower <= userTemp <= upper:
            print("Temperature improves confidence")
            self.modify(c, score=score + 1)
            self.results["Temperature"]=True
        else:
            print("Temperature lowers confidence")
            self.modify(c, score=score - 1)
        self.declare(temperatureChecked())

    # Humidity Rule
    @Rule(
        DiseaseProfile(humidity=MATCH.kbHumidity),
        Environment(humidity=MATCH.userHumidity),
       AS.c << Confidence(score=MATCH.score),
       NOT(HumidityChecked())
    )
    def check_humidity(self, kbHumidity, userHumidity,c, score):
       # print("humidity: ")
      #  print(kbHumidity)
        #userHumidity=self.classify_humidity(userHumidity)

        if userHumidity is None:
            print("No user data for humidity")
            self.results["Humidity"]=None
            return

        if kbHumidity == "None":
            print("Disease is not affected by humidity")
            self.results["Humidity"]=None
            return
            

        if userHumidity == kbHumidity:
            print("Humidity improves confidence")
            self.modify(c, score=score + 1)
            self.results["Humidity"]=True
        else:
            print("Humidity lowers confidence")
            self.modify(c, score=score - 1)
        self.declare(HumidityChecked())

    # Wetness Rule
    @Rule(
        DiseaseProfile(wetness=MATCH.kbWetness),
        Environment(wetness=MATCH.userWetness),
        AS.c << Confidence(score=MATCH.score),
        NOT(wetnessChecked())
    )
    def check_wetness(self, kbWetness, userWetness,c, score):
        if userWetness is None:
            print("No user data for length of wetness")
            self.results["Wetness"]=None
            return
        if kbWetness == "None":
            print("Disease is not affected by length of wetness")
            self.results["Wetness"]=None
            return
        
        #print("kbwetness: ")
        #print(kbWetness)
        if userWetness >= int(kbWetness):
            print("Wetness improves confidence")
            self.modify(c, score=score + 1)
            self.results["Wetness"]=True
        else:
            print("Wetness lowers confidence")
            self.modify(c, score=score - 1)
        self.declare(wetnessChecked())

    #confidence rule
    @Rule(Confidence(score=MATCH.score))
    def final_result(self, score):
        print("Final confidence score:", score)

        if score >= 2:
            print("Environment CONFIRMS disease")
        else:
            print("Environment does NOT confirm disease")

        self.halt()

def classify_humidity(relative_humidity: float )-> str:
    if relative_humidity >= 81:
        return "high"

    if 61 <= relative_humidity <= 80:
        return "moderate"

    if relative_humidity <= 60:
        return "low"

    return "unknown"
    
if __name__=="__main__":
    #backchain test
    plant="Tomato"
    KB_FILE = "kb2.json"
    kb_data = load_json(KB_FILE)
    engine=confirmDiagnosis(kb_data)
    engine.reset()
    engine.declare(backChain(name="Tomato",preDiagnosis="Bacterial spot"))
    engine.run()

   #print(engine.currentPlant)
   #print(engine.currentDiagnosis)

    #diagnose test
    plant_name="Tomato"
    symptom_list=set()
    symptom_list.add("Canker")
    symptom_list.add("Brown")
    symptom_list.add("Rings")
    engine = MultiSymptom(kb_data)
    engine.reset()
    engine.declare(symptomatic(name=plant_name, symptoms=symptom_list))
    engine.run()
    print(engine.results)

    #environment test
    engine = confirmEnvironment(kb_data)
    engine.reset()

    engine.declare(Disease(name="Bacterial spot", plant="Tomato"))

    engine.declare(Environment(
        temperature=75,
        humidity=classify_humidity(90),
        wetness=8
    ))
    engine.run()
        

