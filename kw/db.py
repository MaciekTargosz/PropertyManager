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


def add(data):
    entity_id = data['kw_id'].replace('/', '')
    db.collection(constants.TARGET_DB).document(entity_id).set(data)


def get_last_record_value(district_code):
    try:
        kws_ref = db.collection(constants.TARGET_DB)
        query = kws_ref.where(filter=FieldFilter("kw_district_code", "==", district_code)).order_by("kw_id",
                                                                                                    direction=firestore.Query.DESCENDING).limit(
            1)
        results = query.get()
        if len(results) == 0:
            return "KR1K/00000000/0"
        else:
            return results[0].to_dict()['kw_id']
    except exceptions.FailedPrecondition as e:
        return "KR1K/00000000/0"
