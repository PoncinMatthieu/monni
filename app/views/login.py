
from functools import wraps
from flask import render_template, redirect, request, session, flash, url_for
from urllib import unquote_plus

from app import app

# Authentication
def requiresLogin(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		if 'logged_in' not in session or not session['logged_in']:
			return redirect(url_for('routeViewLogin', r=request.full_path))
		return f(*args, **kwargs)
	return decorated

@app.route('/login', methods=['GET', 'POST'])
def routeViewLogin():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME'] or request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid username or password'
		else:
			session['logged_in'] = True
			flash('You are logged in')
			r = request.form.get("r", url_for('routeViewIndex'))
			return redirect(r)
	r = request.args.get("r", "")
	return render_template('form/login.html', layout="layout.html", header="login", error=error, r=unquote_plus(r))

@app.route('/logout', methods=['GET', 'POST'])
def routeViewLogout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('routeViewLogin'))

