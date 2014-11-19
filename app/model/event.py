
import datetime
import json
from bson import json_util, ObjectId

from app import db

class Event():
	# display the data
	def __repr__(self):
		return json.dumps(self.datas,default=json_util.default)

	@staticmethod
	def FetchTypes():
		return db.events.aggregate([{'$group': {_id: "$type"}}])

	@staticmethod
	def FetchAll(findFilter = {}, projection = None, sortBy = None, distinctKey = None):
		events = []
		c = db.events.find(findFilter, projection)
		if sortBy:
			c = c.sort(sortBy,-1)
		if distinctKey:
			return c.distinct(distinctKey)
		for e in c:
			events.append(Event.Clone(e))
		return events

	@staticmethod
	def FetchFromService(sid, findFilter = {}, projection = None, sortBy = None, distinctKey = None):
		if findFilter == None:
			findFilter = {}
		findFilter['sid'] = ObjectId(sid)
		return Event.FetchAll(findFilter, projection, sortBy, distinctKey)

	@staticmethod
	def FetchOfType(type, projection = None):
		return Event.FetchAll({'type': type}, projection)

	@staticmethod
	def Fetch(eid, findFilter = {}, projection = None):
		if findFilter == None:
			findFilter = {}
		findFilter['_id'] = ObjectId(eid)
		return Event.Clone(db.events.find_one({'_id': ObjectId(eid)}, projection))

	@staticmethod
	def DeleteAllFromService(sid):
		db.events.remove({'sid': ObjectId(sid)})

	@staticmethod
	def Clone(data):
		if data == None:
			return None
		return Event(data['sid'], data['type'], data, data['_id'])

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

	def Insert(self, collectionName = 'events'):
		data = self.datas
		data['sid'] = ObjectId(self.sid)
		data['type'] = self.type
		newId = None
		if collectionName == 'events':
			newId = db.events.insert(data)
		elif collectionName == 'archivedEvents':
			newId = db.archivedEvents.insert(data)
		if newId != None:
			self.id = str(newId)
			return self.id
		return None

	def Update(self, id = None):
		if id == None:
			id = self.id

		data = self.datas
		data['sid'] = ObjectId(self.sid)
		data['type'] = self.type
		db.events.update({'_id': ObjectId(id)}, {'$set': data})

	def Delete(self, id = None):
		if id == None:
			id = self.id
		db.events.remove({'_id': ObjectId(id)})

	def Archive(self):
		id = self.id
		self.Insert('archivedEvents')
		self.Delete(id)
