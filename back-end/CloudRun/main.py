import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np
from ESTest import MultiSymptom, load_json, symptomatic
from google.cloud import storage
import tensorflow as tf

app = Flask(__name__)

# -------------------------
# CORS CONFIG
# -------------------------
ALLOWED_ORIGINS = [
    "http://localhost:8081",
    "https://plantdisease-932821527783.europe-west1.run.app",
    "https://diseaseidentity.com",
    "https://www.diseaseidentity.com"
]

CORS(
    app,
    resources={r"/*": {"origins": ALLOWED_ORIGINS}},
    supports_credentials=True,
    allow_headers="*",
    methods=["GET", "POST", "OPTIONS"]
)


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


# -------------------------
# IMAGE PREPROCESSING
# -------------------------
def preprocess_image(file_like, target_size=(224, 224)):
    img = Image.open(file_like).convert("RGB")
    img = img.resize(target_size)
    arr = np.array(img).astype("float32") / 255.0
    arr = np.expand_dims(arr, axis=0)
    return arr


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


# -------------------------
# API: IMAGE DIAGNOSIS
# -------------------------
@app.route("/api/diagnoseImage", methods=["POST"])
def diagnose_image():
    model = load_model_lazy()
    if model is None:
        return jsonify({"error": "Model unavailable"}), 500

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    img_array = preprocess_image(request.files["image"])

    try:
        # Use the default signature
        infer = model.signatures.get("serving_default")
        if infer is None:
            return {"error": "No serving_default signature in model"}, 500

        # Call the TF ConcreteFunction
        outputs = infer(tf.constant(img_array, dtype=tf.float32))

        # Usually contains only one output:
        # {"output_0": [probabilities]}
        output_key = list(outputs.keys())[0]
        preds = outputs[output_key].numpy()[0]

        predicted_idx = int(np.argmax(preds))
        confidence = float(np.max(preds) * 100)

        return jsonify({
            "predicted_class_index": predicted_idx,
            "confidence_percent": confidence
        }), 200

    except Exception as e:
        print("Image diagnose error:", str(e))
        return jsonify({"error": str(e)}), 500


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

    try:
        engine = MultiSymptom(kb_data)
        engine.reset()
        engine.declare(symptomatic(name=plant, symptoms=symptoms))
        engine.run()
        management = engine.results.get("Management",[])
        classification = engine.results.get("Classification",[])
        probs = engine.results.get("Probability", [])
        return {"plant": plant, "probabilities": probs, "classification": classification, "management": management}, 200

    except Exception as e:
        print("Diagnose error:", str(e))
        return {"error": str(e)}, 500


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
