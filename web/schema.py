"""
This is schema for Weather API.

* Register
    - POST
        /register
    - username, password
    - OK 200
    - INVALID_USERNAME 301
    - KEYS_NOT_VALID 306
    * Return if OK:
        {
            "Message": "You successfully signed for an API.",
            "Code": 200
        }

* Weather
    - POST
        /weather
    - username, password, country, city, format_temperature (validation)
    - OK 200
    - INVALID_USERNAME 301
    - INVALID_PASSWORD 302
    - OUT_OF_TOKENS 303
    - DATA_NOT_EXIST 304
    - KEYS_NOT_vALID 306
    * Return if OK:
        {
            "Message": "This is weather for *CITY*, *COUNTRY*: {
                "Temperature": *FORMAT_TEMPERATURE*,
                "Minimum temperature": *FORMAT_TEMPERATURE*,
                "Maximum temperature": *FORMAT_TEMPERATURE*,
                "Feels like": *FORMAT_TEMPERATURE*,
                "Description": *str*,
                "Wind speed": *float*
            },
            "Code": 200
        }

* Refill
    - POST
        /refill
    - username, admin_pwd, amout
    - OK 200
    - INVALID_USERNAME 301
    - INVALID_ADMIN_PASSWORD 305
    - KEYS_NOT_VALID 306
    * Return if OK:
        {
            "Message": "Tokens added successfully.",
            "Code": 200
        }
"""
