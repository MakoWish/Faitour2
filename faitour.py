#!/usr/bin/python3

import os
import time
import utils.config as config
import handlers.intercept as intercept
from update import check as update_available
from utils.emulators import ServiceEmulators
from utils.logger import logger


#===============================================================================
# Main function to start Faitour
#===============================================================================
def main():
	# Ensure we are running as root/sudo
	if os.geteuid() != 0:
		logger.critical('"type":["start","error"],"kind":"event","category":["process"],"dataset":"faitour.application","action":"start","reason":"Application must be run as root/sudo","outcome":"failure"')
		os._exit(5)

	# Ensure our configuration looks okay
	if not config.is_valid():
		logger.critical('"type":["error"],"kind":"event","category":["configuration"],"dataset":"faitour.application","action":"check_config","reason":"Default configuration found","outcome":"failure"')
		return False

	# Check if there are any updates available
	if update_available(silent=True):
		logger.info('"type":["info"],"kind":"event","category":["process"],"dataset":"faitour.application","action":"reason","reason":"An update is available. Please run \'update.py\' to apply these updates.","outcome":"unknown"')

	# Note that the application is starting
	logger.info('"type":["start","info"],"kind":"event","category":["process"],"dataset":"faitour.application","action":"reason","reason":"Faitour is starting","outcome":"unknown"')

	# Start any emulators that are enabled
	emulators = ServiceEmulators()
	emulators.start()

	# Get our configured maximum NFQUEUE size
	max_queue_size = config.get_value("network.max_queue_size")

	# Start intercepting packets
	intercept.start(max_queue_size)


#===============================================================================
# Application entry point
#===============================================================================
if __name__ == "__main__":
	try:
		main()
	except Exception as e:
		logger.error(f'"type":["end"],"kind":"event","category":["process"],"dataset":"faitour.application","action":"end","reason":"{e}","outcome":"failure"')
	finally:
		time.sleep(2) # Pause just to give things time to fully shut down in case of a service restart
		logger.info('"type":["end","info"],"kind":"event","category":["process"],"dataset":"faitour.application","action":"end","reason":"Faitour has stopped","outcome":"success"')
		os._exit(0)
