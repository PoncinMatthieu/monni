
from flask import render_template, redirect, request, session, flash

from app import app
from app.model import ResolvedEvent
from login import requiresLogin

@app.route('/resolvedEvents')
@requiresLogin
def routeViewResolvedEvents():
	events = ResolvedEvent.FetchAll()
	return render_template('resolvedEvents.html', header="home", sidebar="resolvedEvents", events=events)

@app.route('/resolvedEvents/delete/<eid>', methods=['GET', 'POST'])
@requiresLogin
def routeViewResolvedEventDelete(eid):
	e = ResolvedEvent.Fetch(eid)
	if e == None:
		flash('Resolved event doesn\'t exits.')
	else:
		e.Delete()
		flash('Resolved event deleted sucessfully.')
	return redirect(request.referrer)

