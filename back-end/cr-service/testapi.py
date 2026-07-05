import sys
from flask import Flask, request, jsonify
from flask_cors import CORS

sys.path.append("../../")

from skeletons.JoshStuff.GeminiDiagnoseAndElaborate import getReport

app = Flask(__name__)
CORS(app, origins="http://localhost:8081")


@app.route("/diagnose", methods=["POST"])
def diagnose():
    data = request.get_json()
    print(data)
    elaborationPrompt = f"For the plant disease {",".join(data["symptoms"])}, and the plant type {data["plant"]}, provide recommendations " \
            "on how best to treat this aflicted plant, as well as prevention strategies for the future."
    diagnosisPrompt = f"Identify the most likely disease affecting a {data["plant"]} with the following symptoms: {','.join(data["symptoms"])} affecting the plant's leaves. " \
                       "Provide a list of the five most likely diseases if there are that many likely candidates."
    return getReport(diagnosisPrompt)