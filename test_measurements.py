import measurement_api
import requests
import pytest
import uuid
import barrel_api
from schemas import measurement_schema
from jsonschema import validate

def test_create_measurement():
    # Verifies that a measurement can be created and that the returned data matches the expected schema.
    
    # Create barrel
    barrel_id = create_barrel()
    payload = measurement_api.new_measurement_payload(barrel_id)
    # Create measurement
    create_measurement_response = measurement_api.create_measurement(payload)
    create_measurement_data = create_measurement_response.json()
    
    # Validate
    assert create_measurement_response.status_code == 201
    validate(instance=create_measurement_data, schema=measurement_schema)

    get_measurement_response = measurement_api.get_measurements_by_id(create_measurement_data['id'])
    assert get_measurement_response.status_code == 200
    # Clean up
    delete_barrel(barrel_id)

def test_get_measurement():
    # Verifies that a measurement can be retrieved by ID and its data matches the original payload.

    # Prepare test data
    barrel_id = create_barrel()
    payload = measurement_api.new_measurement_payload(barrel_id)
    create_measurement_response = measurement_api.create_measurement(payload)
    create_measurement_data = create_measurement_response.json()
    assert create_measurement_response.status_code == 201

    # Test get and validate
    get_measurement_response = measurement_api.get_measurements_by_id(create_measurement_data['id'])
    assert get_measurement_response.status_code == 200
    get_measurement_data = get_measurement_response.json()
    validate(instance=get_measurement_data, schema=measurement_schema)

    for key in ["barrelId", "dirtLevel", "weight"]:
        assert payload[key] == get_measurement_data[key], f"Barrel with id '{get_measurement_data['id']}' contains unexpected value for key '{key}'"

    # Clean up
    delete_barrel(barrel_id)

def test_get_measurements():
    # Verifies that creating a new measurement that the new measurement is listed in the collection.
    
    # Fetch all measurements
    get_measurements_response = measurement_api.get_measurements()
    get_measurements_data = get_measurements_response.json()
    assert get_measurements_response.status_code == 200
    assert isinstance(get_measurements_data, list)
    
    # Add new measurement
    barrel_id = create_barrel()
    payload = measurement_api.new_measurement_payload(barrel_id)
    create_response = measurement_api.create_measurement(payload)
    assert create_response.status_code == 201
    created_measurement_data = create_response.json()
    get_added_measurements_response = measurement_api.get_measurements()
    get_added_measurements_data = get_added_measurements_response.json()

    # Validate new get measurements contains new measurement

    assert any(b["id"] == created_measurement_data["id"] for b in get_added_measurements_data), "Newly created measurement not found in the list"
    for measurement in get_added_measurements_data:
        validate(instance=measurement, schema=measurement_schema)

# Allow TC if multiple measurements is possible for one barrel
"""
def test_create_multiple_measurements_for_barrel():
    # Verifies that creating multiple measurements for one barrel is possible.
    barrel_id = create_barrel()
    for i in range(10):
        payload = measurement_api.new_measurement_payload(barrel_id)
        create_response = measurement_api.create_measurement(payload)
        assert create_response.status_code == 201"""

### Negative scenarios

def test_get_non_existent_measurement():
    # Ensures the API returns 404 when trying to fetch a measurement with a non-existent ID.

    non_existent_id = str(uuid.uuid4())
    response = measurement_api.get_measurement_by_id(non_existent_id)
    assert response.status_code == 404 

def test_create_measurement_for_nonexistent_barrel():
    # Ensures the API returns 404 when trying to create a measurement on non-existent barrel.

    payload=measurement_api.new_measurement_payload() # empty barrel id to generate random
    response = measurement_api.create_measurement(payload)
    assert response.status_code == 404

@pytest.mark.parametrize("payload_template, missing_or_invalid_fields", [
    # All required fields missing
    (lambda barrel_id: {}, ["barrelId", "dirtLevel", "weight"]),

    # Two fields missing
    (lambda barrel_id: {"barrelId": barrel_id}, ["dirtLevel", "weight"]),
    (lambda barrel_id: {"dirtLevel": 1.2}, ["barrelId", "weight"]),
    (lambda barrel_id: {"weight": 10.0}, ["barrelId", "dirtLevel"]),

    # One field missing
    (lambda barrel_id: {"barrelId": barrel_id, "dirtLevel": 1.2}, ["weight"]),
    (lambda barrel_id: {"barrelId": barrel_id, "weight": 10.0}, ["dirtLevel"]),
    (lambda barrel_id: {"dirtLevel": 1.2, "weight": 10.0}, ["barrelId"]),

    # Invalid barrelId format
    (lambda barrel_id: {"barrelId": "not-a-uuid", "dirtLevel": 0.5, "weight": 1.0}, ["barrelId"]),

    # Invalid dirtLevel types
    (lambda barrel_id: {"barrelId": barrel_id, "dirtLevel": "heavy", "weight": 1.0}, ["dirtLevel"]),
    (lambda barrel_id: {"barrelId": barrel_id, "dirtLevel": True, "weight": 1.0}, ["dirtLevel"]),
    (lambda barrel_id: {"barrelId": barrel_id, "dirtLevel": None, "weight": 1.0}, ["dirtLevel"]),
    (lambda barrel_id: {"barrelId": barrel_id, "dirtLevel": -0.1, "weight": 1.0}, ["dirtLevel"]),
    (lambda barrel_id: {"barrelId": barrel_id, "dirtLevel": 0, "weight": 1.0}, ["dirtLevel"]),

    # Invalid weight types
    (lambda barrel_id: {"barrelId": barrel_id, "dirtLevel": 0.5, "weight": "light"}, ["weight"]),
    (lambda barrel_id: {"barrelId": barrel_id, "dirtLevel": 0.5, "weight": False}, ["weight"]),
    (lambda barrel_id: {"barrelId": barrel_id, "dirtLevel": 0.5, "weight": None}, ["weight"]),
    (lambda barrel_id: {"barrelId": barrel_id, "dirtLevel": 0.5, "weight": -0.1}, ["weight"]),
    (lambda barrel_id: {"barrelId": barrel_id, "dirtLevel": 0.5, "weight": 0}, ["weight"]),
]) 

def test_create_measurement_invalid_inputs(payload_template, missing_or_invalid_fields):
    barrel_id = create_barrel()
    payload = payload_template(barrel_id)
    response = measurement_api.create_measurement(payload)
    response_data = response.json()

    assert "errors" in response_data, f"Expected 'errors' key in response: {response_data}"
    
     # Normalize error field names to lowercase and remove $. for comparison
    error_fields = [field.lower().lstrip("$.") for field in response_data["errors"].keys()]


    for expected_field in missing_or_invalid_fields:
        assert expected_field.lower() in error_fields, (
            f"Expected error for field '{expected_field}', "
            f"but it was not found in response errors: {response_data['errors']}" 
    )

# Helpers
def create_barrel():
    payload = barrel_api.new_barrel_payload()
    create_response = barrel_api.create_barrel(payload)
    assert create_response.status_code == 201
    return str(create_response.json()['id'])

def delete_barrel(barrel_id):
    create_response = barrel_api.delete_barrel_by_id(barrel_id)
    assert create_response.status_code == 200


    


