
import datetime
import json
from bson import json_util, ObjectId

from app import db

class ProfilerEvent():
	# display the data
	def __repr__(self):
		return json.dumps(self.datas,default=json_util.default)

	@staticmethod
	def FetchAll(findFilter = {}, projection = None, sortBy = None, distinctKey = None):
		events = []
		c = db.profilerEvents.find(findFilter, projection)
		if sortBy:
			c = c.sort(sortBy,-1)
		if distinctKey:
			return c.distinct(distinctKey)
		for e in c:
			events.append(ProfilerEvent.Clone(e))
		return events

	@staticmethod
	def FetchBySidAndType(sid, type, findFilter = None, projection = None, sortBy = None):
		if findFilter == None:
			findFilter = {}
		findFilter['sid'] = ObjectId(sid)
		findFilter['type'] = type
		return ProfilerEvent.FetchAll(findFilter, projection, sortBy)

	@staticmethod
	def FetchFromService(sid, findFilter = {}, projection = None, sortBy = None, distinctKey = None):
		if findFilter == None:
			findFilter = {}
		findFilter['sid'] = ObjectId(sid)
		return ProfilerEvent.FetchAll(findFilter, projection, sortBy, distinctKey)

	@staticmethod
	def Clone(data):
		if data == None:
			return None
		return ProfilerEvent(data['sid'], data['type'], data, data['_id'])

	def __init__(self, sid = None, type = None, datas = {}, id = None):
		if 'time' not in datas:
			datas['time'] = datetime.datetime.now()
		if 'sid' in datas:
			del datas['sid']
		if 'type' in datas:
			del datas['type']
		if '_id' in datas:
			del datas['_id']

		self.id = str(id)
		self.sid = str(sid)
		self.type = type
		self.datas = datas

	def Insert(self):
		data = self.datas
		data['sid'] = ObjectId(self.sid)
		data['type'] = self.type
		newId = None

		newId = db.profilerEvents.insert(data)
		if newId != None:
			self.id = str(newId)
			return self.id
		return None


	# update values of the event with the new one
	# updating average and max values
	def Update(self, newEvent):
		self.datas['time'] = newEvent.datas['time']
		if self.datas['max'] < newEvent.datas['max']:
			self.datas['max'] = newEvent.datas['max']
		self.datas['avg'] = ((self.datas['avg'] * self.datas['count']) + (newEvent.datas['avg'] * newEvent.datas['count'])) / (self.datas['count'] + newEvent.datas['count'])
		self.datas['count'] += newEvent.datas['count']
		db.profilerEvents.update({'_id': ObjectId(self.id)}, {'$set': self.datas})
