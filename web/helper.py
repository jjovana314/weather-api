""" Helper for weather API. """

from pymongo import MongoClient
from http import HTTPStatus
from jsonschema import validate, ValidationError
from json import dumps, loads
import bcrypt
import exceptions
import exception_messages as ex_m


# status codes
OK = HTTPStatus.OK
INVALID_USERNAME = 301
INVALID_PASSWORD = 302
OUT_OF_TOKENS = 303
DATA_NOT_EXIST = 304
INVALID_ADMIN_PASSWORD = 305
KEYS_NOT_VALID = 306


def schema_validation(schema: dict, data: dict) -> None:
    """ JSON schema validation.

    Arguments:
        schema {dict} -- valid dictionary
        data {dict} -- dictionary for validation

    Raises:
        SchemaError: if data dictionary is not valid
    """
    # we want json data, so we have to dump our data into json string
    data = dumps(data)
    try:
        # try to do validation for our json data
        validate(loads(data), schema)
    except ValidationError as ex:
        # ! here we do not except JSONDecodeError, remember that!
        ex_str = str(ex)
        for idx, value in enumerate(ex_m.schema_errors):
            # create appropriate message for user
            # if there is exception occured
            if value in ex_str:
                raise ex_m.schema_exceptions[idx](ex_m.error_messages[idx])


def convert_temperature(temp_array: list, to_celsius=False) -> list:
    """ Convert temperature from Kelvin to Fahrenheit or Celsius.

    Args:
        temp_array (list): temperatures to convert
        to_celsius (bool): True if we want to convert temperature in Celsius.
                            Default is False.

    Kwargs:
        to_celsius (bool): True if we want to convert temperature to Celsius.
                           Default is False.

    Returns:
        array with converted temperature formatted as string.
    """
    if to_celsius:
        converted_temp = [temp - 273.15 for temp in temp_array]
    else:
        # converting to Fahrenheit
        converted_temp = [(temp - 273.15) * 9/5 + 32 for temp in temp_array]

    temp_formatted = ["{:.2f}".format(round(temp, 2))
                     for temp in converted_temp]
    return temp_formatted


def change_keys_weather(
    temp_dict: dict, array_values: list, keys_weather_return: list
) -> None:
    """ Change keys from dictionary with data about temperature.

    Args:
        temp_dict (dict): dictionary with data about temperature
        array_values (list): values that needs to replace
                             data about temperature
        keys_weather_return (list): keys for replacing

    Note:
        length of array_values and keys_weather_return must be equal
    """
    for i in range(len(array_values)):
        temp_dict[keys_weather_return[i]] = array_values[i]


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
        username (str): username

    Returns:
        bool: True if password is valid, False otherwise
    """
    password_db = users.find(
        {
            "Username": username
        }
    )[0]["Password"]
    hashed_pw = bcrypt.hashpw(password.encode("utf8"), password_db)
    return password_db == hashed_pw


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
    users: MongoClient, username: str, operator_: object, amount: int
) -> None:
    """ Updating tokens.

    Args:
        users (MongoClient): database
        username (str): username
        operator_ (object): + or - for adding or removing tokens
        amount (int): number of tokens that you want to add or remove
    """
    num_tokens = users.find(
        {
            "Username": username
        }
    )[0]["Tokens"]
    new_tokens_value = operator_(num_tokens, amount)
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
                    if value or length of value is less then minumum
                    if value or length of value is greater then maximum

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


def validate_city_and_country(
    data: dict, code: int, main_keys_valid: list
) -> list:
    """ Make sure that city and country exist.

    Args:
        data (list): dictionary for validation
        code (int): code for exception if we don't find city and country
        main_keys_valid (list): list with valid keys

    Raises:
        KeyError: if city or country that was sent is not valid

    Returns:
        list with values that we want to send back to user as respond
    """
    try:
        main_dict = data["main"]
    except KeyError:
        raise KeyError(
            "We cannot found city you entered", code
        ) from None

    main_values = [main_dict[key] for key in main_keys_valid]

    weather_dict = data["weather"][0]
    wind_dict = data["wind"]

    other_values = [weather_dict["description"], wind_dict["speed"]]
    return main_values + other_values


def validate_temp(
    format_temp: str, temp_to_convert: float, weather_return: dict
) -> float:
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
    weather_keys = list(weather_return.keys())
    if format_temp == "C":
        temp_to_convert = convert_temperature(
            temp_to_convert, to_celsius=True
        )
        change_keys_weather(
            weather_return, temp_to_convert, weather_keys[:4]
        )
    elif format_temp == "F":
        temp_to_convert = convert_temperature(temp_to_convert)
        change_keys_weather(
            weather_return, temp_to_convert, weather_keys[:4]
        )

    if format_temp != "F" and format_temp != "C" and format_temp != "K":
        raise ValueError
    return temp_to_convert


def user_validation(
    users: MongoClient, data: dict, valid_keys: list,
    is_register=False) -> tuple:
    """ Validate data about user.

    Args:
        users (MongoClient): database
        data (dict): data for validation
        valid_keys (list): list with valid keys for validation

    Kwargs:
        is_register (bool): True if class caller is Register class.
                            Default is False.

    Returns:
        tuple with status validation (True if data is valid,
        False otherwise), second tuple element is None if
        data is valid, otherwise it is message about error,
        third tuple element is code if error occures, otherwise
        it is OK code (200)
    """
    keys = list(data.keys())
    try:
        validation_keys(valid_keys, keys, KEYS_NOT_VALID)
    except KeyError as ex:
        return (
            False, ex.args[0], ex.args[1]
        )
    password = data.get("admin_pwd", None)
    if password is None:
        # if password is not admin password we assume
        # that it is user's password
        try:
            username = data["username"]
            password = data["password"]
        except KeyError:
            return (
                False,
                "Please enter username and password",
                DATA_NOT_EXIST
            )
    usr_exist = username_exist(users, username)
    # if user needs to be registered in database
    if is_register:
        if usr_exist:
            return (
                False, "This username already exist", INVALID_USERNAME
            )
        return True, None, OK
    # if user tries to login or check weather
    else:
        if not usr_exist:
            return (
                False, "This user does not exist", INVALID_USERNAME
            )
        # validate password if user does not wants to register
        valid_pwd = validation_password(users, password, username)
        if not valid_pwd:
            return (
                False, "Please enter valid password", INVALID_PASSWORD
            )
    return True, None, OK
