from btsapi import create_app
from flask import Flask, render_template, request

app = create_app()
app.app_context().push()

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
        return '', 200, headers


# Import modules using the blueprint handlers variable (mod_vendors)
from btsapi.modules.vendors.controllers import mod_vendors as vendors_module
from btsapi.modules.users.controllers import mod_users as mod_users
from btsapi.modules.authentication.controllers import mod_auth as mod_auth
from btsapi.modules.networkbaseline.controllers import mod_networkbaseline as mod_networkbaseline
from btsapi.modules.technologies.controllers import mod_technologies as mod_technologies
from btsapi.modules.managedobjects.controllers import mod_managedobjects as mod_managedobjects
from btsapi.modules.networkmanagement.controllers import mod_netmgt as mod_netmgt
from btsapi.modules.settings.controllers import mod_settings as mod_settings

# Register blueprint(s)
app.register_blueprint(vendors_module)
app.register_blueprint(mod_users)
app.register_blueprint(mod_auth)
app.register_blueprint(mod_networkbaseline)
app.register_blueprint(mod_technologies)
app.register_blueprint(mod_managedobjects)
app.register_blueprint(mod_netmgt)
app.register_blueprint(mod_settings)

# TP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8181, debug=True)