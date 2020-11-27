register = {
    "type": "object",
    "properties": {
        "username": {
            "type": "string", "minLength": 3, "maxLength": 20
        },
        "password": {
            "type": "string", "minLength": 7, "maxLength": 20
        }
    }
}

weather = {
    "type": "object",
    "properties": {
        "username": {
            "type": "string", "minLength": 3, "maxLength": 20
        },
        "password": {
            "type": "string", "minLength": 7, "maxLength": 20
        },
        "city": {
            "type": "string", "minLength": 2, "maxLength": 50
        },
        "format_temperature": {
            "type": "string", "minLength": 1, "maxLength": 1
        }
    }
}

refill = {
    "type": "object",
    "properties": {
        "username": {
            "type": "string", "minLength": 3, "maxLength": 20
        },
        "admin_pwd": {
            "type": "string", "minLength": 9, "maxLength": 9
        },
        "amount": {
            "type": "integer", "minimum": 1, "maximum": 20
        }
    }
}

