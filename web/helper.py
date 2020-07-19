""" Helper for weather API. """

from pymongo import MongoClient
import bcrypt


# ! repeatable code


def convert_to_celsius(array_temp: list) -> list:
    """ Convert temperature from Kelvin to Celsius.

    Args:
        temp_to_conv (list): temperatures to convert

    Returns:
        array with string temperatures in Celsius.
    """
    temp_return = [temp - 273.15 for temp in array_temp]
    t_string = ["{:.2f}".format(round(t, 2)) for t in temp_return]
    return t_string


def convert_to_fahrenheit(temp_array: list) -> list:
    """ Convert temperature from Kelvin to Fahrenheit.

    Args:
        temp_to_conv (list): temperatures to convert

    Returns:
        array with string temperature in Fahrenheit.
    """
    temp_return = [(temp - 273.15) * 9/5 + 32 for temp in temp_array]
    t_string = ["{:.2f}".format(round(t, 2)) for t in temp_return]
    return t_string


def change_keys_weather(
    temp_dict: dict, array_values: list
) -> None:
    """ Change keys from dictionary with data about temperature.

    Args:
        temp_dict (dict): dictionary with data about temperature
        array_values (list): values that needs to replace
                             data about temperature
    """
    temp_keys = ["Temperature",
                 "Minimum temperature",
                 "Maximum temperature",
                 "Feels like"]
    for i in range(4):
        temp_dict[temp_keys[i]] = array_values[i]
    # temp_dict["Temperature"] = array_values[0]
    # temp_dict["Minimum temperature"] = array_values[1]
    # temp_dict["Maximum temperature"] = array_values[2]
    # temp_dict["Feels like"] = array_values[3]


def validation_keys(valid_keys: list, keys: list, code: int) -> None:
    """ Keys validation.

    Args:
        valid_keys (list): list with valid keys for validation
        keys (list): list with keys that we want to check
        code (int): status code for exceptions

    Raises:
        KeyError: if keys are not valid
    """
    if len(valid_keys) != len(keys):
        raise KeyError("We are missing some keys!", code)

    for k in keys:
        if k not in valid_keys:
            raise KeyError(f"Key {k} is not valid!", code)


def username_exist(users: MongoClient, username: str) -> bool:
    """ Check if username exist in database.

    Args:
        users (MongoClient): database
        username (str): username

    Returns:
        bool: True if username exist, False otherwise
    """
    return False if users.find({"Username": username}).count() == 0 else True


def validation_password(
    users: MongoClient, password: str, username: str
) -> bool:
    """ Password validation.

    Args:
        users (MongoClient): database
        password (str): password for validation
        code (int): error code for exception

    Returns:
        bool: True if password is valid, False otherwise
    """
    password_db = users.find(
        {
            "Username": username
        }
    )[0]["Password"]
    hashed_pw = bcrypt.hashpw(password.encode("utf8"), password_db)
    return password_db != hashed_pw:


def count_tokens(users: MongoClient, username: str) -> int:
    """ Function that counts tokens.

    Args:
        users (MongoClient): [description]
        username (str): [description]

    Returns:
        int: [description]
    """
    num_of_tokens = users.find(
        {
            "Username": username
        }
    )[0]["Tokens"]
    return num_of_tokens


def update_tokens(
    users: MongoClient, username: str, operator_: object, amout: int
) -> None:
    """ Updating tokens.

    Args:
        users (MongoClient): database
        username (str): username
        operator_ (object): + or - for adding or removing tokens
        amout (int): number of tokens that you want to add or remove
    """
    num_tokens = users.find(
        {
            "Username": username
        }
    )[0]["Tokens"]
    new_tokens_value = operator_(num_tokens, amout)
    users.update(
        {
            "Username": username
        },
        {
            "$set": {"Tokens": new_tokens_value}
        }
    )


def validate_type(
    value: object, attr_name: str, type_: type,
    exception_: Exception, code: int,
    min_error=None, max_error=None,
    min_=None, max_=None
) -> object:
    """ Validation of any type.

    Args:
        value (object): value for validation
        attr_name (str): name of attribute that is requesting validation
        type_ (object): type of value
        exception_ (Exception): exception class that is raised
                                  when error occurred
        code (int): code for exception

    Kwargs:
        min_error (str): message for minimum error (default: {None})
        max_error (str): message for maximum error (default: {None})
        min_ (int): minimum value or length of value (default: {None})
        max_ (int): maximum value of length of value (default: {None})

    Raises:
        exception_: if value is not valid type
        exception_: if value or length of value is less then minumum
        exception_: if value or length of value is greater then maximum

    Returns:
        object: value if it's passed validation
    """
    if not isinstance(value, type_):
        raise exception_(
            f"Value for {attr_name} must be a {type_.__name__} type.",
            code
        )

    # value is sequence
    if hasattr(type_, "__getitem__"):
        validation_value = len(value)
    else:
        validation_value = value

    if min_ is not None and min_error is not None and validation_value < min_:
        raise exception_(min_error, code)

    if max_ is not None and max_error is not None and validation_value > max_:
        raise exception_(max_error, code)
    return value


def validate_city_and_country(data: dict, code: int) -> list:
    """ Make sure that city and country exist.

    Args:
        data (list): dictionary for validation
        code (int): code for exception if we don't find city and country

    Raises:
        KeyError: if city or country that is sent is not valid

    Returns:
        list with values that we want to send back to user as respond
    """
    try:
        main_dict = data["main"]
    except KeyError:
        raise KeyError(
            "We cannot found city you entered", code
        ) from None
    main_values = [main_dict["temp"],
                   main_dict["temp_min"],
                   main_dict["temp_max"],
                   main_dict["feels_like"]]
    weather_dict = data["weather"][0]
    wind_dict = data["wind"]

    other_values = [weather_dict["description"], wind_dict["speed"]]
    return main_values + other_values


def validate_temp(format_temp, temp_to_convert, weather_return):
    """ Temperature validation.

    Args:
        format_temp (str): C for Celsius, F for Fahrenheit or K for Kelvin
        temp_to_convert (float): temperature that we want to convert
        weather_return (dict): weather data

    Returns:
        float: converted temperature

    Raises:
        ValueError: if format_temp is not 'C' or 'F'' or 'K'
    """
    if format_temp == "C":
        temp_to_convert = convert_to_celsius(temp_to_convert)
        change_keys_weather(weather_return, temp_to_convert)
    elif format_temp == "F":
        temp_to_convert = convert_to_fahrenheit(temp_to_convert)
        change_keys_weather(weather_return, temp_to_convert)

    if format_temp != "F" and format_temp != "C" and format_temp != "K":
        raise ValueError
    return temp_to_convert
