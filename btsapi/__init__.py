# Import flask and template operators
from flask import Flask, render_template, request
from flask.sessions import SecureCookieSessionInterface

from btsapi.extensions import db, ma, login_manager

from flask_cors import CORS

import base64

# Authentication and authorization functionality from flask_login
from flask_login import user_loaded_from_header, user_loaded_from_request, LoginManager
from flask import g

from btsapi.modules.users.models import User



# This prevents setting the Flask Session cookie whenever the user authenticated using your header_loader.
# Reference: https://flask-login.readthedocs.io/en/latest/
class CustomSessionInterface(SecureCookieSessionInterface):
    """Prevent creating session from API requests."""
    def save_session(self, *args, **kwargs):
        if g.get('login_via_header'):
            return
        return super(CustomSessionInterface, self).save_session(*args,
                                                                **kwargs)


def create_app():
    # Define the WSGI application object
    app = Flask(__name__)

    # Disable strict forward slashed requirement
    app.url_map.strict_slashes = False

    # Configurations
    app.config.from_object('btsapi.config')

    # Define the database object which is imported
    # by modules and controllers
    db.init_app(app) #flask_sqlalchemy
    ma.init_app(app) #flask_marshmallow

    print ("Were are here")

    # Enable CORS -- Remove this if not useful
    CORS(app,  origins="*")

    login_manager.init_app(app)

    # Disable sessions for API calls
    app.session_interface = CustomSessionInterface()

    return app


@user_loaded_from_header.connect
def user_loaded_from_header(self, user=None):
    g.login_via_header = True


@login_manager.header_loader
def load_user_from_header(header_val):
    header_val = header_val.replace('Basic ', '', 1)
    try:
        header_val = base64.b64decode(header_val)
    except TypeError:
        pass
    return User.query.filter_by(api_key=header_val).first()

