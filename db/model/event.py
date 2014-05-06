
import json
from bson import json_util, ObjectId

from app import db

class Event():
	# display the data
	def __repr__(self):
		return json.dumps(self.data,default=json_util.default)

	@staticmethod
	def FetchEventTypes():
		return db.events.aggregate([{'$group': {_id: "$type"}}])

	@staticmethod
	def FetchAllEvents(projection = None):
		events = []
		for e in db.events.find({}, projection).sort('date',-1):
			events.append(Event.Clone(e))
		return events

	@staticmethod
	def FetchEventsFrom(sid, projection = None):
		events = []
		for e in db.events.find({'sid': sid}, projection).sort('date',-1):
			events.append(Event.Clone(e))
		return events

	@staticmethod
	def FetchEventsOfType(type, projection = None):
		events = []
		for e in db.events.find({'type': type}, projection).sort('date',-1):
			events.append(Event.Clone(e))
		return events

	@staticmethod
	def FetchEventWithId(eid, projection = None):
		return Event.Clone(db.events.find_one({'_id': ObjectId(eid)}, projection))

	@staticmethod
	def Clone(data):
		if data == None:
			return None
		return Event(data['sid'], data['type'], data['date'], data['duration'], data['dataType'], data['data'], data['_id'])

	def __init__(self, sid = None, type = None, date = None, duration = None, dataType = None, data = None, id = None):
		self.id = id
		self.sid = sid
		self.type = type
		self.date = date
		self.duration = duration
		self.dataType = dataType
		self.data = data

	def Insert(self):
		db.events.insert({'sid': self.sid, 'type': self.type, 'date': self.date, 'duration': self.duration, 'dataType': self.dataType, 'data': self.data})

	def Update(self, id = None):
		if id == None:
			id = self.id
		db.events.update({'_id': ObjectId(id)}, {'$set': {'sid': self.sid, 'type': self.type, 'date': self.date, 'duration': self.duration, 'dataType': self.dataType, 'data': self.data}})

	def Delete(self, id = None):
		if id == None:
			id = self.id
		db.events.remove({'_id': ObjectId(id)})
