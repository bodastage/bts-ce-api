from btsapi import app
import urllib
from flask import url_for
from flask_script import Manager

app.config['SERVER_NAME'] = 'localhsot'
manager = Manager(app)

@manager.command
def show_routes():
    output = []
    for rule in app.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        #url = url_for(rule.endpoint, **options)
        line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, rule))
        output.append(line)

    for line in sorted(output):
        print(line)
		
if __name__ == "__main__":
    manager.run()