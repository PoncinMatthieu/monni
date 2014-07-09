

from flask import render_template, redirect, request, session, flash

from app import app
from app.threads import services

@app.route('/')
def routeViewIndex():
	return render_template('index.html', header="home", sidebar="services", services=services)

