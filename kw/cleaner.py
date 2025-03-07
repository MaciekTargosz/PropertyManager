import firebase_admin
import constants
from firebase_admin import firestore
from google.cloud.firestore_v1 import FieldFilter
from google.api_core import exceptions

firebaseConfig = {
    'databaseURL': 'https://propertymanager-385720-default-rtdb.europe-west1.firebasedatabase.app',
    'storageBucket': "propertymanager-385720.appspot.com",
}

# app = firebase_admin.initialize_app()
cred = firebase_admin.credentials.Certificate("propertymanager-385720-firebase-adminsdk-g6q8l-1ae1ecdcae.json")
default_app = firebase_admin.initialize_app(cred, firebaseConfig)
db = firestore.client()

kws_ref = db.collection(constants.TARGET_DB)
query = kws_ref.where(filter=FieldFilter("kw_district_code", "==", "KR1K")).order_by("kw_id", direction=firestore.Query.DESCENDING).limit(
    100)
results = query.get()
for result in results:
    print(result.to_dict()['kw_id'])