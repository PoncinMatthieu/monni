
import json
from functools import wraps
from flask import render_template, redirect, request, session, flash, url_for
from bson import json_util, ObjectId

from app import app
from db.model import Service
from db.model import Event
from app.serviceStatusChecker import services

# Authentication
def requiresLogin(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		if 'logged_in' not in session or not session['logged_in']:
			return redirect(url_for('routeLogin'))
		return f(*args, **kwargs)
	return decorated

@app.route('/')
def routeIndex():
	eventServices = app.config['SERVICES']
	return render_template('index.html', services=services, eventServices=eventServices)

@app.route('/service/<sid>')
@requiresLogin
def routeServices(sid):
	eventServices = app.config['SERVICES']
	if sid not in eventServices:
		return 'This service doesn\'t exist', 404

	events = Event.FetchEventsFrom(sid)
	return render_template('service.html', events=events)

@app.route('/event/<eid>')
@requiresLogin
def routeEvent(eid):
	e = Event.FetchEventWithId(eid)
	if e == None:
		return 'This event doesn\'t exist', 404
	e.datas_dump = json.dumps(e.datas, default=json_util.default)
	return render_template('event.html', event=e)

@app.route('/login', methods=['GET', 'POST'])
def routeLogin():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME'] or request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid username or password'
		else:
			session['logged_in'] = True
			flash('You are logged in')
			return redirect(url_for('routeIndex'))
	return render_template('login.html', error=error)

@app.route('/logout', methods=['GET', 'POST'])
def routeLogout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('routeLogin'))

@app.route('/event/del/<eid>', methods=['GET'])
@requiresLogin
def routeDeleteEvent(eid):
	e = Event()
	e.Delete(eid)
	return 'ok'
