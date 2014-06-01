
from lib import mails
import sys
import requests
import json
from bson import json_util, ObjectId

from app import app, db

class Service():
	EVENT_API_STRING = 'eventApi'
	STATUS_CHECK_STRING = 'status'

	# display the data
	def __repr__(self):
		return json.dumps(self.data,default=json_util.default)

	@staticmethod
	def FetchAll(projection = None):
		services = []
		for s in db.services.find({}, projection):
			services.append(Service.Clone(s))
		return services

	@staticmethod
	def Fetch(sid, projection = None):
		return Service.Clone(db.services.find_one({'_id': ObjectId(sid)}, projection))

	@staticmethod
	def Clone(data):
		if data == None:
			return None
		return Service(data, data['_id'])

	def __init__(self, data, id = None):
		if '_id' in data:
			del data['_id']
		self.data = data
		self.id = id
		self.status = 0

	def Insert(self):
		return db.services.insert(self.data)

	def Update(self, id = None):
		if id == None:
			id = self.id
		data = self.data
		db.services.update({'_id': ObjectId(id)}, {'$set': data})

	def Delete(self, id = None):
		if id == None:
			id = self.id
		db.services.remove({'_id': ObjectId(id)})

	# return true if the service is checkable
	def IsStatusCheckable(self):
		return Service.STATUS_CHECK_STRING in self.data
	# return true if the service status type is equal to the one given
	def StatusCheckIs(self, t):
		return self.IsStatusCheckable() and self.data[Service.STATUS_CHECK_STRING]['type'] == t

	# perform http request
	def Request(self):
		if Service.STATUS_CHECK_STRING not in self.data or 'method' not in self.data[Service.STATUS_CHECK_STRING] or 'url' not in self.data[Service.STATUS_CHECK_STRING]:
			print("Service: Can't check service status, the request check is not setup properly.")

		statusChecks = self.data[Service.STATUS_CHECK_STRING]
		kwargs = {}
		if 'auth' in statusChecks and 'login' in statusChecks['auth'] and 'pass' in statusChecks['auth']:
			kwargs['auth'] = (statusChecks['auth']['login'], statusChecks['auth']['pass'])
		if 'headers' in statusChecks:
			kwargs['headers'] = statusChecks['headers']
		if 'data' in statusChecks:
			kwargs['data'] = statusChecks['data']
		if 'params' in statusChecks:
			kwargs['params'] = statusChecks['params']
		if 'verify' in statusChecks:
			kwargs['verify'] = statusChecks['verify']

		return requests.request(statusChecks['method'], statusChecks['url'], **kwargs)

	def CheckStatus(self):
		status = 0
		resultMessage = ''
		try:
			if self.data[Service.STATUS_CHECK_STRING]['type'] == 'HTTP':
				r = self.Request()
				if r != None:
					status = r.status_code
					if status != 200:
						resultMessage = r.text
			else:
				print('Service: Unknown service type. Failed to check service status.')
		except Exception as e:
			print('Service: Unknown error, failed to check service status.')
			print(e)
			resultMessage = str(e)

		self.status = status
		if self.status != 200:
			obj = 'Service ' + self.data['name'] + ' is down'
			message = 'Status check failed with status code: ' + str(self.status) + "\nmessage:\n" + resultMessage
			print(obj + ' ' + message)
			smtp = mails.InitSmtp(app.config['SMTP_HOST'], app.config['SMTP_USER'], app.config['SMTP_PASS'])
			mails.SendMail(smtp, app.config['ALERT_MAIL_FROM'], app.config['ALERT_MAIL_TO'], obj, message)

