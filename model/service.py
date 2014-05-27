
from lib import mails
import sys
import requests
import json
from bson import json_util, ObjectId

from app import app, db

class Service():
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
	def FetchWithId(sid, projection = None):
		return Service.Clone(db.services.find_one({'_id': ObjectId(sid)}, projection))

	@staticmethod
	def Clone(data):
		if data == None:
			return None
		return Service(data)

	def __init__(self, data):
		self.data = data
		self.status = 0

	def Insert(self):
		return db.services.insert(self.data)

	# perform http request
	def Request(self):
		kwargs = {}
		if 'auth' in self.data and 'login' in self.data['auth'] and 'pass' in self.data['auth']:
			kwargs['auth'] = (self.data['auth']['login'], self.data['auth']['pass'])
		if 'headers' in self.data:
			kwargs['headers'] = self.data['headers']
		if 'data' in self.data:
			kwargs['data'] = self.data['data']
		if 'params' in self.data:
			kwargs['params'] = self.data['params']
		if 'verify' in self.data:
			kwargs['verify'] = self.data['verify']

		return requests.request(self.data['method'], self.data['url'], **kwargs)

	def CheckStatus(self):
		self.status = 0
		resultMessage = ''
		try:
			if self.data['type'] == 'HTTP':
				r = self.Request()
				if r != None:
					self.status = r.status_code
					if self.status != 200:
						resultMessage = r.text
			else:
				print('Service: Unknown service type. Failed to check service status.')
		except Exception as e:
			print('Service: Unknown error, failed to check service status.')
			print(e)
			resultMessage = str(e)

		if self.status != 200:
			obj = 'Service ' + self.data['name'] + ' is down'
			message = 'Status check failed with status code: ' + str(self.status) + "\nmessage:\n" + resultMessage
			print(obj + ' ' + message)
			smtp = mails.InitSmtp(app.config['SMTP_HOST'], app.config['SMTP_USER'], app.config['SMTP_PASS'])
			mails.SendMail(smtp, app.config['ALERT_MAIL_FROM'], app.config['ALERT_MAIL_TO'], obj, message)

