
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
	def Exists(findFilter):
		return (db.currentAlerts.find_one(findFilter) != None)

	@staticmethod
	def Fetch(findFilter, projection = None):
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

	def Create(self):
		self.datas['createdTime'] = datetime.datetime.now()
		self.datas['raised'] = False
		self.id = str(db.currentAlerts.insert(self.datas))

	# Raise an existing alert
	# Send mails and sms using the alert datas: 'mail-raised-object' 'mail-raised-data'
	def Raise(self):
		self.datas['raisedTime'] = datetime.datetime.now()
		self.datas['raised'] = True
		db.currentAlerts.update({'_id': ObjectId(self.id)}, self.datas)
		extraData = "\n\nAlert Id: " + self.id
		extraData += "\nRaised at: " + str(self.datas['raisedTime'])

		print(self.datas['mail-raised-object'] + ' ' + self.datas['mail-raised-data'])
		smtp = mails.InitSmtp(app.config['SMTP_HOST'], app.config['SMTP_USER'], app.config['SMTP_PASS'])
		mails.Send(smtp, app.config['ALERT_MAIL_FROM'], app.config['ALERT_MAIL_TO'], self.datas['mail-raised-object'], self.datas['mail-raised-data'] + extraData)
		if 'ALERT_SMS_NEXMO_KEY' in app.config and 'ALERT_SMS_NEXMO_SECRET' in app.config:
			for to in app.config['ALERT_SMS_TO']:
				requests.post('https://rest.nexmo.com/sms/json', params={'api_key': app.config['ALERT_SMS_NEXMO_KEY'], 'api_secret': app.config['ALERT_SMS_NEXMO_SECRET'], 'from': 'Monni', 'to': to, 'text': self.datas['mail-raised-object']})

	# close the current alert and insert it in the closed alerts collection.
	# Send mails and sms to inform the alert was closed if it was previously raised using datas: 'mail-closed-object' 'mail-closed-data'
	# return the id of this closed alert.
	def Close(self):
		newAlert = Alert(self.datas)
		db.currentAlerts.remove({'_id': ObjectId(self.id)})

		if self.datas['raised']:
			raisedTime = self.datas['raisedTime']
			alertTime = datetime.datetime.now() - raisedTime
			mailContent = self.datas['mail-closed-data']
			mailContent += "\n\nAlert Id: " + str(self.id)
			mailContent += "\nDowntime: " + str(alertTime)
			mailContent += "\nError was:\n" + self.datas['mail-raised-data']

			print(self.datas['mail-closed-object'] + ' ' + self.datas['mail-closed-data'])
			smtp = mails.InitSmtp(app.config['SMTP_HOST'], app.config['SMTP_USER'], app.config['SMTP_PASS'])
			mails.Send(smtp, app.config['ALERT_MAIL_FROM'], app.config['ALERT_MAIL_TO'], self.datas['mail-closed-object'], mailContent)
			if 'ALERT_SMS_NEXMO_KEY' in app.config and 'ALERT_SMS_NEXMO_SECRET' in app.config:
				for to in app.config['ALERT_SMS_TO']:
					requests.post('https://rest.nexmo.com/sms/json', params={'api_key': app.config['ALERT_SMS_NEXMO_KEY'], 'api_secret': app.config['ALERT_SMS_NEXMO_SECRET'], 'from': 'Monni', 'to': to, 'text': self.datas['mail-closed-object']})
		return db.closedAlerts.insert(newAlert.datas)
