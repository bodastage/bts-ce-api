from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  jsonify, make_response
from btsapi.modules.users.models import User, UserSchema
from btsapi import app, db
import datetime


# @TODO: Change this endpoint to /api/authentication
mod_auth = Blueprint('authetication', __name__, url_prefix='/authenticate')


@mod_auth.route('/', methods=['POST','OPTIONS'])
def authenticate_user():
    """Get a list of all the users in the system"""

    return jsonify({"token":"123456789"})
