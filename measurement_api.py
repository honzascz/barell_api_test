import requests
import utils
from configurations import TESTENV_URL
import uuid

def new_measurement_payload(barrel_id=None, dirtLevel=None, weight=None):
    barrel_id = str(uuid.uuid4()) if barrel_id in (None, '', []) else barrel_id
    dirtLevel = utils.get_random_double() if dirtLevel in (None, '', []) else dirtLevel
    weight = utils.get_random_double() if weight in (None, '', []) else weight

    payload = {
        "barrelId": barrel_id,
        "dirtLevel": dirtLevel,
        "weight": weight
    }
    return payload

def create_measurement(payload):
    return requests.post(TESTENV_URL + "/measurements", json=payload)

def get_measurements_by_id(id):
    return requests.get(TESTENV_URL + "/measurements/"+id)

def get_measurements():
    return requests.get(TESTENV_URL + "/measurements/")
