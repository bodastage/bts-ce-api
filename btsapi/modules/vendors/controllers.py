# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

	  # Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_vendors = Blueprint('vendors', __name__, url_prefix='/vendors')

# Set the route and accepted methods
@mod_vendors.route('/', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_vendors():
	pass