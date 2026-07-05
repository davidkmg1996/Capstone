import firebase_admin
from firebase_admin import firestore

# firebase emulators:start --export-on-exit

# Application Default credentials are automatically created.
app = firebase_admin.initialize_app()
db = firestore.client()