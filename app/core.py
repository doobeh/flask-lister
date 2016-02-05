"""
    listing.core
    ~~~~~~~~~~~~
    the gears to get the machine turning.
"""

from flask import Flask
from flask.ext.autoindex import AutoIndex
from flask.ext.basicauth import BasicAuth


class MultiBasicAuth(BasicAuth):
    def check_credentials(self, username, password):
        return app.config["USERS"].get(username) == password

def create_app(config_filename):
    factory_app = Flask(__name__)
    factory_app.config.from_pyfile(config_filename)
    return factory_app


app = create_app('../config.py')

MultiBasicAuth(app)
AutoIndex(app, browse_root=app.config["SHARED_DIRECTORY"])
