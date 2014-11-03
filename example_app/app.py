from ISStreamer.Streamer import Streamer
import time

logger = Streamer("buffer_bucket_1",client_key="2wO7oCojtm2eBnZEGXehC6fC1QCepbhd", debug_level=2)


def stress_test_loop(i):
	while i > 0:
		time.sleep(.01)
		logger.log("stress_test", i)
		i = i - 1

stress_test_loop(7)

logger.close()
