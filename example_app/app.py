from ISStreamer.Streamer import Streamer
logger = Streamer("example_offline", debug_level=2, offline=True)

def stress_test_loop(i, num):
	while i > 0:
		logger.log("iterations_left_{n}".format(n=num), i)
		i = i - 1


stress_test_loop(22, 1)

logger.close()