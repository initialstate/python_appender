from ISStreamer.Streamer import Streamer
import time

logger = Streamer("same_name-onoff",client_key="2wO7oCojtm2eBnZEGXehC6fC1QCepbhd", debug_level=2)


def stress_test_loop(i):
	while i > 0:
		logger.log("stress_test", "ON")
		time.sleep(.5)
		logger.log("stress_test", "OFF")
		time.sleep(.5)
		logger.log("iterations_left", i)
		i = i - 1

stress_test_loop(100)

logger.close()
