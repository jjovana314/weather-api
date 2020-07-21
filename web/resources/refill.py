import helper
import config
from flask import jsonify
from flask_restful import request, Resource
from werkzeug.wrappers import BaseResponse
from operator import add


class Refill(Resource):
    """ Refill tokens. """
    def post(self) -> BaseResponse:
        """ Called when we have a POST request.

        Returns:
            BaseResponse object with message and code
        """
        # add admin's password and username to database
        users.insert(
            {
                "Username": config.admin_name,
                "Password": config.admin_pwd_crypted
            }
        )
        data = request.get_json()
        is_valid, msg, code = helper.user_validation(
            config.users, data, config.refill_keys_valid, is_register=False
        )
        if not is_valid:
            return jsonify({"Message": msg, "Code": code})
        username = data["username"]
        amount_tokens = data["amount"]

        # refill tokens
        helper.update_tokens(
            config.users, username, add, amount_tokens
        )
        return jsonify(
            {
                "Message": "Tokens updated successfully.",
                "Code": helper.OK
            }
        )
