from flask import Flask, request
from flask_cors import CORS
import json
from flask import jsonify

from firestore import db

app = Flask(__name__)

CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"]
)

@app.route('/getFiles')
def get_files():
    documents = db.collection("files").where("parentId", "==", "")
    files = []
    for document in documents.stream():
        files.append(document.to_dict() | {"documentId": document.id})
    return files

@app.route("/getSubFiles", methods=["POST"])
def get_sub_files():
    sub_files = db.collection("files").where("parentId", "==", request.get_json()["parentId"])

    data = []
    for file in sub_files.stream():
        data.append(file.to_dict())
    return data

@app.route("/addFolder", methods=["POST"])
def add_folder():
    payload = request.get_json()
    print(payload)
    db.collection("files").add({"name": payload["name"], "parentId": payload["parentId"]})
    return ""