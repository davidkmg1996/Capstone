import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np
from ESTest import PlantDiseaseEngine, load_json, symptomatic
from google.cloud import storage
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
import tensorflow as tf
import requests

app = Flask(__name__)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# -------------------------
# CORS CONFIG
# -------------------------
ALLOWED_ORIGINS = [
    "http://localhost:8081",
    "https://plantdisease-932821527783.europe-west1.run.app",
    "https://diseaseidentity.com",
    "https://www.diseaseidentity.com",
    "http://localhost:5000"
]

CORS(
    app,
    resources={r"/*": {"origins": ALLOWED_ORIGINS}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS"]
)

@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")

    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"

    return response

@app.route("/api/register", methods=["OPTIONS"])
@app.route("/api/login", methods=["OPTIONS"])
def options_handler():
    return "", 204

# -------------------------
# LABELS
# -------------------------
LABEL_NAMES = [
    'Tan', 'Sunken', 'Black-Lesions', 'Black-Veins', 'Rotting', 'Brown', 'Wilt',
    'Blotchy', 'Healthy', 'Oily', 'Yellow', 'Greasy', 'Black', 'Scorched',
    'Purple', 'Brown-Lesions', 'Watery', 'Halo', 'Spots', 'Distortion',
    'Sunscald', 'Powdery', 'Fuzzy', 'Elliptical-Lesions', 'Parallel-Lesions',
    'Green-Lesions', 'Spores', 'Yellow-Lesions', 'Discolored-Streaks',
    'White-Mold', 'Circular', 'Rings', 'Collapsed', 'Shriveled',
    'Black-Specks', 'Discolored'
]

# -------------------------
# DB
# -------------------------
def get_db_connection():
    return psycopg2.connect(
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=f"/cloudsql/{os.environ['CLOUD_SQL_CONNECTION_NAME']}"
    )

# -------------------------
# KB
# -------------------------
KB_FILE = "KB.json"
kb_data = load_json(KB_FILE)

# -------------------------
# MODEL
# -------------------------
_model = None
_storage_client = storage.Client()
_model_bucket = "modelplantb"
_savedmodel_dir = "saved_model"

def download_savedmodel_to_tmp(bucket_name, folder_name, local_path="/tmp/saved_model"):
    bucket = _storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=folder_name + "/")
    os.makedirs(local_path, exist_ok=True)

    for blob in blobs:
        rel_path = blob.name[len(folder_name) + 1:]
        if not rel_path:
            continue
        full_local_path = os.path.join(local_path, rel_path)
        os.makedirs(os.path.dirname(full_local_path), exist_ok=True)
        blob.download_to_filename(full_local_path)

    return local_path

def load_model_lazy():
    global _model
    if _model:
        return _model

    try:
        model_path = download_savedmodel_to_tmp(_model_bucket, _savedmodel_dir)
        _model = tf.saved_model.load(model_path)
        return _model
    except Exception as e:
        print("Model load failed:", str(e))
        return None

# -------------------------
# HELPERS
# -------------------------
def convert_symptoms(predicted_symptoms):
    return {
        s["symptom_name"]: s["probability_percent"] / 100
        for s in predicted_symptoms
    }

def convert_manual(symptom_list):
    return {s: 0.5 for s in symptom_list}

def preprocess_image(file_like, target_size=(224, 224)):
    img = Image.open(file_like).convert("RGB")
    img = img.resize(target_size)
    arr = np.array(img).astype("float32") / 255.0
    return np.expand_dims(arr, axis=0)

# -------------------------
# FORMAT
# -------------------------
def format_diagnosis_text(plant, classification, management, probabilities):
    lines = [f"Diagnosis for {plant}", ""]

    if probabilities:
        top = probabilities[0]
        lines.append(f"Most likely: {top['disease']} ({top['probability']}%)")

    if classification:
        lines.append(f"\nType: {classification}")
    if management:
        lines.append(f"\nManagement:\n{management}")

    if probabilities and len(probabilities) > 1:
        lines.append("\nOther possibilities:")
        for p in probabilities[1:]:
            lines.append(f"- {p['disease']} ({p['probability']}%)")

    return "\n".join(lines)

# -------------------------
# IMAGE DIAGNOSIS
# -------------------------
@app.route("/api/diagnoseImage", methods=["POST"])
def diagnose_image():
    model = load_model_lazy()
    if model is None:
        return jsonify({"error": "Model unavailable"}), 500

    print("FILES:", request.files)
    print("FORM:", request.form)

    file = request.files.get("image")

    if file is None:
        return jsonify({
            "error": "No image uploaded",
            "debug_files": str(request.files)
        }), 400

    try:
        img_array = preprocess_image(file)

        infer = model.signatures["serving_default"]
        input_key = list(infer.structured_input_signature[1].keys())[0]

        outputs = infer(**{input_key: tf.constant(img_array, dtype=tf.float32)})

        output_tensor = list(outputs.values())[0]
        probs = output_tensor.numpy()

        if len(probs.shape) > 1:
            probs = probs[0]

        probs = np.array(probs)

        if not np.isclose(np.sum(probs), 1.0, atol=0.1):
            probs = tf.nn.softmax(probs).numpy()

        TOP_K = min(5, len(probs), len(LABEL_NAMES))

        top_indices = np.argsort(probs)[-TOP_K:][::-1]

        predicted_symptoms = [
            {
                "symptom_name": LABEL_NAMES[i],
                "probability_percent": float(probs[i]) * 100
            }
            for i in top_indices
        ]

        symptoms_dict = {
            s["symptom_name"]: s["probability_percent"] / 100
            for s in predicted_symptoms
        }

        engine = PlantDiseaseEngine(kb_data)
        engine.reset()

        engine.declare(symptomatic(
            name="Tomato",
            symptoms=symptoms_dict,
            temperature=None,
            humidity=None,
            lengthOfW=None
        ))

        engine.run()

        raw = engine.results

        return jsonify({
            "symptoms": predicted_symptoms,
            "debug_received": True,
            "probabilities_raw": str(raw)
        }), 200

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT password_hash FROM users WHERE username = %s', (username,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row is None or not check_password_hash(row[0], password):
            return jsonify({"error": "Invalid username or password"}), 401

        return jsonify({"message": "Login successful"}), 200
    except Exception as e:
        print("Login error:", str(e))
        return jsonify({"error": "Server error"}), 500

@app.route("/api/register", methods=["POST"])
def register():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Missing JSON body"}), 400

        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400

        password_hash = generate_password_hash(password)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({"error": "Username already exists"}), 409

        cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Registration successful"}), 201
    except Exception as e:
        print("REGISTER ERROR:", repr(e))
        return jsonify({"error": "Server error"}), 500

# -------------------------
# MANUAL DIAGNOSIS
# -------------------------
@app.route("/api/diagnose", methods=["POST"])
def diagnose():
    data = request.get_json()

    plant = data.get("plant")
    symptoms = data.get("symptoms", [])

    try:
        symptoms_dict = convert_manual(symptoms)

        engine = PlantDiseaseEngine(kb_data)
        engine.reset()
        engine.declare(symptomatic(
            name=plant,
            symptoms=symptoms_dict,
            temperature=None,
            humidity=None,
            lengthOfW=None
        ))
        engine.run()

        probabilities = sorted(engine.results, key=lambda x: x["probability"], reverse=True)

        return jsonify({
            "result": format_diagnosis_text(
                plant,
                probabilities[0]["classification"] if probabilities else None,
                probabilities[0]["management"] if probabilities else None,
                probabilities
            )
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------
# GEMINI OPINION
# -------------------------
@app.route("/api/geminiOpinion", methods=["POST"])
def gemini_opinion():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input provided"}), 400

    plant = data.get("plant")
    symptoms = data.get("symptoms", [])

    try:
        prompt = f"Identify the most likely disease affecting {plant} with symptoms: {', '.join(symptoms)}"

        report_text = getReport(prompt)

        return jsonify({"report": report_text}), 200

    except Exception as e:
        print("Gemini error:", str(e))
        return jsonify({"error": str(e)}), 500

def getReport(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    r = requests.post(url, headers=headers, json=payload, timeout=30)

    if r.status_code != 200:
        raise Exception(r.text)

    data = r.json()

    return data["candidates"][0]["content"]["parts"][0]["text"]

# -------------------------
# ROOT
# -------------------------
@app.route("/")
def root():
    return {"message": "Service is running"}

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))