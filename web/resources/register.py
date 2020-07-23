from flask_restful import Resource, request
from flask import jsonify
from werkzeug.wrappers import BaseResponse
import helper
import bcrypt
import config


class Register(Resource):
    """ User registration. """
    def post(self) -> BaseResponse:
        """ Called when we have a POST request.

        Returns:
            BaseResponse object with message and code
        """
        data = request.get_json()
        # data_keys_list = list(data.keys())
        is_valid, msg, code = helper.user_validation(
            config.users, data, config.register_keys_valid, is_register=True
        )
        if not is_valid:
            return jsonify({"Message": msg,"Code": code})
        username = data["username"]
        password = data["password"]

        try:
            username = helper.validate_type(
                username, "username", str,
                ValueError, helper.INVALID_USERNAME,
                min_error=config.min_username, min_=config.username_length
            )
        except ValueError as ex:
            return jsonify({"Message": ex.args[0], "Code": ex.args[1]})

        try:
            password = helper.validate_type(
                password, "password", str,
                ValueError, helper.INVALID_PASSWORD,
                min_error=config.min_password, min_=config.password_length
            )
        except ValueError as ex:
            return jsonify({"Message": ex.args[0], "Code": code.args[1]})

        # hash password
        hashed_pw = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())
        # add user to database
        config.users.insert(
            {
                "Username": username,
                "Password": hashed_pw,
                "Tokens": config.tokens_start
            }
        )
        return jsonify(
            {
                "Message": "You signed up successfully.",
                "Code": helper.OK
            }
        )
