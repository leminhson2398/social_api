from starlette.config import Config
import logging
import sys
import firebase_admin
from firebase_admin import credentials, firestore


# init firebase connection:
credential = credentials.Certificate("./social_api/service_Account.json")
firebase_admin.initialize_app(credential=credential)
firestoreDB = firestore.client()

# append for import
sys.path.append("..")


# configure logging:
logging.basicConfig(format="%(asctime)s - %(message)s",
                    datefmt="%m/%d/%Y %I:%M:%S %p", level=logging.ERROR)

config = Config("./social_api/.env")
