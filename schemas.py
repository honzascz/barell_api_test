barrel_schema = {
    "type": "object",
    "required": ["id", "qr", "rfid", "nfc"],
    "properties": {
        "id": {"type": "string", "format": "uuid"},
        "qr": {"type": "string"},
        "rfid": {"type": "string"},
        "nfc": {"type": "string"}
    },
    "additionalProperties": False
}

measurement_schema = {
    "type": "object",
    "required": ["id", "barrelId", "dirtLevel", "weight"],
    "properties": {
        "id": {"type": "string", "format": "uuid"},
        "barrelId": {"type": "string", "format": "uuid"},
        "dirtLevel": {"type": "number"},
        "weight": {"type": "number"}
    },
    "additionalProperties": False
}