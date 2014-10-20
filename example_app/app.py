from ISStreamer.Streamer import Streamer
import time

logger = Streamer("bucket_7",client_key="2wO7oCojtm2eBnZEGXehC6fC1QCepbhd", debug=True)


def stress_test_loop(i):
	while i > 0:
		time.sleep(.01)
		logger.log("stress_test", i)
		i = i - 1

stress_test_loop(100)

#logger.set_bucket("bucket_5_new")

#stress_test_loop(10)