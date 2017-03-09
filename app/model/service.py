
from lib import mails
import sys
import requests
import json
import datetime
from bson import json_util, ObjectId

from app import app, db
from event import Event
from alert import Alert

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
	def FetchByEventAPI(id, key, projection = None):
		return Service.Clone(db.services.find_one({'eventApi': {'id': id, 'key': key}}, projection))

	@staticmethod
	def Clone(data):
		if data == None:
			return None
		return Service(data, data['_id'])

	def __init__(self, data, id = None):
		if '_id' in data:
			del data['_id']
		self.data = data
		self.id = str(id)
		self.status = 0

	def Insert(self):
		newId = db.services.insert(self.data)
		if newId != None:
			self.id = str(newId)
			return self.id
		return None

	def Update(self, id = None):
		if id == None:
			id = self.id
		data = self.data
		db.services.update({'_id': ObjectId(id)}, {'$set': data})

	def Delete(self, id = None):
		if id == None:
			id = self.id
		# before we delete a service, delete all related entities
		Event.DeleteAllFromService(id)
		# delete the service
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
		status, resultMessage = self.TryCheckStatus()

		# if status no good, create an alert
		if status != 200:
			self.status = status

			# check if an alert was already created, if not, create one
			if not Alert.Exists({'type': 'service', 'eid': self.id}):
				alert = Alert({
						'type': 'service',
						'eid': self.id,
						'mail-raised-object': 'Alert raised: Service ' + self.data['name'] + ' is down',
						'mail-raised-data': 'Status check failed with status code: ' + str(self.status) + "\nResult:\n" + resultMessage,
						'mail-closed-object': 'Alert closed: Service ' + self.data['name'] + ' is up',
						'mail-closed-data': 'The service is back online.'
						})
				alert.Create()
			else:
				# alert already exist, but was not raised?
				alert = Alert.Fetch({'type': 'service', 'eid': self.id, 'raised': False})
				if alert:
					# raise the alert only after given time, to avoid false positives.
					if (datetime.datetime.now() - alert.datas['createdTime']).seconds > app.config['ALERT_RAISE_AFTER']:
						alert.Raise()
		else:
			# check if an alert was already raised
			# if yes, close it
			alert = Alert.Fetch({'type': 'service', 'eid': self.id})
			if alert != None:
				alert.Close()
			self.status = status

	def TryCheckStatus(self):
		status = 0
		resultMessage = ''
		try:
			status_check_type = self.data[Service.STATUS_CHECK_STRING].get('type', None)
			if status_check_type == 'HTTP':
				r = self.Request()
				if r != None:
					status = r.status_code
					if status != 200:
						resultMessage = r.text
			elif status_check_type == 'Heartbeat':
				required_count = self.data[Service.STATUS_CHECK_STRING]['count'] #how many events...
				required_type = self.data[Service.STATUS_CHECK_STRING].get('event_type', 'Heartbeat') # of this type
				tag = self.data[Service.STATUS_CHECK_STRING].get('tag', None) # and possibly with the given tag in the message
				period = int(self.data[Service.STATUS_CHECK_STRING]['minutes']) #in how many minutes do we expect
				query = {'type': required_type, 
						'time': {'$gt': datetime.datetime.now() - datetime.timedelta(minutes=period)}}
				if tag:
					query['tags'] = tag
				count = Event.Count(self.id, query)
				resultMessage = 'Received %d heartbeats %s in last %d minutes' % (count, ("(with '%s')" % tag) if tag else "", period)
				print resultMessage
				status = 503 if count < required_count else 200
			else:
				print('Service: Unknown status check type. Failed to check service status.')
		except Exception as e:
			print('Service: Unknown error, failed to check service status.')
			print(e)
			resultMessage = str(e)
		return status, resultMessage
