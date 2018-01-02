from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  jsonify, make_response
from btsapi.modules.users.models import User, UserSchema
from btsapi import app, db
import datetime


# @TODO: Change this endpoint to /api/authentication
mod_auth = Blueprint('authetication', __name__, url_prefix='/authenticate')


@mod_auth.route('/', methods=['POST'])
def authenticate_user():
    """Get a list of all the users in the system"""
    username = request.headers.get('x-auth-username')
    password = request.headers.get('X-Auth-Password')
    user = User.query.filter_by(username=username, password=password).first()

    app.logger.info("headers: {}".format(request.headers))
    app.logger.info("username: {}".format(username))
    app.logger.info("password: {}".format(password))

    if user is not None:
        ma_schema = UserSchema()

        return jsonify(ma_schema.dump(user).data)
    else:
        return jsonify({"message":"Invalide credentials"})
