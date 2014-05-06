
from functools import wraps
from flask import render_template, redirect, request, session, flash, url_for

from app import app
from db.model import Event

# Authentication
def requiresLogin(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		if 'logged_in' not in session or not session['logged_in']:
			return redirect(url_for('login'))
		return f(*args, **kwargs)
	return decorated

@app.route('/')
def index():
	services = app.config['SERVICES']
	return render_template('index.html', services=services)

@app.route('/service/<sid>')
@requiresLogin
def services(sid):
	services = app.config['SERVICES']
	if sid not in services:
		return 'This service doesn\'t exist', 404

	events = Event.FetchEventsFrom(sid)
	return render_template('service.html', events=events)

@app.route('/event/<eid>')
@requiresLogin
def event(eid):
	e = Event.FetchEventWithId(eid)
	if e == None:
		return 'This event doesn\'t exist', 404
	return render_template('event.html', event=e)

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME'] or request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid username or password'
		else:
			session['logged_in'] = True
			flash('You are logged in')
			return redirect(url_for('index'))
	return render_template('login.html', error=error)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('login'))

@app.route('/event/del/<eid>', methods=['GET'])
@requiresLogin
def deleteEvent(eid):
	e = Event()
	e.Delete(eid)
	return 'ok'
