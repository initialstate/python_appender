from ISStreamer.Streamer import Streamer
import time

streamer = Streamer(bucket_name="test", debug_level=3, ini_file_location="./isstreamer.ini", async=True)

def stress_test_loop(i, num):
	while i > 0:
		streamer.log("iterations_left_{n}".format(n=num), i)
		time.sleep(.1)
		streamer.flush()
		i = i - 1


stress_test_loop(5000, 1)

streamer.close()