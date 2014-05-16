#
# This is script exemple to send an event from python using the requests module
#

import requests

r = requests.post('http://devapi.ovelin.com:5223/api/event/plop', auth=('sid', 'key'), headers={'content-type': 'application/json'}, data='{"data":"mydata"}')
print(r.text)
