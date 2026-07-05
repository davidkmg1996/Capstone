# skeleton.py
import json
from experta import KnowledgeEngine, Fact, Rule, MATCH, P
from fpdf import FPDF

class Observation(Fact): pass

class PlantDiagnosis(KnowledgeEngine):
    def __init__(self, kb):
        super().__init__()
        self.kb = kb
        self.log = []            # store fired-rule traces
        self.pdf = FPDF()

    @Rule(Observation(plant=MATCH.plant, disease=MATCH.disease,
                      confidence=P(lambda c: c >= 0.7)))
    def diagnose(self, plant, disease):
        info = self.kb.get(plant, {}).get(disease)
        self.log.append({"rule":"diagnose", "plant":plant, "disease":disease, "kb_found": bool(info)})
        if not info:
            # fallback: unknown disease for this plant
            self.pdf.add_page()
            self.pdf.multi_cell(0,10, f"Unknown disease {disease} for {plant}")
        else:
            self.pdf.add_page()
            text = f"Diagnosis: {info['name']}\n\nSymptoms:\n- " + "\n- ".join(info['symptoms'])
            text += "\n\nRecommendations:\n- " + "\n- ".join(info['treatments'])
            self.pdf.set_font("Arial", size=12)
            self.pdf.multi_cell(0,10, text)
        self.pdf.output("diagnosis.pdf")

    @Rule(Observation(confidence=P(lambda c: c < 0.7)))
    def uncertain(self, confidence):
        self.log.append({"rule":"uncertain", "confidence": float(confidence)})
        self.pdf.add_page()
        self.pdf.set_font("Arial", size=12)
        self.pdf.multi_cell(0,10,"Uncertain diagnosis. Please retake the photo or seek expert review.")
        self.pdf.output("diagnosis.pdf")

# Usage
with open("KB.json") as f:
    kb = json.load(f)

engine = PlantDiagnosis(kb)
engine.reset()
# after model predicts:
engine.declare(Observation(plant="Cassava", disease="CassavaBlight", confidence=0.87))
engine.run()
print(engine.log)   # show why the system decided what it did
