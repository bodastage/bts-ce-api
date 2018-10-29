import os

# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

# Define the database - we are working with
SQLALCHEMY_DATABASE_URI = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
                                os.getenv("BTS_DB_USER", "bodastage"),
                                os.getenv("BTS_DB_PASS", "password"),
                                os.getenv("BTS_DB_HOST", "192.168.99.100"),
                                os.getenv("BTS_DB_PORT", "5432"),
                                os.getenv("BTS_DB_NAME", "bts"),
                            )

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