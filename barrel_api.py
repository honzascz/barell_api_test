import requests
import utils
from configurations import TESTENV_URL


def new_barrel_payload():
    randomId = utils.get_random_id()
    payload = {
        "qr": "qr_"+str(randomId),
        "rfid": "rfid_"+str(randomId),
        "nfc": "nfc_"+str(randomId)
    }
    return payload

def create_barrel(payload):
    return requests.post(TESTENV_URL + "/barrels", json=payload)

def get_barrel_by_id(id):
    return requests.get(TESTENV_URL + "/barrels/"+id)

def get_barrels():
    return requests.get(TESTENV_URL + "/barrels/")

def delete_barrel_by_id(id):
    return requests.delete(TESTENV_URL + "/barrels/"+id)
