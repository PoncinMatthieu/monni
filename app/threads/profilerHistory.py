# This file handle threads that will save profiler events to another collection.

import threading
import atexit
import requests
from functools import wraps
from flask import session, url_for, request, Response
from bson import json_util

from app import app
from app.model import Service

profilerLock = threading.Lock()
profilerThread = None
profilerThreadInterval = 60

def CheckServiceStatus():
	service.CheckStatus()
	InitThread()

def TerminateThread():
	print("Terminating profiler history thread.")
	if profilerThread:
		profilerThread.cancel()

def InitThread():
	print("Init profiler history thread.")
	global profilerThread
	profilerThread = threading.Timer(profilerThreadInterval, CheckServiceStatus, [])
	profilerThread.start()

# init threads!
InitThread()
atexit.register(TerminateThread)
