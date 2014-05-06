#!/usr/bin/python

if __name__ == "__main__":
	from app import app
	app.run(port=5223, debug=True)
else:
	from api import app as application # for beanstalk to start the app
