""" Weather API that give some information about current weather. """

from config import app, api
from resources.register import Register
from resources.refill import Refill
from resources.weather import Weather


api.add_resource(Register, "/register")
api.add_resource(Weather, "/weather")
api.add_resource(Refill, "/refill")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
