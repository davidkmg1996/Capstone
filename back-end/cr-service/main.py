import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np
from ESTest import MultiSymptom, load_json, symptomatic
from google.cloud import storage
import psycopg2
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import tensorflow as tf


app = Flask(__name__)

# -------------------------
# CORS CONFIG
# -------------------------
ALLOWED_ORIGINS = [
    "http://localhost:8081",
    "https://plantdisease-932821527783.europe-west1.run.app",
    "https://diseaseidentity.com",
    "https://www.diseaseidentity.com",
    "http://localhost:5000",
    "http://localhost:5000/api/diagnose"
]

CORS(
    app,
    resources={r"/*": {"origins": ALLOWED_ORIGINS}},
    supports_credentials=True,
    allow_headers="*",
    methods=["GET", "POST", "OPTIONS"]
)

LABEL_NAMES = [
    'Tan', 'Sunken', 'Black-Lesions', 'Black-Veins', 'Rotting', 'Brown', 'Wilt',
    'Blotchy', 'Healthy', 'Oily', 'Yellow', 'Greasy', 'Black', 'Scorched',
    'Purple', 'Brown-Lesions', 'Watery', 'Halo', 'Spots', 'Distortion',
    'Sunscald', 'Powdery', 'Fuzzy', 'Elliptical-Lesions', 'Parallel-Lesions',
    'Green-Lesions', 'Spores', 'Yellow-Lesions', 'Discolored-Streaks',
    'White-Mold', 'Circular', 'Rings', 'Collapsed', 'Shriveled',
    'Black-Specks', 'Discolored'
]



@app.route("/api/<path:path>", methods=["OPTIONS"])
@app.route("/<path:path>", methods=["OPTIONS"])
def options_handler(path):
    response = jsonify({"status": "OK"})
    origin = request.headers.get("Origin")
    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin

    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response


@app.after_request
def after_request(response):
    origin = request.headers.get("Origin")
    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin

    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response

def get_db_connection():
    return psycopg2.connect(
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=f"/cloudsql/{os.environ['CLOUD_SQL_CONNECTION_NAME']}"
    )


# -------------------------
# KNOWLEDGE BASE
# -------------------------
KB_FILE = "KB.json"
kb_data = load_json(KB_FILE)


# -------------------------
# SAVEDMODEL GLOBALS
# -------------------------
_model = None
_storage_client = storage.Client()
_model_bucket = "modelplantb"
_savedmodel_dir = "saved_model"     # this folder must contain saved_model.pb


@app.route("/api/db-test")
def db_test():
    try:
        conn_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")
        socket_path = f"/cloudsql/{conn_name}"

        print("CLOUD_SQL_CONNECTION_NAME =", conn_name)
        print("EXPECTED SOCKET PATH =", socket_path)
        print("SOCKET EXISTS =", os.path.exists(socket_path))

        conn = psycopg2.connect(
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            host=socket_path
        )

        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.close()
        conn.close()

        return {"status": "DB OK"}, 200

    except Exception as e:
        print("DB TEST ERROR:", repr(e))
        return {"error": repr(e)}, 500


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
    if _model is not None:
        return _model

    try:
        print("[INFO] TF version:", tf.__version__)
        print("[INFO] Downloading SavedModel...")

        model_path = download_savedmodel_to_tmp(
            _model_bucket,
            _savedmodel_dir,
            "/tmp/saved_model"
        )

        print("[INFO] Loading SavedModel...")
        _model = tf.saved_model.load(model_path)

        print("[INFO] SavedModel is ready")
        return _model

    except Exception as e:
        print("[ERROR] Model load failed:", str(e))
        _model = None
        return None

def lookup_disease_info(kb_data, disease_name):
    # If KB is wrapped in a dict, unwrap it
    if isinstance(kb_data, dict):
        if "rules" in kb_data:
            entries = kb_data["rules"]
        else:
            entries = []
            for v in kb_data.values():
                if isinstance(v, list):
                    entries.extend(v)
    else:
        entries = kb_data

    for entry in entries:
        if not isinstance(entry, dict):
            continue

        if entry.get("disease", "").lower() == disease_name.lower():
            return {
                "type": entry.get("type"),
                "management": entry.get("management")
            }

    return {}

# -------------------------
# IMAGE PREPROCESSING
# -------------------------
def preprocess_image(file_like, target_size=(255, 255)):
    img = Image.open(file_like).convert("RGB")
    img = img.resize(target_size)
    arr = np.array(img).astype("float32") / 255.0
    return np.expand_dims(arr, axis=0)



# -------------------------
# API: MODEL INFO (DEBUG)
# -------------------------
@app.route("/api/model-info", methods=["GET"])
def model_info():
    model = load_model_lazy()
    if model is None:
        return {"error": "model not loaded"}, 500

    signatures = list(model.signatures.keys())
    return {"signatures": signatures}, 200

def normalize_text(value):
    """
    Ensures engine outputs become clean strings.
    """
    if value is None:
        return None

    # If list, take first element
    if isinstance(value, list):
        if not value:
            return None
        return normalize_text(value[0])

    # If tuple, same logic
    if isinstance(value, tuple):
        return normalize_text(value[0])

    # Convert everything else to string
    return str(value)

def format_diagnosis_text(plant, classification, management, probabilities):
    plant = normalize_text(plant)
    classification = normalize_text(classification)
    management = normalize_text(management)

    lines = []

    lines.append(f"Diagnosis for {plant}")
    lines.append("")

    if probabilities:
        top_disease, top_prob = probabilities[0]
        lines.append(
            f"The most likely disease affecting this plant is "
            f"{top_disease} ({round(top_prob, 2)}% probability)."
        )
    else:
        lines.append("No dominant disease could be identified.")

    if classification:
        lines.append("")
        lines.append(f"This disease is classified as {classification}.")

    if management:
        lines.append("")
        lines.append("Recommended management:")
        lines.append(management)

    if probabilities and len(probabilities) > 1:
        lines.append("")
        lines.append("Other possible conditions:")
        for disease, prob in probabilities[1:]:
            lines.append(f"• {disease} ({round(prob, 2)}%)")

    return "\n".join(lines)



# -------------------------
# API: IMAGE DIAGNOSIS
# -------------------------
@app.route("/api/diagnoseImage", methods=["POST"])
def diagnose_image():
    print("🔥 IMAGE → EXPERT SYSTEM PIPELINE 🔥")

    model = load_model_lazy()
    if model is None:
        return jsonify({"error": "Model unavailable"}), 500

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    img_array = preprocess_image(request.files["image"])

    try:
        infer = model.signatures["serving_default"]
        outputs = infer(tf.constant(img_array, dtype=tf.float32))
        print("🔎 MODEL OUTPUT KEYS:", list(outputs.keys()))

        probs = outputs["output_0"].numpy()[0]  # (36,)

        THRESHOLD = 0.5

        predicted_symptoms = [
            {
                "symptom_index": i,
                "symptom_name": LABEL_NAMES[i],
                "probability_percent": round(float(p) * 100, 2)
            }
            for i, p in enumerate(probs)
            if p >= THRESHOLD
        ]

        # 🔑 Extract symptom names for expert system
        symptom_names = [s["symptom_name"] for s in predicted_symptoms]

        print("🧠 Symptoms sent to expert system:", symptom_names)

        # 🔥 Run expert system
        engine = MultiSymptom(kb_data)
        engine.reset()
        engine.declare(symptomatic(name="Unknown", symptoms=symptom_names))
        engine.run()

        

        probabilities = engine.results.get("Probability", [])

        if not probabilities:
            return jsonify({
            "image_symptoms": predicted_symptoms,
            "expert_diagnosis": "No disease could be confidently determined.",
            "expert_probabilities": []
            }), 200

        classification = None
        management = None

        if probabilities:
            top_disease = probabilities[0][0]
            disease_info = lookup_disease_info(kb_data, top_disease)

            classification = disease_info.get("type")
            management = disease_info.get("management")

        diagnosis_text = format_diagnosis_text(
            plant="Unknown (Image-based)",
            classification=classification,
            management=management,
            probabilities=probabilities
        )

        response = {
            "image_symptoms": predicted_symptoms,
            "expert_diagnosis": diagnosis_text,
            "expert_probabilities": probabilities
        }   

        print("✅ FINAL RESPONSE:", response)
        return jsonify(response), 200

    except Exception as e:
        import traceback
        print("❌ IMAGE DIAGNOSE ERROR ❌")
        traceback.print_exc()
        return jsonify({
        "error": str(e),
        "type": type(e).__name__
        }), 500



# -------------------------
# API: SYMPTOM DIAGNOSIS
# -------------------------
@app.route("/api/diagnose", methods=["POST"])
def diagnose():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input provided"}), 400

    plant = data.get("plant")
    symptoms = data.get("symptoms", [])
    # temperature = data.get("temperature")
    # moistureDuration = data.get("moistureDuration")
    # print(f"{plant} {symptoms} {temperature} {moistureDuration}")

    return jsonify({
            "plant": plant,
            "diagnosis": "diag"
        }), 200

    try:
        engine = MultiSymptom(kb_data)
        engine.reset()
        engine.declare(symptomatic(name=plant, symptoms=symptoms))
        engine.run()

        # Extract raw engine results
        management = (
        engine.results.get("Management")
        or engine.results.get("management")
        )

        classification = (
        engine.results.get("Classification")
        or engine.results.get("type")
        )

        probabilities = engine.results.get("Probability", [])


        # Generate human-readable text
        text = format_diagnosis_text(
            plant=plant,
            classification=classification,
            management=management,
            probabilities=probabilities
        )

        return jsonify({
            "plant": plant,
            "diagnosis": text
        }), 200

    except Exception as e:
        print("Diagnose error:", str(e))
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

        cur.execute(
        'SELECT password_hash FROM users WHERE username = %s',
        (username,)
        )


        row = cur.fetchone()

        cur.close()
        conn.close()

        if row is None:
            return jsonify({"error": "Invalid username or password"}), 401

        stored_hash = row[0]

        if not check_password_hash(stored_hash, password):
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

        # Hash the plaintext password
        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        cur = conn.cursor()

        # Check if username already exists
        cur.execute(
            "SELECT 1 FROM users WHERE username = %s",
            (username,)
        )

        if cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({"error": "Username already exists"}), 409

        # Insert new user
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, password_hash)
        )

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Registration successful"}), 201

    except Exception as e:
        print("🔥 REGISTER ERROR:", repr(e))
        return jsonify({"error": "Server error"}), 500



# -------------------------
# ROOT
# -------------------------
@app.route("/")
def root():
    return {"message": "Service is running"}, 200


# -------------------------
# LOCAL RUN ONLY
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

