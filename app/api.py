
import datetime
from functools import wraps
from flask import session, url_for, request, Response

from app import app
from db.model import Event

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
def apiIndex():
	return 'Monni api is up and running.'

@app.route('/api/event/<type>', methods=['POST'])
@requiresAuth
def newEvent(type):
	date = request.json['date'] if 'date' in request.json else datetime.datetime.now()
	duration = request.json['duration'] if 'duration' in request.json else None
	dataType = request.json['dataType'] if 'dataType' in request.json else None
	data = request.json['data'] if 'data' in request.json else None
	e = Event(session['sid'], type, date, duration, dataType, data)
	e.Insert()
	return 'ok'

