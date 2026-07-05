import json
from experta import KnowledgeEngine, Fact, Rule, MATCH
from collections import Counter, defaultdict

class symptomatic(Fact):
    name = ""
    symptoms = []
    
class backChain(Fact):
    name = ""
    preDiagnosis = ""
    
def load_json(fPath):
    with open(fPath) as f:
        return json.load(f)

def getPriors(kb):
    dCounts = Counter()
    for symptom, entries in kb.get("symptoms", {}).items():
        for entry in entries:
            disease = entry.get("disease")
            if disease:
                dCounts[disease] += 1

    total = sum(dCounts.values())

    return {disease: dCounts[disease] / total for disease in dCounts}

def getLikelihood(kb):
    DSCounts = defaultdict(Counter)
    DTotals = Counter()
    totalSymptoms = list(kb["symptoms"].keys())

    for symptom, entries in kb["symptoms"].items():
        for entry in entries:
            if "disease" in entry and entry["disease"]:
                disease = entry["disease"]
                DSCounts[disease][symptom] += 1
                DTotals[disease] += 1

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

        for e2 in self.kb.get('symptoms', {}):
            if e2 in self.getSymptomNames:
                symptomList.append(e2)

        # Validate symptoms
        for check in symptoms:
            if check not in symptomList:
                self.results = {"error": "One or more symptoms are invalid"}

        # Calculate possible diseases
        dList = []
        newSymptomList = self.kb.get("symptoms", {})
        for symptom in symptomList:
            entries = newSymptomList.get(symptom, [])
            for entry in entries:
                if entry.get('plant') == name and entry.get('disease'):
                    dList.append(entry['disease'])

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
        for symptom_name, entries in self.kb["symptoms"].items():
            for entry in entries:
        # Skip empty dicts like {}
                if not entry:
                    continue

                if (entry.get("disease", "").lower().strip() == disease_name and 
                    entry.get("plant", "").lower().strip() == plant_name):
                    if "management" in entry:
                        management = entry.get("management", "")
                    if "type" in entry:
                        classification = entry.get("type", "")
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

        for e2 in self.kb.get('symptoms', {}):
            if e2 in symptoms:
                symptomList.append(e2)

        dList = []
        for symptomCount in symptoms:
            for sListItem in symptomList:
                if sListItem == symptomCount:
                    diseaseStart = self.kb.get("symptoms", {}).get(sListItem, [])
                    diseaseList = [
                        entry.get('symptom') 
                        for entry in diseaseStart 
                        if entry.get('plant') == name and entry.get('disease') == preDiagnosis
                    ]
                    dList.append(diseaseList)

        return {"plant": name, "diagnosis": preDiagnosis, "symptoms": list(set([s for sublist in dList for s in sublist]))}

