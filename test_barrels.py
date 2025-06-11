import barrel_api
import requests
import pytest
import uuid
from schemas import barrel_schema
from jsonschema import validate

@pytest.fixture(scope="function") 
def created_barrel():
    # Fixture to create a barrel before each test and delete it after.
    # Returns: (input_payload, created_barrel_data)

    payload = barrel_api.new_barrel_payload()
    create_response = barrel_api.create_barrel(payload)
    assert create_response.status_code == 201
    barrel_data = create_response.json()

    yield payload, barrel_data

    # Teardown: delete the barrel after the test finishes
    delete_response = barrel_api.delete_barrel_by_id(barrel_data["id"])
    assert delete_response.status_code == 200, f"Failed to delete barrel {barrel_data['id']}"

def test_create_barrel(created_barrel):
    # Verifies that a barrel can be created and that the returned data matches the expected schema.

    # Create barrel
    _, create_barrel_data = created_barrel
    
    # Validate
    validate(instance=create_barrel_data, schema=barrel_schema)
    get_barrel_response = barrel_api.get_barrel_by_id(create_barrel_data['id'])
    assert get_barrel_response.status_code == 200
    
def test_get_barrel(created_barrel):
    # Verifies that a barrel can be retrieved by ID and its data matches the original payload.

    # Create barrel
    payload, barrel_data = created_barrel

    # Fetch barrel
    get_barrel_response = barrel_api.get_barrel_by_id(barrel_data['id'])

    # Validate GET response
    get_barrel_data = get_barrel_response.json()
    validate(instance=get_barrel_data, schema=barrel_schema)
    for key in ["Qr", "Rfid", "Nfc"]:
        assert payload[key] == get_barrel_data[key], f"Barrel with id '{get_barrel_data['id']}' contains unexpected value for key '{key}'"

def test_get_barrels():
    # Verifies that creating a new barrel that the new barrel is listed in the collection.
    
    # Fetch all barrels
    get_barrels_response = barrel_api.get_barrels()
    get_barrels_data = get_barrels_response.json()
    assert get_barrels_response.status_code == 200
    assert isinstance(get_barrels_data, list)
    
    # Add new barrel
    payload = barrel_api.new_barrel_payload()
    create_response = barrel_api.create_barrel(payload)
    assert create_response.status_code == 201
    created_barrel_data = create_response.json()
    get_added_barrels_response = barrel_api.get_barrels()
    get_added_barrels_data = get_added_barrels_response.json()

    # Validate new get barrels contains new barrel

    assert any(b["id"] == created_barrel_data["id"] for b in get_added_barrels_data), "Newly created barrel not found in the list"
    for barrel in get_added_barrels_data:
        validate(instance=barrel, schema=barrel_schema)

    # Delete added barrel
    delete_response = barrel_api.delete_barrel_by_id(created_barrel_data['id'])
    assert delete_response.status_code == 200, f"Failed to delete barrel {created_barrel_data['id']}"

### Negative scenarios

def test_get_non_existent_barrel():
    # Ensures the API returns 404 when trying to fetch a barrel with a non-existent ID.

    non_existent_id = str(uuid.uuid4())
    response = barrel_api.get_barrel_by_id(non_existent_id)
    assert response.status_code == 404 

def test_delete_non_existent_barrel():
    # Ensures the API returns 404 when trying to delete a barrel with a non-existent ID.

    non_existent_id = str(uuid.uuid4())
    response = barrel_api.delete_barrel_by_id(non_existent_id)
    assert response.status_code == 404

def test_create_duplicate_barrel(created_barrel):
    # Ensures the API does not allow creating a barrel with duplicate Qr/Rfid/Nfc values. Assumes uniqueness is enforced at API level.
    # Creates barrel by fixtures
    payload, create_barrel_data = created_barrel

    # Creates barrel with same payload as previous one
    crate_duplicit_barrel_response = barrel_api.create_barrel(payload)
    if  crate_duplicit_barrel_response.status_code == 201:
        barrel_api.delete_barrel_by_id(crate_duplicit_barrel_response.json()['id'])
        assert False 

@pytest.mark.parametrize("invalid_payload, missing_or_invalid_fields", [
    # One, Two, or all fields missing
    ({}, ["Qr", "Rfid", "Nfc"]),
    ({"Qr": "Qr_test"}, ["Rfid", "Nfc"]),
    ({"Rfid": "Rfid_test"}, ["Qr", "Nfc"]),
    ({"Nfc": "Nfc_test"}, ["Qr", "Rfid"]),
    ({"Qr": "Qr_test", "Rfid": "Rfid_test"}, ["Nfc"]),
    ({"Qr": "Qr_test", "Nfc": "Nfc_test"}, ["Rfid"]),
    ({"Rfid": "Rfid_test", "Nfc": "Nfc_test"}, ["Qr"]),
    
    # One field empty
    ({"Qr": "", "Rfid": "Rfid_test", "Nfc": "Nfc_test"}, ["Qr"]),
    ({"Qr": "Qr_test", "Rfid": "", "Nfc": "Nfc_test"}, ["Rfid"]),
    ({"Qr": "Qr_test", "Rfid": "Rfid_test", "Nfc": ""}, ["Nfc"]),
    
    # Two fields empty
    ({"Qr": "", "Rfid": "", "Nfc": "Nfc_test"}, ["Qr", "Rfid"]),
    ({"Qr": "", "Rfid": "Rfid_test", "Nfc": ""}, ["Qr", "Nfc"]),
    ({"Qr": "Qr_test", "Rfid": "", "Nfc": ""}, ["Rfid", "Nfc"]),

    # One field missing, one empty
    ({"Rfid": "Rfid_test", "Nfc": ""}, ["Qr", "Nfc"]),
    ({"Qr": "", "Nfc": "Nfc_test"}, ["Qr", "Rfid"]),
    ({"Qr": "Qr_test", "Rfid": ""}, ["Rfid", "Nfc"]),

    # One field has invalid type
    ({"Qr": 123, "Rfid": "Rfid_test", "Nfc": "Nfc_test"}, ["Qr"]),
    ({"Qr": 12.34, "Rfid": "Rfid_test", "Nfc": "Nfc_test"}, ["Qr"]),
    ({"Qr": True, "Rfid": "Rfid_test", "Nfc": "Nfc_test"}, ["Qr"]),
    ({"Qr": None, "Rfid": "Rfid_test", "Nfc": "Nfc_test"}, ["Qr"]),

    ({"Qr": "Qr_test", "Rfid": 456, "Nfc": "Nfc_test"}, ["Rfid"]),
    ({"Qr": "Qr_test", "Rfid": 45.67, "Nfc": "Nfc_test"}, ["Rfid"]),
    ({"Qr": "Qr_test", "Rfid": False, "Nfc": "Nfc_test"}, ["Rfid"]),
    ({"Qr": "Qr_test", "Rfid": None, "Nfc": "Nfc_test"}, ["Rfid"]),

    ({"Qr": "Qr_test", "Rfid": "Rfid_test", "Nfc": 789}, ["Nfc"]),
    ({"Qr": "Qr_test", "Rfid": "Rfid_test", "Nfc": 78.9}, ["Nfc"]),
    ({"Qr": "Qr_test", "Rfid": "Rfid_test", "Nfc": True}, ["Nfc"]),
    ({"Qr": "Qr_test", "Rfid": "Rfid_test", "Nfc": None}, ["Nfc"]),
])
def test_create_barrel_invalid_combinations(invalid_payload, missing_or_invalid_fields):
    # Tests various invalid combinations of missing or empty fields in the payload. The API is expected to return a 400 Bad Request. 

    response = barrel_api.create_barrel(invalid_payload)
    response_data = response.json()
    assert response.status_code == 400
    assert "errors" in response_data, f"Expected 'errors' key in response: {response_data}"

     # Normalize error field names to lowercase and remove $. for comparison
    error_fields = [field.lower().lstrip("$.") for field in response_data["errors"].keys()]


    for expected_field in missing_or_invalid_fields:
        assert expected_field.lower() in error_fields, (
            f"Expected error for field '{expected_field}', "
            f"but it was not found in response errors: {response_data['errors']}" 
    )


