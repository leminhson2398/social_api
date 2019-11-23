from starlette.config import Config
import logging
import sys
from firebase_admin import credentials, firestore, initialize_app
import os
from google.cloud import storage

CURDIR: str = os.path.dirname(
    os.path.abspath(__file__)
)
SERVICE_ACCOUNT_FILE_NAME: str = "service_Account.json"
STORAGE_SERVICE_FILE_NAME: str = "storageService.json"
# init firebase connection:
credential = credentials.Certificate(
    os.path.join(CURDIR, SERVICE_ACCOUNT_FILE_NAME)
)
initialize_app(credential=credential)
firestoreDB = firestore.client()

# set environmental variable for google cloud storage:
os.environ.update({
    "GOOGLE_APPLICATION_CREDENTIALS": os.path.join(CURDIR, STORAGE_SERVICE_FILE_NAME)
})

# storage bucket name:
BUCKET_NAME: str = "firestore-257604.appspot.com"

# init google cloud storage client:
GC_CLOUD_CLIENT = storage.Client()

# get bucket with bucket name:
GC_BUCKET = GC_CLOUD_CLIENT.get_bucket(BUCKET_NAME)
if not GC_BUCKET.requester_pays:
    GC_BUCKET.requester_pays = True
    GC_BUCKET.patch()

# append for import
sys.path.append("..")


# configure logging:
logging.basicConfig(
    format="%(asctime)s - %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.ERROR
)

config = Config(
    os.path.join(CURDIR, ".env")
)
