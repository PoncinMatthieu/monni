
import json
import requests
import datetime
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
		datas['raisedTime'] = datetime.datetime.now()
		newId = db.currentAlerts.insert(self.datas)

		print(self.datas['mail-raised-object'] + ' ' + self.datas['mail-raised-data'])
		smtp = mails.InitSmtp(app.config['SMTP_HOST'], app.config['SMTP_USER'], app.config['SMTP_PASS'])
		mails.Send(smtp, app.config['ALERT_MAIL_FROM'], app.config['ALERT_MAIL_TO'], self.datas['mail-raised-object'], self.datas['mail-raised-data'])
		if 'ALERT_SMS_NEXMO_KEY' in app.config and 'ALERT_SMS_NEXMO_SECRET' in app.config:
			for to in app.config['ALERT_SMS_TO']:
				requests.post('https://rest.nexmo.com/sms/json', params={'api_key': app.config['ALERT_SMS_NEXMO_KEY'], 'api_secret': app.config['ALERT_SMS_NEXMO_SECRET'], 'from': 'Monni', 'to': to, 'text': self.datas['mail-raised-object']})

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

		raisedTime = self.datas['raisedTime']
		alertTime = datetime.datetime.now() - raisedTime
		mailContent = self.datas['mail-closed-data'] + "\n\nAlert closed after " + str(alertTime) + ".\n\nError was:\n" + self.datas['mail-raised-data']

		print(self.datas['mail-closed-object'] + ' ' + self.datas['mail-closed-data'])
		smtp = mails.InitSmtp(app.config['SMTP_HOST'], app.config['SMTP_USER'], app.config['SMTP_PASS'])
		mails.Send(smtp, app.config['ALERT_MAIL_FROM'], app.config['ALERT_MAIL_TO'], self.datas['mail-closed-object'], self.datas['mail-closed-data'])
		if 'ALERT_SMS_NEXMO_KEY' in app.config and 'ALERT_SMS_NEXMO_SECRET' in app.config:
			for to in app.config['ALERT_SMS_TO']:
				requests.post('https://rest.nexmo.com/sms/json', params={'api_key': app.config['ALERT_SMS_NEXMO_KEY'], 'api_secret': app.config['ALERT_SMS_NEXMO_SECRET'], 'from': 'Monni', 'to': to, 'text': self.datas['mail-closed-object']})
		return db.closedAlerts.insert(newAlert.datas)
