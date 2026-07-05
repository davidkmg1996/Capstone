import json
from experta import KnowledgeEngine, Fact, Rule, MATCH, AS, NOT, L, W
from flask import jsonify
 
# ---------------------------------------------------------------------------
# Facts  (each represents one piece of working memory)
# ---------------------------------------------------------------------------
 
class symptomatic(Fact):
    """Initial input: plant name, symptoms dict, and environmental readings."""
    pass
 
class CandidateDisease(Fact):
    """
    Asserted after symptom matching.
    Holds a disease name and its raw symptom CF before environment is applied.
    """
    pass
 
class EnvironmentChecked(Fact):
    """
    Asserted after environmental CF has been calculated for a candidate.
    Holds the combined final CF ready for ranking.
    """
    pass
 
class FinalDiagnosis(Fact):
    """
    Asserted for each disease that clears the confidence threshold.
    Used by the output rule and the backward-chaining rule.
    """
    pass
 
class BackChainRequest(Fact):
    """
    Asserted when two top diagnoses are too close to separate confidently.
    Triggers the backward-chaining rule to ask a clarifying question.
    """
    pass
 
class BackChainAnswer(Fact):
    """
    Asserted when the user answers a backward-chaining clarifying question.
    """
    pass
 
class DiagnosisComplete(Fact):
    """Sentinel — prevents the output rule from firing more than once."""
    pass
class TemperatureChecked(Fact):
    """
    Asserted by Rule 2 after temperature CF is applied.
    Carries cf_after_temp forward to Rule 3.
    """
    pass
 
class HumidityChecked(Fact):
    """
    Asserted by Rule 3 after humidity CF is combined in.
    Carries cf_after_humidity forward to Rule 4.
    """
    pass
 
class WetnessChecked(Fact):
    """
    Asserted by Rule 4 after wetness CF is combined in.
    This is the fully-combined environmental CF — ready for thresholding.
    """
    pass
class KeyChecked(Fact):
    """Asserted by rule 2 after cf is combined"""
 
 
# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
 
def load_json(fPath):
    with open(fPath) as f:
        return json.load(f)
 
 
def combine_cf(cf1, cf2):
    """Standard certainty-factor combination formula."""
    if cf1 > 0 and cf2 > 0:
        return cf1 + cf2 * (1 - cf1)
    elif cf1 < 0 and cf2 < 0:
        return cf1 + cf2 * (1 + cf1)
    else:
        denom = 1 - min(abs(cf1), abs(cf2))
        if denom == 0:
            return 0  # or handle as you see fit
        return (cf1 + cf2) / denom
 
 
def classify_humidity(relative_humidity: float) -> str:
    if relative_humidity >= 81:
        return "high"
    if 61 <= relative_humidity <= 80:
        return "moderate"
    return "low"
 
 
# ---------------------------------------------------------------------------
# Expert System
# ---------------------------------------------------------------------------
 
class PlantDiseaseEngine(KnowledgeEngine):
 
    def __init__(self, kb):
        super().__init__()
        self.kb = kb
        self.results = []
        self.clarifying_question = None   # set by backward-chaining rule
        self.log = []                     # audit trail of rule firings
 
    # -----------------------------------------------------------------------
    # RULE 1 — Symptom Matching
    # Fires on the initial symptomatic fact.
    # For every disease whose plant matches, computes a symptom-only CF
    # and declares a CandidateDisease fact so Rule 2 can pick it up.
    # -----------------------------------------------------------------------
    @Rule(symptomatic(
        name=MATCH.name,
        symptoms=MATCH.symptoms,
        temperature=MATCH.temperature,
        humidity=MATCH.humidity,
        lengthOfW=MATCH.lengthOfW
    ))
    def match_symptoms(self, name, symptoms, temperature, humidity, lengthOfW):
        self.log.append("Rule 1 fired: matching symptoms to candidate diseases")
 
        for disease_name, entry_list in self.kb["diseases"].items():
            for entry in entry_list:
                if entry.get("plant") != name:
                    continue
 
                disease_symptoms = set(entry["symptom"])
                cf_symptoms = 0
                matched=0
                unmatched=0
                total=0
                for symptom, confidence in symptoms.items():
                    total += confidence
                    if symptom in disease_symptoms:
                        matched += confidence
                    else:
                        unmatched+=confidence

                ratio = (matched-unmatched) / total if total > 0 else 0
                coverage = len([s for s in symptoms if s in disease_symptoms]) / len(disease_symptoms)
                cf_symptoms = ratio * coverage


                # Only declare candidates with at least weak positive support
                #changed for testing, should be 0
                if cf_symptoms > -1:
                    self.declare(CandidateDisease(
                        disease=disease_name,
                        plant=name,
                        cf_running=cf_symptoms,
                        temperature=temperature,
                        humidity=humidity,
                        lengthOfW=lengthOfW,
                        management=entry["management"],
                        classification=entry["type"],
                        kb_temp=entry.get("temperature"),
                        kb_humidity=entry.get("humidity"),
                        kb_wetness=entry.get("lengthOfWetness"),
                        kb_keySymptoms=entry.get("keySymptoms"),
                        userSymptoms=symptoms,
                    ))
 



    @Rule(AS.candidate << CandidateDisease(
        disease=MATCH.disease,
        plant=MATCH.plant,
        cf_running=MATCH.cf_running,
        temperature=MATCH.temperature,
        humidity=MATCH.humidity,
        lengthOfW=MATCH.lengthOfW,
        management=MATCH.management,
        classification=MATCH.classification,
        kb_temp=MATCH.kb_temp,
        kb_humidity=MATCH.kb_humidity,
        kb_wetness=MATCH.kb_wetness,
        kb_keySymptoms=MATCH.kb_keySymptoms,
        userSymptoms=MATCH.userSymptoms
    ))
    def check_keySymptom(self, candidate, disease, plant, cf_running,
                          temperature, humidity, lengthOfW, management,
                          classification, kb_temp, kb_humidity, kb_wetness,userSymptoms,kb_keySymptoms):
        self.retract(candidate)
        user_symptoms=set(userSymptoms.keys())
        key_symptoms = set(kb_keySymptoms)

        print(kb_keySymptoms)
        print(key_symptoms)
        print(user_symptoms)
        matched_key=user_symptoms & key_symptoms
        print(matched_key)
        if matched_key:
            cfKey=0.7
        else:
            cfKey=-0.2
        cf_afterKey=combine_cf(cf_running, cfKey)
        self.declare(KeyChecked(
        disease=disease,
        plant=plant,
        cf_running=cf_afterKey,
        temperature=temperature,
        humidity=humidity,
        lengthOfW=lengthOfW,
        management=management,
        classification=classification,
        kb_temp=kb_temp,
        kb_humidity=kb_humidity,
        kb_wetness=kb_wetness
        ))
        
        
    # -----------------------------------------------------------------------
    # RULE 2 — Temperature Check
    # Fires once per CandidateDisease.
    # Applies the temperature CF to cf_running using combine_cf,
    # then declares a TemperatureChecked fact for Rule 3 to pick up.
    # -----------------------------------------------------------------------
    @Rule(AS.candidate << KeyChecked(
        disease=MATCH.disease,
        plant=MATCH.plant,
        cf_running=MATCH.cf_running,
        temperature=MATCH.temperature,
        humidity=MATCH.humidity,
        lengthOfW=MATCH.lengthOfW,
        management=MATCH.management,
        classification=MATCH.classification,
        kb_temp=MATCH.kb_temp,
        kb_humidity=MATCH.kb_humidity,
        kb_wetness=MATCH.kb_wetness,

    ))
    def check_temperature(self, candidate, disease, plant, cf_running,
                          temperature, humidity, lengthOfW, management,
                          classification, kb_temp, kb_humidity, kb_wetness):
        self.log.append(f"Rule 2 fired: checking temperature for {disease}")
        self.retract(candidate)
 
        #cf_temp = self._temperature_cf(kb_temp, temperature)
        temp_range=kb_temp
        if temp_range == "None" or temp_range is None or temperature is None:
            cf_temp=0
        else:
            lower, upper = temp_range[0], temp_range[1]
            if lower <= temperature <= upper:
                cf_temp= 0.4
            elif temperature < lower - 5 or temperature > upper + 5:
                cf_temp= -0.3
            else:
                cf_temp=-0.1
 
        # Only combine if the KB has temperature data for this disease
        if cf_temp != 0:
            cf_after_temp = combine_cf(cf_running, cf_temp)
        else:
            cf_after_temp = cf_running

        self.declare(TemperatureChecked(
            disease=disease,
            plant=plant,
            cf_running=cf_after_temp,
            humidity=humidity,
            lengthOfW=lengthOfW,
            management=management,
            classification=classification,
            kb_humidity=kb_humidity,
            kb_wetness=kb_wetness,
        ))
 
    # -----------------------------------------------------------------------
    # RULE 3 — Humidity Check
    # Fires once per TemperatureChecked fact.
    # Combines the humidity CF into cf_running using combine_cf,
    # then declares a HumidityChecked fact for Rule 4 to pick up.
    # -----------------------------------------------------------------------
    @Rule(AS.temp_checked << TemperatureChecked(
        disease=MATCH.disease,
        plant=MATCH.plant,
        cf_running=MATCH.cf_running,
        humidity=MATCH.humidity,
        lengthOfW=MATCH.lengthOfW,
        management=MATCH.management,
        classification=MATCH.classification,
        kb_humidity=MATCH.kb_humidity,
        kb_wetness=MATCH.kb_wetness,
    ))
    def check_humidity(self, temp_checked, disease, plant, cf_running,
                       humidity, lengthOfW, management, classification,
                       kb_humidity, kb_wetness):
        self.log.append(f"Rule 3 fired: checking humidity for {disease}")
        self.retract(temp_checked)
 
        #cf_hum = self._humidity_cf(kb_humidity, humidity)
        if kb_humidity == "None" or kb_humidity is None or humidity is None:
            cf_hum=0
        else:

            if humidity == kb_humidity:
                cf_hum=0.4
            else:
                cf_hum=-0.3
 
        cf_after_humidity = combine_cf(cf_running, cf_hum) if cf_hum is not None else cf_running
 
        self.declare(HumidityChecked(
            disease=disease,
            plant=plant,
            cf_running=cf_after_humidity,
            lengthOfW=lengthOfW,
            management=management,
            classification=classification,
            kb_wetness=kb_wetness,
        ))
 
    # -----------------------------------------------------------------------
    # RULE 4 — Wetness Check
    # Fires once per HumidityChecked fact.
    # Combines the wetness CF into cf_running using combine_cf.
    # This is the last environmental step — declares WetnessChecked
    # with the fully combined CF ready for thresholding.
    # -----------------------------------------------------------------------
    @Rule(AS.hum_checked << HumidityChecked(
        disease=MATCH.disease,
        plant=MATCH.plant,
        cf_running=MATCH.cf_running,
        lengthOfW=MATCH.lengthOfW,
        management=MATCH.management,
        classification=MATCH.classification,
        kb_wetness=MATCH.kb_wetness,
    ))
    def check_wetness(self, hum_checked, disease, plant, cf_running,
                      lengthOfW, management, classification, kb_wetness):
        self.log.append(f"Rule 4 fired: checking wetness for {disease}")
        self.retract(hum_checked)
 
        #cf_wet = self._wetness_cf(kb_wetness, lengthOfW)
 
        if kb_wetness == "None" or kb_wetness is None or lengthOfW is None:
            cf_wet=0
        else:
            if lengthOfW >= int(kb_wetness):
                cf_wet=0.4
            else:
                cf_wet=-0.3

        cf_final = combine_cf(cf_running, cf_wet) if cf_wet !=0 else cf_running

 
        self.declare(WetnessChecked(
            disease=disease,
            plant=plant,
            cf_final=cf_final,
            management=management,
            classification=classification,
        ))
     # -----------------------------------------------------------------------
    # RULE 5 — Threshold & Diagnosis
    # Fires once per EnvironmentChecked fact.
    # Only promotes diseases above the confidence threshold to FinalDiagnosis.
    # -----------------------------------------------------------------------
    CONFIDENCE_THRESHOLD = -1
 
    @Rule(AS.checked << WetnessChecked(
        disease=MATCH.disease,
        plant=MATCH.plant,
        cf_final=MATCH.cf_final,
        management=MATCH.management,
        classification=MATCH.classification,
    ))
    def threshold_check(self, checked, disease, plant, cf_final,
                        management, classification):
        self.log.append(f"Rule 5 fired: threshold check for {disease} (CF={cf_final:.3f})")
 
        self.retract(checked)
 
        if cf_final >= self.CONFIDENCE_THRESHOLD:
            self.declare(FinalDiagnosis(
                disease=disease,
                plant=plant,
                cf_final=cf_final,
                management=management,
                classification=classification,
            ))
      # -----------------------------------------------------------------------
    # RULE 6 — Output
    # Fires once when no BackChainRequest is pending (or ambiguity resolved).
    # Collects all FinalDiagnosis facts, ranks them, and writes self.results.
    # -----------------------------------------------------------------------
    @Rule(
    NOT(DiagnosisComplete()),
    NOT(BackChainRequest()),
    NOT(CandidateDisease()),
    NOT(TemperatureChecked()),
    NOT(HumidityChecked()),
    NOT(WetnessChecked()),
    NOT(KeyChecked()),
    )
    def produce_output(self):
        diagnoses = [
            f for f in self.facts.values()
            if isinstance(f, FinalDiagnosis)
        ]
        if not diagnoses:
            return
 
        ranked = sorted(diagnoses, key=lambda f: f["cf_final"], reverse=True)[:5]
 
        self.results = [
            {
                "disease":        f["disease"],
                "plant":          f["plant"],
                "probability":    round(f["cf_final"], 4),
                "management":     f["management"],
                "classification": f["classification"],
            }
            for f in ranked
        ]
 
        self.log.append("Rule 6 fired: output produced")
        self.declare(DiagnosisComplete())
 
        with open("data.json", "w") as file:
            json.dump(self.results, file, indent=4)
        

if __name__ == "__main__":
    KB_FILE = "KB.json"
    kb_data = load_json(KB_FILE)
    plant_name="Maize (corn)"
    temperature=None
    humidity=None
    lengthOfW=None
    symptoms={
    "Gray lesions": 0.45,
    "Tan": 0.42,
    "Brown": 0.40,
    "Yellow": 0.38
}
    engine = PlantDiseaseEngine(kb_data)
    engine.reset()
    engine.declare(symptomatic(name=plant_name, symptoms=symptoms, temperature=temperature,humidity=humidity,lengthOfW=lengthOfW))
    engine.run()
    print(engine.results)