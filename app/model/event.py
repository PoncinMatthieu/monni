
import datetime
import json
from bson import json_util, ObjectId

from app import db

class Event():
	# display the data
	def __repr__(self):
		return json.dumps(self.data,default=json_util.default)

	@staticmethod
	def FetchTypes():
		return db.events.aggregate([{'$group': {_id: "$type"}}])

	@staticmethod
	def FetchAll(projection = None):
		events = []
		for e in db.events.find({}, projection).sort('time',-1):
			events.append(Event.Clone(e))
		return events

	@staticmethod
	def FetchFromService(sid, findFilter = None, projection = None):
		events = []
		if findFilter == None:
			findFilter = {}
		findFilter['sid'] = sid
		for e in db.events.find(findFilter, projection).sort('time',-1):
			events.append(Event.Clone(e))
		return events

	@staticmethod
	def FetchOfType(type, projection = None):
		events = []
		for e in db.events.find({'type': type}, projection).sort('time',-1):
			events.append(Event.Clone(e))
		return events

	@staticmethod
	def Fetch(eid, projection = None):
		return Event.Clone(db.events.find_one({'_id': ObjectId(eid)}, projection))

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

		self.id = id
		self.sid = sid
		self.type = type
		self.datas = datas

	def Insert(self):
		data = self.datas
		data['sid'] = self.sid
		data['type'] = self.type
		return db.events.insert(data)

	def Update(self, id = None):
		if id == None:
			id = self.id

		data = self.datas
		data['sid'] = self.sid
		data['type'] = self.type
		db.events.update({'_id': ObjectId(id)}, {'$set': data})

	def Delete(self, id = None):
		if id == None:
			id = self.id
		db.events.remove({'_id': ObjectId(id)})
