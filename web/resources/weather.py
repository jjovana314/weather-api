from flask_restful import Resource, request
from flask import jsonify
from werkzeug.wrappers import BaseResponse
from operator import sub, add
import requests
import helper
import bcrypt
import json
import config
import requests


class Weather(Resource):
    """ Send user information about weather in their city. """
    def post(self):
        """ Called when we have a POST request.

        Returns:
            BaseResponse object with message and code
        """
        data = request.get_json()

        # if we do, than we can take values that is sent
        is_valid, msg, code = helper.user_validation(
            config.users, data, config.weather_keys_valid, is_register=False
        )
        if not is_valid:
            return jsonify({"Message": msg, "Code": code})

        city = data["city"]
        username = data["username"]
        format_temp = str(data["format_temperature"]).upper()
        if helper.count_tokens(config.users, username) <= 0:
            return jsonify(
                {
                    "Message": "You are out of tokens, please refill.",
                    "Code": helper.OUT_OF_TOKENS
                }
            )

        # get data from openweather web app
        r = requests.get(f"http://api.openweathermap.org/data/2.5/"
                         f"weather?q={city}"
                         f"&appid=5b18652fc700a44670ccb177ade90c69")
        data_return = dict(r.json())
        # validate that city and counrry exist
        try:
            all_values = helper.validate_city_and_country(
                data_return, helper.DATA_NOT_EXIST, config.main_keys_valid
            )
        except KeyError as ex:
            return jsonify({"Message": ex.args[0], "Code": ex.args[1]})

        weather_return = dict(zip(config.keys_weather_return, all_values))
        temp_to_convert = [weather_return[key] for key in list(weather_return.keys())[:4]]

        try:
            temp_to_convert = helper.validate_temp(
                format_temp, temp_to_convert, weather_return
            )
        except ValueError:
            return jsonify(
                {
                    "Message": ("For temperature in Celsius send 'C', "
                                "for temperature in Fahrenheit send 'F'."),
                    "Code": helper.KEYS_NOT_VALID
                }
            )

        # don't forget to take one token from user
        helper.update_tokens(config.users, username, sub, 1)
        # finaly, return valid respond with OK status
        return jsonify(
            {
                "Message":
                {
                    f"This is weather for {city}": weather_return
                },
                "Code": helper.OK
            }
        )
