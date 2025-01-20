from firebase_admin import credentials, initialize_app
import firebase_admin
from google.cloud import firestore
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

def initialize_firebase():
    try:
        # Check if Firebase is already initialized
        firebase_admin.get_app()
    except ValueError:
        # Initialize Firebase with explicit credentials
        cred = credentials.Certificate("app/service-account.json")
        initialize_app(cred, {
            'projectId': os.getenv('FIREBASE_PROJECT_ID')  # Add your Firebase project ID here
        })

# Initialize Firestore client
db = firestore.Client.from_service_account_json("app/service-account.json") 