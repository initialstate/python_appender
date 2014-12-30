from ISStreamer.Streamer import Streamer
streamer = Streamer(bucket_name="test", debug_level=2)

def stress_test_loop(i, num):
	while i > 0:
		streamer.log("iterations_left_{n}".format(n=num), i)
		i = i - 1


stress_test_loop(2, 1)

streamer.close()