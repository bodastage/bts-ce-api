# Import flask and template operators
from flask import Flask, render_template, request
from flask_cors import CORS
# Import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

# Import Flask Marshmallow
from flask_marshmallow import Marshmallow

# Define the WSGI application object
app = Flask(__name__)

# Enable CORS -- Remove this if not useful
CORS(app,  origins="*")


# This is added to handle CORS
# Taken from https://mortoray.com/2014/04/09/allowing-unlimited-access-with-cors/
@app.after_request
def add_cors(resp):
    """ Ensure all responses have the CORS headers. This ensures any failures are also accessible
        by the client. """

    resp.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin','*')
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS, GET'
    resp.headers['Access-Control-Allow-Headers'] = request.headers.get(
        'Access-Control-Request-Headers', 'Authorization' )
    # set low for debugging
    # if app.debug:
    #    resp.headers['Access-Control-Max-Age'] = '1'

    return resp


# Intercept pre-flight requests
@app.before_request
def handle_options_header():
    if request.method == 'OPTIONS':
        headers = {}
        headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        headers['Access-Control-Allow-Credentials'] = 'true'
        headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS, GET'
        headers['Access-Control-Allow-Headers'] = request.headers.get(
            'Access-Control-Request-Headers', 'Authorization')
        return ('', 200, headers)


# TP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


# Configurations
app.config.from_object('btsapi.config')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Import modules using the blueprint handlers variable (mod_vendors)
from btsapi.modules.vendors.controllers import mod_vendors as vendors_module
from btsapi.modules.users.controllers import mod_users as mod_users
from btsapi.modules.authentication.controllers import mod_auth as mod_auth
from btsapi.modules.networkbaseline.controllers import mod_networkbaseline as mod_networkbaseline

# Register blueprint(s)
app.register_blueprint(vendors_module)
app.register_blueprint(mod_users)
app.register_blueprint(mod_auth)
app.register_blueprint(mod_networkbaseline)
