
import json
from bson import json_util, ObjectId

from lib import mails
from app import app, db

class Alert():
	# display the data
	def __repr__(self):
		return json.dumps(self.data,default=json_util.default)

	@staticmethod
	def WasRaised(findFilter):
		return (db.currentAlerts.find_one(findFilter) != None)

	@staticmethod
	def Fetch(aid, projection = None):
		return Alert.Clone(db.alerts.find_one({'_id': ObjectId(aid)}, projection))

	@staticmethod
	def FetchRaised(findFilter, projection = None):
		return Alert.Clone(db.currentAlerts.find_one(findFilter, projection))

	@staticmethod
	def Clone(data):
		if data == None:
			return None
		return Alert(data, data['_id'])

	def __init__(self, datas = {}, id = None):
		if '_id' in datas:
			del datas['_id']

		self.id = str(id)
		self.datas = datas

	# Raise a new alert, saving in the currentAlerts
	# Send a mail using the alert datas: 'mail-raised-object' 'mail-raised-data'
	def Raise(self):
		newId = db.currentAlerts.insert(self.datas)

		print(self.datas['mail-raised-object'] + ' ' + self.datas['mail-raised-data'])
		smtp = mails.InitSmtp(app.config['SMTP_HOST'], app.config['SMTP_USER'], app.config['SMTP_PASS'])
		mails.SendMail(smtp, app.config['ALERT_MAIL_FROM'], app.config['ALERT_MAIL_TO'], self.datas['mail-raised-object'], self.datas['mail-raised-data'])

		if newId != None:
			self.id = str(newId)
			return self.id
		return None

	# close the current alert and insert it in the closed alerts collection.
	# Send a mail to inform the alert was closed using datas: 'mail-closed-object' 'mail-closed-data'
	# return the id of this closed alert.
	def Close(self):
		newAlert = Alert(self.datas)
		db.currentAlerts.remove({'_id': ObjectId(self.id)})

		print(self.datas['mail-closed-object'] + ' ' + self.datas['mail-closed-data'])
		smtp = mails.InitSmtp(app.config['SMTP_HOST'], app.config['SMTP_USER'], app.config['SMTP_PASS'])
		mails.SendMail(smtp, app.config['ALERT_MAIL_FROM'], app.config['ALERT_MAIL_TO'], self.datas['mail-closed-object'], self.datas['mail-closed-data'])

		return db.closedAlerts.insert(newAlert.datas)
