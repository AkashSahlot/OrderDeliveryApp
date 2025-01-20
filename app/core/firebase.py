from firebase_admin import credentials, initialize_app
import firebase_admin
from google.cloud import firestore

def initialize_firebase():
    try:
        # Check if Firebase is already initialized
        firebase_admin.get_app()
    except ValueError:
        # Initialize Firebase with explicit credentials
        cred = credentials.Certificate("app/service-account.json")
        initialize_app(cred, {
            'projectId': 'your-project-id'  # Add your Firebase project ID here
        })

# Initialize Firestore client
db = firestore.Client.from_service_account_json("app/service-account.json") 