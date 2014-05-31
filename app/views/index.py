

from flask import render_template, redirect, request, session, flash

from app import app
from app.threads import services

@app.route('/')
def routeViewIndex():
	eventServices = app.config['SERVICES']
	return render_template('index.html', services=services, eventServices=eventServices)

