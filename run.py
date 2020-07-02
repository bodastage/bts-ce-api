import argparse
from btsapi import app

parser = argparse.ArgumentParser(description='Run server')
parser.add_argument("-p","--port", help="Port", default=8888)
parser.add_argument("-s","--server", help="Host IP", default='0.0.0.0')

args = parser.parse_args()

port = args.port
server = args.server

if __name__ == '__main__':
    app.run(host=server, port=port, debug=True)