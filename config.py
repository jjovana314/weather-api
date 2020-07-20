import bcrypt


# some global variables
tokens_start = 10

password_length = 8
username_length = 5
min_username = f"Useranme must be at least {username_length} long"
min_password = f"Password must be at least {password_length} long"

register_keys_valid = ["username", "password"]

weather_keys_valid = [
    "username", "password", "city", "format_temperature"
]
main_keys_valid = ["temp", "temp_max", "temp_min", "feels_like"]
keys_weather_return = [
    "Temperature", "Minimum temperature", "Maximum temperature",
    "Feels like", "Description", "Wind speed"
]

admin_pwd = "ad002.C2f"
admin_name = "admin"
refill_keys_valid = ["username", "admin_pwd", "amount"]
# crypting admin's password and inserting into database
admin_pwd_crypted = bcrypt.hashpw(
    admin_pwd.encode("utf8"), bcrypt.gensalt()
)