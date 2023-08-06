#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Antonio Martins (digiplan.pt@gmail.com)
#

# Check all requirements in README.md

import os
import socket
from datetime import datetime
import logging
import config

from __version__ import __version__
import hl7_v2x_receiver


###################################################################


# TODO: Create local git repository and upload project to github https://github.com
# TODO: Use HL7apy from http://crs4.github.io/hl7apy/index.html instead of python-hl7
# TODO: Use HL7apy to implement HL7 data types
# TODO: Use Requests toolbelt to crate the multipartEncoder https://toolbelt.readthedocs.io/en/latest/user.html
# TODO: Create a white list of allowed HL7 MLLP hostname clients
# TODO: Implement RPLC document and other types
# TODO: Change UNICODE converting lxml and xml_declaration = True


###################################################################


# Logging facility
logger = logging.getLogger(config.APP_NAME)


###################################################################
## Class Oru2xds
###################################################################


class Oru2xds:
	def __init__(self):
		# create logger
		self.config_logging()

		logger.info("Starting oru2xds %s ...", __version__)
		logger.info("Log location: %s", config.LOG_DIR_PATH)
		logger.debug("Logging level for the console is %s", config.LOG_LEVEL_CONSOLE)
		logger.debug("Logging level for the log file is %s", config.LOG_LEVEL_FILE)
		logger.info("Affinity Domain Assigning Authority OID: %s", config.AFFINITY_DOMAIN_ASSIGNING_AUTHORITY_OID)

		# TODO: For example, if we received an argument with a file containing a
		# sample message, we could write a method that could handle it,
		# instead of spawning an HL7 MLLP service
		# Build an HL7 message
		# logger.info("Building HL7 message")
		# hl7message = hl7_receiver_4.build_hl7_message()
		# proxy2xds(hl7message)

		self.showhostname()
		# Start a network server
		myHL7receiver = hl7_v2x_receiver.Hl7v2x()
		myHL7receiver.start_service()

	#
	## Logging configuration
	#
	def config_logging(self):

		# Setting the log directory to be relative to the package dir
		path = os.path.abspath(__file__)
		config.LOG_DIR_PATH = os.path.dirname(path) + "/log"

		# Start logging
		if not os.path.exists(config.LOG_DIR_PATH) : os.makedirs(config.LOG_DIR_PATH)

		# Levels may be DEBUG, INFO, WARNING, ERROR, CRITICAL
		logger.setLevel(logging.DEBUG)

		# Console logging
		consoleHandler = logging.StreamHandler()
		if config.LOG_LEVEL_CONSOLE == "DEBUG":
			consoleHandler.setLevel(logging.DEBUG)
		elif config.LOG_LEVEL_CONSOLE == "INFO":
			consoleHandler.setLevel(logging.INFO)
		elif config.LOG_LEVEL_CONSOLE == "WARNING":
			consoleHandler.setLevel(logging.WARNING)
		elif config.LOG_LEVEL_CONSOLE == "ERROR":
			consoleHandler.setLevel(logging.ERROR)
		elif config.LOG_LEVEL_CONSOLE == "CRITICAL":
			consoleHandler.setLevel(logging.CRITICAL)
		else:
			raise ValueError('Invalid log level: %s', config.LOG_LEVEL_CONSOLE)
		formatter = logging.Formatter('%(message)s')
		consoleHandler.setFormatter(formatter)
		logger.addHandler(consoleHandler)

		# File logging
		dateStr = datetime.now().date().strftime("%Y%m%d")
		fileHandler = logging.FileHandler(config.LOG_DIR_PATH + '/oru2xds-{}.log'.format(dateStr))
		if config.LOG_LEVEL_FILE == "DEBUG":
			fileHandler.setLevel(logging.DEBUG)
		elif config.LOG_LEVEL_FILE == "INFO":
			fileHandler.setLevel(logging.INFO)
		elif config.LOG_LEVEL_FILE == "WARNING":
			fileHandler.setLevel(logging.WARNING)
		elif config.LOG_LEVEL_FILE == "ERROR":
			fileHandler.setLevel(logging.ERROR)
		elif config.LOG_LEVEL_FILE == "CRITICAL":
			consoleHandler.setLevel(logging.CRITICAL)
		else:
			raise ValueError('Invalid log level: %s', config.LOG_LEVEL_FILE)
		formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s')
		fileHandler.setFormatter(formatter)
		logger.addHandler(fileHandler)


	#
	## Display the hostname and IP address
	#
	def showhostname(self):
		try: 
			host_name = socket.gethostname()
			host_ip = socket.gethostbyname(host_name)
			logger.info("Hostname: %s (%s)", host_name, host_ip)
		except: 
			logger.error("Unable to get Hostname and IP") 
			raise


def main():
	print("This is oru2xds version " + __version__)


if __name__ == "__main__":
	Oru2xds()

