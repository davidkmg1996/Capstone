import json
from experta import KnowledgeEngine, Fact, Rule, MATCH, AS

# ---------------------------------------------------------------------------
# FACTS
# ---------------------------------------------------------------------------

class symptomatic(Fact): pass
class CandidateDisease(Fact): pass
class KeyChecked(Fact): pass
class TemperatureChecked(Fact): pass
class HumidityChecked(Fact): pass
class WetnessChecked(Fact): pass


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def load_json(path):
    with open(path) as f:
        return json.load(f)


def combine_cf(cf1, cf2):
    # Stable CF combination bounded in [-1, 1]
    if cf1 is None: cf1 = 0
    if cf2 is None: cf2 = 0

    if cf1 > 0 and cf2 > 0:
        return cf1 + cf2 * (1 - cf1)
    elif cf1 < 0 and cf2 < 0:
        return cf1 + cf2 * (1 + cf1)
    else:
        denom = 1 - min(abs(cf1), abs(cf2))
        return 0 if denom == 0 else (cf1 + cf2) / denom


def clamp(x, low=-1, high=1):
    return max(low, min(high, x))


# ---------------------------------------------------------------------------
# ENGINE
# ---------------------------------------------------------------------------

class PlantDiseaseEngine(KnowledgeEngine):

    CONFIDENCE_THRESHOLD = 0.05  # realistic cutoff

    def __init__(self, kb):
        super().__init__()
        self.kb = kb
        self.results = []

    # -----------------------------------------------------------------------
    # RULE 1 — SYMPTOM MATCHING (STABLE CORE SIGNAL)
    # -----------------------------------------------------------------------
    @Rule(symptomatic(
        name=MATCH.name,
        symptoms=MATCH.symptoms,
        temperature=MATCH.temperature,
        humidity=MATCH.humidity,
        lengthOfW=MATCH.lengthOfW
    ))
    def match_symptoms(self, name, symptoms, temperature, humidity, lengthOfW):

        for disease_name, entries in self.kb.get("diseases", {}).items():
            for entry in entries:

                if entry.get("plant") != name:
                    continue

                kb_symptoms = set(entry.get("symptom", []))
                if not kb_symptoms:
                    continue

                user_symptoms = set(symptoms.keys())

                # ---- stable overlap scoring ----
                overlap = len(user_symptoms & kb_symptoms)
                total = len(kb_symptoms)

                base_cf = overlap / total if total else 0

                # small penalty for extra noise symptoms
                noise = len(user_symptoms - kb_symptoms) / max(len(user_symptoms), 1)
                cf = base_cf - (noise * 0.2)

                cf = clamp(cf)

                self.declare(CandidateDisease(
                    disease=disease_name,
                    plant=name,
                    cf=cf,
                    temperature=temperature,
                    humidity=humidity,
                    lengthOfW=lengthOfW,
                    management=entry.get("management"),
                    classification=entry.get("type"),
                    kb_temp=entry.get("temperature"),
                    kb_humidity=entry.get("humidity"),
                    kb_wetness=entry.get("lengthOfWetness"),
                    kb_keySymptoms=entry.get("keySymptoms"),
                    userSymptoms=symptoms,
                ))

    # -----------------------------------------------------------------------
    # RULE 2 — KEY SYMPTOMS BOOST
    # -----------------------------------------------------------------------
    @Rule(AS.c << CandidateDisease(
        disease=MATCH.disease,
        cf=MATCH.cf,
        kb_keySymptoms=MATCH.kb_keySymptoms,
        userSymptoms=MATCH.userSymptoms,
        plant=MATCH.plant,
        temperature=MATCH.temperature,
        humidity=MATCH.humidity,
        lengthOfW=MATCH.lengthOfW,
        management=MATCH.management,
        classification=MATCH.classification,
        kb_temp=MATCH.kb_temp,
        kb_humidity=MATCH.kb_humidity,
        kb_wetness=MATCH.kb_wetness
    ))
    def key_symptoms(self, c, disease, cf, kb_keySymptoms, userSymptoms,
                     plant, temperature, humidity, lengthOfW,
                     management, classification,
                     kb_temp, kb_humidity, kb_wetness):

        self.retract(c)

        user_set = set(userSymptoms.keys())
        key_set = set(kb_keySymptoms or [])

        boost = 0.6 if user_set & key_set else -0.15
        cf_new = combine_cf(cf, boost)

        self.declare(KeyChecked(
            disease=disease,
            cf=clamp(cf_new),
            plant=plant,
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
    # RULE 3 — TEMPERATURE
    # -----------------------------------------------------------------------
    @Rule(AS.c << KeyChecked(
        disease=MATCH.disease,
        cf=MATCH.cf,
        kb_temp=MATCH.kb_temp,
        temperature=MATCH.temperature,
        humidity=MATCH.humidity,
        lengthOfW=MATCH.lengthOfW,
        management=MATCH.management,
        classification=MATCH.classification,
        kb_humidity=MATCH.kb_humidity,
        kb_wetness=MATCH.kb_wetness,
        plant=MATCH.plant
    ))
    def temperature(self, c, disease, cf, kb_temp, temperature,
                    humidity, lengthOfW,
                    management, classification,
                    kb_humidity, kb_wetness, plant):

        self.retract(c)

        cf_temp = 0

        if kb_temp and temperature is not None:
            low, high = kb_temp
            if low <= temperature <= high:
                cf_temp = 0.3
            else:
                cf_temp = -0.2

        cf_new = combine_cf(cf, cf_temp)

        self.declare(TemperatureChecked(
            disease=disease,
            cf=clamp(cf_new),
            plant=plant,
            temperature=temperature,
            humidity=humidity,
            lengthOfW=lengthOfW,
            management=management,
            classification=classification,
            kb_humidity=kb_humidity,
            kb_wetness=kb_wetness
        ))

    # -----------------------------------------------------------------------
    # RULE 4 — HUMIDITY
    # -----------------------------------------------------------------------
    @Rule(AS.c << TemperatureChecked(
        disease=MATCH.disease,
        cf=MATCH.cf,
        humidity=MATCH.humidity,
        kb_humidity=MATCH.kb_humidity,
        lengthOfW=MATCH.lengthOfW,
        management=MATCH.management,
        classification=MATCH.classification,
        kb_wetness=MATCH.kb_wetness,
        plant=MATCH.plant
    ))
    def humidity(self, c, disease, cf, humidity, kb_humidity,
                 lengthOfW, management, classification,
                 kb_wetness, plant):

        self.retract(c)

        cf_h = 0

        if kb_humidity and humidity is not None:
            cf_h = 0.3 if str(humidity) == str(kb_humidity) else -0.2

        cf_new = combine_cf(cf, cf_h)

        self.declare(HumidityChecked(
            disease=disease,
            cf=clamp(cf_new),
            plant=plant,
            lengthOfW=lengthOfW,
            management=management,
            classification=classification,
            kb_wetness=kb_wetness
        ))

    # -----------------------------------------------------------------------
    # RULE 5 — WETNESS
    # -----------------------------------------------------------------------
    @Rule(AS.c << HumidityChecked(
        disease=MATCH.disease,
        cf=MATCH.cf,
        lengthOfW=MATCH.lengthOfW,
        kb_wetness=MATCH.kb_wetness,
        management=MATCH.management,
        classification=MATCH.classification,
        plant=MATCH.plant
    ))
    def wetness(self, c, disease, cf, lengthOfW,
                kb_wetness, management, classification, plant):

        self.retract(c)

        cf_w = 0

        if kb_wetness and lengthOfW is not None:
            cf_w = 0.3 if lengthOfW >= int(kb_wetness) else -0.2

        cf_final = combine_cf(cf, cf_w)
        cf_final = clamp(cf_final)

        self.declare(WetnessChecked(
            disease=disease,
            cf_final=cf_final,
            plant=plant,
            management=management,
            classification=classification
        ))

    # -----------------------------------------------------------------------
    # FINAL OUTPUT
    # -----------------------------------------------------------------------
    @Rule(AS.c << WetnessChecked(
        disease=MATCH.disease,
        cf_final=MATCH.cf_final,
        management=MATCH.management,
        classification=MATCH.classification,
        plant=MATCH.plant
    ))
    def final(self, c, disease, cf_final, management, classification, plant):

        self.retract(c)

        # convert [-1,1] → [0,100]
        probability = ((cf_final + 1) / 2) * 100

        if probability >= self.CONFIDENCE_THRESHOLD * 100:
            self.results.append({
                "disease": disease,
                "plant": plant,
                "probability": round(probability, 2),
                "management": management,
                "classification": classification
            })