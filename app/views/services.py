
import json, ast
from bson import json_util
from flask import render_template, redirect, request, session, flash, url_for

from app import app
from app.model import Event
from app.model import Service
from login import requiresLogin
from app.threads import serviceStatus

@app.route('/form/service', defaults={'sid': None}, methods=["GET"])
@app.route('/form/service/<sid>', methods=["GET"])
@requiresLogin
def routeViewServicesGetForm(sid):
	s = None
	if sid != None:
		s = Service.Fetch(sid)
	return render_template('form/service.html', layout="layout.html", service=s)

@app.route('/form/service', defaults={'sid': None}, methods=["POST"])
@app.route('/form/service/<sid>', methods=["POST"])
@requiresLogin
def routeViewServicesPostForm(sid):
	data = {'name': request.form['name']}

	if 'eventApiId' in request.form and 'eventApiKey' in request.form and len(request.form['eventApiId']) > 0 and len(request.form['eventApiKey']) > 0:
		data[Service.EVENT_API_STRING] = {'id': request.form['eventApiId'], 'key': request.form['eventApiKey']}

	if 'statusCheckHttpUrl' in request.form and len(request.form['statusCheckHttpUrl']) > 0:
		httpData = {'type': 'HTTP', 'url': request.form['statusCheckHttpUrl'], 'method': request.form['statusCheckHttpMethod']}
		if 'statusCheckHttpValidateCert' not in request.form or request.form['statusCheckHttpValidateCert'] != 'on':
			httpData['verify'] = False
		if 'statusCheckHttpBasicAuthLogin' in request.form and 'statusCheckHttpBasicAuthPass' in request.form and len(request.form['statusCheckHttpBasicAuthLogin']) > 0 and len(request.form['statusCheckHttpBasicAuthPass']) > 0:
			httpData['auth'] = {'login': request.form['statusCheckHttpBasicAuthLogin'], 'pass': request.form['statusCheckHttpBasicAuthPass']}
		headersLeft = True
		headers = {}
		i = 0
		while headersLeft:
			if 'statusCheckHttpHeaderKey'+str(i) in request.form and 'statusCheckHttpHeaderData'+str(i) in request.form and len(request.form['statusCheckHttpHeaderKey'+str(i)]) > 0 and len(request.form['statusCheckHttpHeaderData'+str(i)]) > 0:
				headers[request.form['statusCheckHttpHeaderKey'+str(i)]] = request.form['statusCheckHttpHeaderData'+str(i)]
			else:
				headersLeft = False
			i += 1
		httpData['headers'] = headers
		if 'statusCheckHttpData' in request.form and len(request.form['statusCheckHttpData']) > 0:
			httpData['data'] = request.form['statusCheckHttpData']
		data[Service.STATUS_CHECK_STRING] = httpData

	s = Service(data, sid)
	if sid == None:
		s.Insert()
		flash('New service created sucessfully.')
	else:
		s.Update()
		flash('Service updated sucessfully.')
	serviceStatus.InitServiceThreads()
	return redirect(url_for('routeViewIndex'))

@app.route('/del/service/<sid>')
@requiresLogin
def routeViewServicesDelete(sid):
	s = Service.Fetch(sid)
	if s != None:
		s.Delete()
		serviceStatus.InitServiceThreads()
		flash('Service deleted sucessfully.')
	return redirect(url_for('routeViewIndex'))

@app.route('/service/<sid>', methods=["GET", "POST"])
@requiresLogin
def routeViewServices(sid):
	s = Service.Fetch(sid)
	if s == None:
		flash('The requested service does not exist!')
		return redirect(url_for('routeViewIndex'))

	find = None
	group = None
	if request.method == "POST":
		if 'find' in request.form and len(request.form['find']) > 0:
			find = ast.literal_eval(request.form['find'])
		if 'group' in request.form and len(request.form['group']) > 0:
			group = request.form['group']

	events = Event.FetchFromService(s.id, findFilter=find)

	if group != None:
		newEvents = []
		for e in events:
			found = False
			for ne in newEvents:
				if group in e.datas and group in ne.datas and e.datas[group] == ne.datas[group]:
					found = True
					ne.datas['time'] += 1
					break
			if not found:
				e.datas['time'] = 1
				newEvents.append(e)
		events = newEvents

	return render_template('service.html', service=s, events=events, form=(request.form if request.method == "POST" else None ))

@app.route('/event/<eid>')
@requiresLogin
def routeViewServicesEvent(eid):
	e = Event.Fetch(eid)
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
