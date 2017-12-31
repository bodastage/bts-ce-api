# Import flask and template operators
from flask import Flask, render_template

# Import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

# Import Flask Marshmallow
from flask_marshmallow import Marshmallow

# Define the WSGI application object
app = Flask(__name__)


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

# Register blueprint(s)
app.register_blueprint(vendors_module)