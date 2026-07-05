from flask import Flask, request, jsonify
from ESTest import confirmDiagnosis, backChain, MultiSymptom, load_json, symptomatic, crawl
from werkzeug.utils import secure_filename
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
UPLOAD_FOLDER = "/tmp/uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@app.route('/option', methods=['POST'])
def main():
    print("Would you like to diagnose or confirm a diagnosis?\nPlease Enter \"Diagnose\" or \"Confirm\"")
    choose = input()
    if str(choose) == "Diagnose" or str(choose).lower() == "diagnose":   
       diagnose()
    elif str(choose) == "Confirm" or str(choose).lower() == "confirm":
       confirm() 

@app.route('/diagnose', methods=['POST'])
def diagnose():
    crawl()
    kb = load_json("KB.json")
    # engine = PlantDiagnosis(kb)
    engine = MultiSymptom(kb)
    print("\nPlease enter symptoms separated by commas: ", end=" ")
    symptomInput = input()
    symptomList = [symptom.strip() for symptom in symptomInput.split(",")]
    engine.reset()
    engine.declare(symptomatic(name="Tomato", symptoms=symptomList))
    engine.run()

@app.route('/diagnoseArgs', methods=['POST'])
def diagnoseWithArgs(symptoms):
    kb = load_json("KB.json")
    # engine = PlantDiagnosis(kb)
    engine = MultiSymptom(kb)
    print("\nPlease enter symptoms separated by commas: ", end=" ")
    symptomInput = symptoms
    symptomList = [symptom.strip() for symptom in symptomInput.split(",")]
    engine.reset()
    engine.declare(symptomatic(name="Tomato", symptoms=symptomList))
    engine.run()

#Needs CloudRun update
@app.route('/retry', methods=['POST'])
def diagnoseNoCrawl():
    kb = load_json("KB.json")
    # engine = PlantDiagnosis(kb)
    engine = MultiSymptom(kb)
    print("\nPlease enter symptoms separated by commas: ", end=" ")
    symptomInput = input()
    symptomList = [symptom.strip() for symptom in symptomInput.split(",")]
    engine.reset()
    engine.declare(symptomatic(name="Tomato", symptoms=symptomList))
    engine.run()

@app.route('/upload', methods = ['POST'])
def uploadImage():
    file = request.files('image')
    filename = secure_filename(file.filename)
    iPath = os.path.join(app.config['UPLOADE_FOLDER'], filename)
    file.save(iPath)

#Needs ClodRun update
@app.route('/confirm', methods=['POST'])
def confirm():
    kb = load_json("KB.json")
    engine2 = confirmDiagnosis(kb)
    print("Please enter the name of a disease")
    diseaseConf = input()
    disease = diseaseConf
    engine2.reset()
    engine2.declare(backChain(name="Tomato", preDiagnosis=disease))
    engine2.run()
        
if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=5000)
    main()