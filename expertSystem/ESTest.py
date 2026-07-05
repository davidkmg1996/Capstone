import json
from experta import KnowledgeEngine, Fact, Rule, MATCH, P, Field, engine, AS, NOT
from collections import Counter, defaultdict
from twisted.internet import asyncioreactor
asyncioreactor.install()
from scrapy.crawler import CrawlerProcess
from diseaseInfo.diseaseInfo.spiders.scrape import MySpider
from fpdf import FPDF
import math
import array
import re

#for scrapy, run python 

class symptomatic(Fact):
    name = ""
    symptoms = []
    
class backChain(Fact):
    name = ""
    preDiagnosis = ""

class backChainTest(Fact):
    name =""
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
    
def crawl():
    process = CrawlerProcess()
    process.crawl(MySpider)
    process.start(install_signal_handlers=False)

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
        self.pdf = FPDF()
        self.valid_symptoms = set()


        self.symptomList = []
        self.currentPlant = None
        for symptomID, symptomInfo in self.kb.get('symptoms', {}).items():
            if 'name' in symptomInfo:
                self.valid_symptoms.add(symptomInfo['name'].lower())  

        self.priors = getPriors(self.kb)
        self.likelihood = getLikelihood(self.kb)

    @Rule(symptomatic(name=MATCH.name, symptoms = MATCH.symptoms))
    def getSymptoms(self, name, symptoms):
        from expertTest import diagnoseNoCrawl
        self.currentPlant = name
        self.getSymptomNames= []
        self.getSymptomNames = symptoms
        

        if self.currentPlant is None:
            self.currentPlant = name.lower()
            print(f"This is a {self.currentPlant}")

        symptomList = []        

        if symptomList is None:
           pass
        else:
            for e2 in self.kb.get('symptoms', {}):
                if e2 in self.getSymptomNames:
                    symptomList.append(e2)

            for check in symptoms:
                if check not in symptomList:
                    print("One or more symptoms are invalid, please try again")
                    diagnoseNoCrawl()
                    return
                
            print(f"You've indicated that the {name} has the symptoms", end = " ")
            if check in symptomList:   
                for sListItem in symptomList:
                    print(f"{sListItem}", end=", ")
      
            print("\n")
            dList = []
            newSymptomList = self.kb.get("symptoms", {})
            for symptomCount in newSymptomList:
                    for sListItem in symptomList:
                        if sListItem == symptomCount:
                            diseaseStart = self.kb.get("symptoms", {}).get(sListItem, [])
                            diseaseList = [entry.get('disease') for entry in diseaseStart if 'disease' in entry and entry.get('plant') == name]
                            dList.append(diseaseList)
            
            posteriors = {}
            for disease, prior, in self.priors.items():
                prob = prior
                for s in symptoms:
                    prob *= self.likelihood[disease].get(s, 1e-6)
                posteriors[disease] = prob

            totalProb = sum(posteriors.values())
            posteriors = {d: round(p/totalProb * 100, 2) for d, p in posteriors.items()}

                
            print(f"Based on these symptoms, your plant could potentially have:")
            z = 0
            cDisease = [disease for disList in dList for disease in disList]
            for p in cDisease:
                if p in cDisease:
                    z+=1
            count = Counter(cDisease)

            tDiseases = sorted(posteriors.items(), key=lambda x: x[1], reverse=True)[:5]
            
            for disease, prob in tDiseases:
                print(f"{disease}: {prob}%")
            
class confirmDiagnosis(KnowledgeEngine):
    def __init__(self, kb):
        super().__init__()
        self.kb = kb
        self.log = []            
        self.pdf = FPDF()
        self.currentPlant = None
        self.currentDisease = None
            
    @Rule(backChain(name = MATCH.name, preDiagnosis = MATCH.preDiagnosis))
    def getDiagnosis(self, name, preDiagnosis):
        self.currentPlant = name
        self.currentDiagnosis = preDiagnosis
        self.getSymptomName = []
        symptoms = self.kb.get("symptoms", {})
        self.getSymptomName = symptoms
    
        
        symptomList = []
        
        print(f"You've indicated that the plant is a {name}\nThe symptoms for that disease are:\n")
        dList = []
        newSymptomList = self.kb.get("symptoms", {})
        for e2 in self.kb.get('symptoms', {}):
            if e2 in self.getSymptomName:
                symptomList.append(e2)
                
        for symptomCount in newSymptomList:
            for sListItem in symptomList:
                if sListItem == symptomCount:
                    diseaseStart = self.kb.get("symptoms", {}).get(sListItem, [])
                    diseaseList = [entry.get('symptom') for entry in diseaseStart if entry.get('plant') == name and entry.get('disease') == preDiagnosis]
                    dList.append(diseaseList)
    
        print(", ".join(set([symptom for joinDis in dList for symptom in joinDis])))
        comfirmList = self.kb.get('symptoms')
        print("Please enter the names of the symptoms")
        inputSymptoms = input() 
        symptomList = [symptomI.strip() for symptomI in inputSymptoms.split(",")]
        print(", ".join(set(symptomList)))

    @Rule (backChainTest(name = MATCH.name, disease = MATCH.disease))
    def getPercentage(self, name, disease):
        disease_symptoms = {}
        numOfSymptoms=0
        totalSymptoms=0
        #Loop through symptoms
        for symptom, entries in self.kb["symptoms"].items():
          totalSymptoms+=1
          for entry in entries:

            if "disease" not in entry:
                continue

            if entry["disease"].lower() == disease.lower() and entry["plant"].lower()==name.lower():
                # Add to result dictionary
                if disease not in disease_symptoms:
                    disease_symptoms[disease] = set()
                disease_symptoms[disease].add(symptom)
                if symptom not in disease_symptoms:
                    numOfSymptoms+=1
                    print(numOfSymptoms)
            #Print results for testing
        if disease_symptoms:
            print(f"\n Symptoms for {disease}:")
            for symptom in disease_symptoms[disease]:
                print(f"- {symptom}")
        else:
            print(f"\n No symptoms found for '{disease}' in KB.json")
        #place holder percentage calculation
        print(f" {round(numOfSymptoms /totalSymptoms, 2)}% ")
#using kb2.json
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
                print(entry)
                print(entry.get("temperature"))
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