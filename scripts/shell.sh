#
# This is script exemple to send an event from shell script using curl
#

curl -X POST -H "Content-Type: application/json" -u "sid:key" --data '{"data": "mydata"}' http://devapi.ovelin.com:5223/api/event/test
