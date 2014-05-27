# This file handle threads that will check the services status

import threading
import atexit
import requests
from functools import wraps
from flask import session, url_for, request, Response
from bson import json_util

from app import app
from db.model import Service

serviceLock = threading.Lock()
services = []

def CheckServiceStatus(service):
	print("Checking status for: " + service.data['name'])
	service.CheckStatus()
	InitThread(service, 60)

def TerminateThreads():
	for s in services:
		s.statusThread.cancel()

def InitThread(service, interval):
	service.statusThread = threading.Timer(interval, CheckServiceStatus, [service])
	service.statusThread.start()

def InitServiceThreads():
	global services
	for s in Service.FetchAll():
		services.append(s)
		InitThread(s, 5)

	atexit.register(TerminateThreads)

# init threads!
InitServiceThreads()
