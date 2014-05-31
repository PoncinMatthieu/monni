
import json
from bson import json_util
from flask import render_template, redirect, request, session, flash

from app import app
from login import requiresLogin
from model import Event

@app.route('/newservice', methods=["GET"])
def routeViewServicesGetNew():
	return render_template('form/service.html')

@app.route('/newservice', methods=["POST"])
def routeViewServicesPostNew():
	return render_template('form/service.html')

@app.route('/service/<sid>')
@requiresLogin
def routeViewServices(sid):
	eventServices = app.config['SERVICES']
	if sid not in eventServices:
		return 'This service doesn\'t exist', 404

	events = Event.FetchEventsFrom(sid)
	return render_template('service.html', events=events)

@app.route('/event/<eid>')
@requiresLogin
def routeViewServicesEvent(eid):
	e = Event.FetchEventWithId(eid)
	if e == None:
		return 'This event doesn\'t exist', 404
	e.datas_dump = json.dumps(e.datas, default=json_util.default)
	return render_template('event.html', event=e)

@app.route('/event/del/<eid>', methods=['GET'])
@requiresLogin
def routeViewServicesDeleteEvent(eid):
	e = Event()
	e.Delete(eid)
	return 'ok'
