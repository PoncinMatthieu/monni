
import json
from bson import json_util, ObjectId

from app import db

class ResolvedEvent():
	# display the data
	def __repr__(self):
		return json.dumps(self.data,default=json_util.default)

	@staticmethod
	def FetchAll(findFilter = {}, projection = None):
		events = []
		for e in db.resolvedEvents.find(findFilter, projection).sort('time',-1):
			events.append(ResolvedEvent.Clone(e))
		return events

	@staticmethod
	def FetchFromService(sid, findFilter = {}, projection = None):
		if findFilter == None:
			findFilter = {}
		findFilter['sid'] = sid
		return ResolvedEvent.FetchAll(findFilter, projection)

	@staticmethod
	def Fetch(reid, projection = None):
		return ResolvedEvent.Clone(db.resolvedEvents.find_one({'_id': ObjectId(reid)}, projection))

	@staticmethod
	def Clone(data):
		if data == None:
			return None
		return ResolvedEvent(data['sid'], data['type'], data, data['_id'])

	def __init__(self, sid = None, type = None, datas = {}, id = None):
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
		newId = db.resolvedEvents.insert(data)
		if newId != None:
			self.id = str(newId)
			return self.id
		return None

	def ArchiveEvents(self):
		data = self.datas
		data['sid'] = ObjectId(self.sid)
		data['type'] = self.type
		for e in Event.FetchAll(data):
			e.Archive()

