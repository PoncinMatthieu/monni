
from functools import wraps
from flask import session, url_for, request, Response
from bson import json_util

from app import app
from model import Event

# Authentication
def authenticate():
	return Response(
		'Could not verify your access level for that URL.\n'
		'You have to login with proper credentials', 403,
		{'WWW-Authenticate': 'Basic realm="Login Required"'})

def checkAuth(serviceName, serviceKey):
	services = app.config['SERVICES']
	if serviceName in services and services[serviceName] == serviceKey:
		session['sid'] = serviceName
		return 1
	return 0

def performRequestAuth():
	# Basic HTTP authentication
	auth = request.authorization
	if auth:
		return checkAuth(auth.username, auth.password)
	elif 'sid' not in session:
		return 0
	elif session['sid'] not in app.config['SERVICES']:
		return 0
	else:
		return 1

def requiresAuth(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		if performRequestAuth() != 1:
			return authenticate()
		return f(*args, **kwargs)
	return decorated

@app.route('/api')
def routeApiIndex():
	return 'Monni api is up and running.'

@app.route('/api/auth')
@requiresAuth
def routeApiAuth():
	return 'Authentication successful'

@app.route('/api/event/<type>', methods=['POST'])
@requiresAuth
def routeApiNewEvent(type):
	# get json with json_util from bson module so that types matches with mongo types.
	e = Event(session['sid'], type, json_util.loads(request.data))
	e.Insert()
	return 'ok'

