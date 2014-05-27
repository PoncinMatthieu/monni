
from functools import wraps
from flask import Flask, request, session, g, redirect, url_for,abort, render_template, flash, Markup

from config import globals
import db

# Create app
print("Initializing server...")
app = Flask(__name__)
app.config.from_pyfile(globals.PROJECT_DIR + '/config/default.cfg')

# Get access to databases replica set.
# in case we have no replica set (preferably only for dev environment) we use a normal connection.
print("Creating 'db' replica set connection with read pref PRIMARY_PREFERRED")
dbConnection = db.Connection()
dbConnection.connect(app.config['DB_HOST'], app.config['DB_REPLICA_SET'])
print("Using db '" + app.config['DB_NAME'] + "'")
db = dbConnection.getDatabase(app.config['DB_NAME'])

# Requests
#@app.before_request
#def beforeRequest():
#	print("before request")

@app.after_request
def afterRequest(response):
	# TODO: Crossdomain access headers should be added for dev but not for production.
	# Remove comments below to enable crossdomain access.

	response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin'))
	response.headers.add('Access-Control-Allow-Methods', 'GET, POST')
	response.headers.add('Access-Control-Allow-Headers', 'X-Requested-With, Origin, Accept, Content-Type, Authorization, Compression, Remember')
	response.headers.add('Access-Control-Allow-Credentials',  'true')
	response.headers.add('Cache-Control', 'no-cache')
	response.headers.add('Expires', '-1')
	return response

# Exceptions
@app.errorhandler(Exception)
def handleDefaultExceptions(error):
	import traceback
	trace = traceback.format_exc()
	print('Exception occured while processing request: ' + request.path + '\n' + trace)

	# return 500
	response = jsonify({})
	response.status_code = 500;
	return response

# Import whole application
import main
import api
import serviceStatusChecker

print("Server initialized")
