# This file handle threads that will check the services status

import threading
import atexit
import requests
from functools import wraps
from flask import session, url_for, request, Response
from bson import json_util

from app import app
from app.model import Service

serviceLock = threading.Lock()
services = []

def CheckServiceStatus(service):
	service.CheckStatus()
	InitThread(service, 60)

def TerminateThreads():
	print("Terminating service status threads.")
	for s in services:
		if hasattr(s, 'statusThread'):
			s.statusThread.cancel()

def InitThread(service, interval):
	service.statusThread = threading.Timer(interval, CheckServiceStatus, [service])
	service.statusThread.start()

def InitServiceThreads():
	global services
	TerminateThreads()
	print("Init Service status threads.")
	del services[0:len(services)]
	for s in Service.FetchAll():
		services.append(s)
		if s.IsStatusCheckable():
			InitThread(s, 5)


# init threads!
InitServiceThreads()
atexit.register(TerminateThreads)
