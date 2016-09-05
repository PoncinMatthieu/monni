
import datetime
import json
from bson import json_util, ObjectId

from app import app, db

cached_queries = []

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
	def FetchAllAndCache(*args, **kwargs):
		for q in cached_queries:
			if q['args'] == args and q['kwargs'] == kwargs:
				return q['result']
		cache = {'args': args, 'kwargs': kwargs, 'result': ProfilerEvent.FetchAll(*args, **kwargs)}
		cached_queries.append(cache)
		return cache['result']

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
	def FetchHistory(sid, type, period, fromDate, toDate):
		events = []
		print(str({'sid': ObjectId(sid), 'type': type, 'time': {'$gte': fromDate, '$lt': toDate}}))
		c = db.profilerEventsHistory.find({'sid': ObjectId(sid), 'type': type, 'time': {'$gte': fromDate, '$lt': toDate}}).sort('time',1)
		for e in c:
			events.append(ProfilerEvent.Clone(e))
		return events

	# this method creates the profiled events history by storing the current ones in a separated collection
	@staticmethod
	def StoreAndResetCurrentEvents():
		cursor = db.profilerEvents.find({}, {'_id': 0})
		if cursor:
			events = []
			for e in cursor:
				events.append(e)
			if len(events) > 0:
				db.profilerEventsHistory.insert(events)
			db.profilerEvents.remove(w=1)
			config = db.configs.find_one({'type': 'profiler'}, {'lastEventReset': 1, 'lastEventResetDue': 1})
			db.configs.update({'type': 'profiler'}, {'$set': {'lastEventResetDue': config['lastEventReset'] + datetime.timedelta(seconds=app.config['EVENT_PROFILER_MIN_HISTORY_INTERVAL']), 'lastEventReset': config['lastEventResetDue']}}, w=1)

	# this method check weather we need or not to save and reset profiler events
	@staticmethod
	def ResetingEventsRequired():
		now = datetime.datetime.now()
		config = db.configs.find_one({'type': 'profiler'}, {'lastEventResetDue': 1})
		if not config:
			db.configs.insert({'type': 'profiler', 'lastEventResetDue': now, 'lastEventReset': now}, w=1)
			return True
		return (now >= config['lastEventResetDue'])

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

		if 'min' in self.datas and 'min' in newEvent.datas:
			if self.datas['min'] > newEvent.datas['min']:
				self.datas['min'] = newEvent.datas['min']
		elif 'min' in newEvent.datas:
			self.datas['min'] = newEvent.datas['min']

		if 'max' in self.datas and 'max' in newEvent.datas:
			if self.datas['max'] < newEvent.datas['max']:
				self.datas['max'] = newEvent.datas['max']
		elif 'max' in newEvent.datas:
			self.datas['max'] = newEvent.datas['max']

		self.datas['avg'] = ((self.datas['avg'] * self.datas['count']) + (newEvent.datas['avg'] * newEvent.datas['count'])) / (self.datas['count'] + newEvent.datas['count'])
		self.datas['count'] += newEvent.datas['count']
		db.profilerEvents.update({'_id': ObjectId(self.id)}, {'$set': self.datas})
