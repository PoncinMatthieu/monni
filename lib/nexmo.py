
import requests

def send_sms(api_key, api_secret, phone_number, text):
	requests.post('https://rest.nexmo.com/sms/json', params={'api_key': api_key, 'api_secret': api_secret, 'from': 'Monni', 'to': phone_number, 'text': text})

def send_voice(api_key, api_secret, phone_number, text, repeat=1):
	requests.get('https://api.nexmo.com/tts/json', params={'api_key': api_key, 'api_secret': api_secret, 'to': phone_number, 'text': text, 'repeat': repeat, 'lg': 'en-gb'})
