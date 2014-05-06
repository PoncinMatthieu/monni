
import pymongo
from pymongo import Connection as MongoConnection, MongoReplicaSetClient
from pymongo.read_preferences import ReadPreference

class Connection():
	def __init__(self):
		self.connection = None

	def connect(self,hosts="localhost", replicaSet="", readPreference=ReadPreference.SECONDARY_PREFERRED):
		# if the replicaset is empty, we use a normal connection, if not, we use a MongoReplicaSetClient
		# in wich case we set the read preference
		# by default, SECONDARY_PREFERRED since we don't big have consistancy issues. Fail safe when the primary/secondary goes down.
		if replicaSet == "":
			print("Using mongodb host " + hosts + " for read/writes.")
			self.connection = MongoConnection(hosts)
		else:
			print("Using mongodb hosts " + hosts + " with replica set " + replicaSet + " and read pref " + str(readPreference))
			self.connection = MongoReplicaSetClient(hosts, replicaSet=replicaSet, read_preference=readPreference)
			print("Replica set:")
			print("PRIMARY: " + str(self.connection.primary))
			print("SECONDARIES: " + str(self.connection.secondaries))
			print("ARBITERS: " + str(self.connection.arbiters))

	def close(self):
		self.connection.close()
		self.connection = None

	# \return the requested db setting the readPreference if set.
	def getDatabase(self, dbname, readPreference=None):
		db = self.connection[dbname]
		if readPreference != None:
			db.read_preference = readPreference
		return db

