import os

# Initialize the database details
BTS_DB_HOST=os.environ['BTS_DB_HOST']
BTS_DB_NAME=os.environ['BTS_DB_NAME']
BTS_DB_USER=os.environ['BTS_DB_USER']
BTS_DB_PASS=os.environ['BTS_DB_PASS']
BTS_DB_PORT=os.environ['BTS_DB_PORT']

# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

# Define the database - we are working with
SQLALCHEMY_DATABASE_URI = 'postgresql://{2}:{3}@{0}:{4}/{1}'.\
    format(BTS_DB_HOST, BTS_DB_NAME, BTS_DB_USER, BTS_DB_PASS, BTS_DB_PORT)
DATABASE_CONNECT_OPTIONS = {}

# Disable migration creation
SQLALCHEMY_TRACK_MODIFICATIONS=False

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for
# signing the data. 
CSRF_SESSION_KEY = "secret"

# Secret key for signing cookies
SECRET_KEY = "secret"