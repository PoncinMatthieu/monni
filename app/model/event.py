
import datetime
import json
from bson import json_util, ObjectId

from app import app, db

DedicatedCollections = app.config.get('DEDICATED_COLLECTIONS', '').split(',')

cached_queries = []

class Event():
	# display the data
	def __repr__(self):
		return json.dumps(self.datas,default=json_util.default)

	@staticmethod
	def GetCollection(type=None, **kwargs):
		return "%s" % type.lower() if type in DedicatedCollections else 'events'
	
	@staticmethod
	def FetchTypes():
		event_types = db[Event.GetCollection()].aggregate([{'$group': {'_id': "$type"}}])
		return event_types + DedicatedCollections

	@staticmethod
	def FetchAll(findFilter = {}, projection = None, sortBy = None, skip = None, limit = None, distinctKey = None):
		events = []
		c = db[Event.GetCollection(**findFilter)].find(findFilter, projection)
		if sortBy:
			c = c.sort(sortBy,-1)
		if skip:
			c = c.skip(skip)
		if limit:
			c = c.limit(limit)
		if distinctKey:
			return c.distinct(distinctKey)
		for e in c:
			events.append(Event.Clone(e))
		return events

	@staticmethod
	def FetchAllAndCache(*args, **kwargs):
		for q in cached_queries:
			if q['args'] == args and q['kwargs'] == kwargs:
				return q['result']
		cache = {'args': args, 'kwargs': kwargs, 'result': Event.FetchAll(*args, **kwargs)}
		cached_queries.append(cache)
		return cache['result']

	@staticmethod
	def Count(sid, findFilter = {}):
		if findFilter == None:
			findFilter = {}
		findFilter['sid'] = ObjectId(sid)
		return db[Event.GetCollection(**findFilter)].find(findFilter).count()

	@staticmethod
	def FetchFromService(sid, findFilter = {}, projection = None, sortBy = None, skip = None, limit = None, distinctKey = None):
		if findFilter == None:
			findFilter = {}
		findFilter['sid'] = ObjectId(sid)
		return Event.FetchAll(findFilter, projection, sortBy, skip, limit, distinctKey)

	@staticmethod
	def FetchOfType(type, projection = None):
		return Event.FetchAll({'type': type}, projection)

	@staticmethod
	def Fetch(eid, findFilter = {}, projection = None):
		if findFilter == None:
			findFilter = {}
		findFilter['_id'] = ObjectId(eid)
		return Event.Clone(db[Event.GetCollection(**findFilter)].find_one({'_id': ObjectId(eid)}, projection))

	@staticmethod
	def DeleteAllFromService(sid):
		query = {'sid': ObjectId(sid)}
		db.events.remove(query)
		for collection in DedicatedCollections:
			db[Event.GetCollection(type=collection)].remove(query)

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

	def Insert(self, collectionName = None):
		data = self.datas
		data['sid'] = ObjectId(self.sid)
		data['type'] = self.type
		newId = None
		if collectionName:
			newId = db[collectionName].insert(data)
		else:
			newId = db[Event.GetCollection(type=self.type)].insert(data)
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
		db[Event.GetCollection(type=self.type)].update({'_id': ObjectId(id)}, {'$set': data})

	def Delete(self, id = None):
		if id == None:
			id = self.id
		db[Event.GetCollection(type=self.type)].remove({'_id': ObjectId(id)})

	def Archive(self):
		id = self.id
		self.Insert('archivedEvents')
		self.Delete(id)
