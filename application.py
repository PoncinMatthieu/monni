#!/usr/bin/python
#
# This file is used to run the application and all other related tools like unit-tests
#
# - Running the application locally without wsgi (start the app in debug mode):
#   $> ./application.py
#
# - Running unit tests:
#   $> ./application.py [--host hostname] --tests [test-suite] [test-name]
#
#

import sys, getopt

def printUsage():
	print('Usage:')
	print('./application [OPTION]\n')
	print('OPTIONS:')
	print('\t--port portNumber')
	print('\t--tests [test-suite] [test-name] [--host hostname]')

def wrongParams():
	print('Wrong parameters')
	printUsage()
	sys.exit(2)

def runTests(host, unitTestSuite, unitTestName):
	import tests

	tests.host = host
	testSuites = tests.loadTestSuites()

	if unitTestName != None and unitTestSuite == None:
		wrongParams()
	if unitTestSuite != None and unitTestName not in testSuites:
		wrongParams()

	if unitTestName != None:
		print('Running single test: ' + unitTestSuite + '.' + unitTestName)
		tests.runSingleTest(unitTestSuite, testSuites[unitTestSuite], unitTestName)
	elif unitTestSuite != None:
		print('Running test suite: ' + sys.argv[2])
		tests.runTestSuite(testSuites[unitTestSuite])
	else:
		for suite in testSuites:
			print('Running test suite: ' + suite)
			tests.runTestSuite(testSuites[suite])

def runApp(port):
	from app import app
	app.run(port=port, debug=True)

def getNumberOfParams(argv):
	nb = 0
	while nb < len(argv):
		if argv[nb].startswith('-'):
			return nb
		nb += 1
	return nb

def main(argv):
	port = 5223
	host = "localhost:5223"
	runUnitTests = False
	unitTestSuite = None
	unitTestName = None

	while len(argv) > 0:
		nbParams = getNumberOfParams(argv[1:])

		if nbParams >= 0 and nbParams < 3 and (argv[0] == "--tests" or argv[0] == "-t"):
			runUnitTests = True
			if nbParams >= 1:
				unitTestSuite = argv[1]
				if nbParams == 2:
					unitTestName = argv[2]
		elif nbParams == 1 and (argv[0] == "--port" or argv[0] == "-p"):
			port = int(argv[1])
		elif nbParams == 1 and (argv[0] == "--host" or argv[0] == "-h"):
			host = argv[1]
		else:
			wrongParams()

		argv = argv[nbParams+1:]


	if runUnitTests:
		runTests(host, unitTestSuite, unitTestName)
	else:
		runApp(port)


if __name__ == "__main__":
	main(sys.argv[1:])
else:
	from api import app as application # for wsgi to start the app
