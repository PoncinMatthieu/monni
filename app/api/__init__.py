
from functools import wraps
from flask import session, url_for, request, Response
from bson import json_util

from app import app
from app.model import Event, ResolvedEvent, Service, ProfilerEvent

# Authentication
def authenticate():
	return Response(
		'Could not verify your access level for that URL.\n'
		'You have to login with proper credentials', 403,
		{'WWW-Authenticate': 'Basic realm="Login Required"'})

def checkAuth(serviceName, serviceKey):
	s = Service.FetchByEventAPI(serviceName, serviceKey)
	if s != None:
		session['sid'] = s.id
		return 1
	return 0

def performRequestAuth():
	# Basic HTTP authentication
	auth = request.authorization
	if auth:
		return checkAuth(auth.username, auth.password)
	elif 'sid' not in session:
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

@app.route('/api/archive/resolvedEvents/<reid>', methods=['GET', 'POST'])
@requiresAuth
def routeApiArchiveResolvedEvent(reid):
	re = ResolvedEvent.Fetch(reid)
	if re == None:
		return 'This resolved event doesn\'t exist', 404
	re.ArchiveEvents()
	return 'ok'

@app.route('/api/profiler/<type>', methods=['POST'])
@requiresAuth
def routeApiNewProfilerEvent(type):
	data = json_util.loads(request.data)

	events = ProfilerEvent.FetchBySidAndType(session['sid'], type)
	for d in data['events']:
		data['events'][d]['event'] = d
		newEvent = ProfilerEvent(session['sid'], type, data['events'][d])
		found = False
		for e in events:
			if d == e.datas['event']:
				e.Update(newEvent)
				found = True
		if not found:
			events.append(newEvent)
			newEvent.Insert()
	return 'ok'

