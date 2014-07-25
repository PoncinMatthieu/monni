
from flask import render_template, redirect, request, session, flash

from app import app

@app.route('/settings')
def routeViewSettings():
	return render_template('settings.html', header="settings", sidebar="")

