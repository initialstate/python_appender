from ISStreamer.SingletonStreamer import Streamer

def stress_test_loop(i, num):
	logger = Streamer("single_new_{n}".format(n=num),client_key="2wO7oCojtm2eBnZEGXehC6fC1QCepbhd", debug_level=2)
	while i > 0:
		logger.log("iterations_left_{n}".format(n=num), i)
		i = i - 1


stress_test_loop(100, 1)
stress_test_loop(100, 2)


logger = Streamer("blahblah")
logger.log("blahblah", 1)
logger.close()