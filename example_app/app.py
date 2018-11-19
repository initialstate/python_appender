from ISStreamer.Streamer import Streamer
import time, math

streamer = Streamer(bucket_key="479DAGGBW86T", debug_level=3, ini_file_location="./isstreamer.ini")

def stress_test_loop(i, num):
	while i > 0:
		d = {
			"iterations_left": i,
			"some other value": math.sqrt(i)
		}
		streamer.log_object(d, key_prefix="")
		time.sleep(.1)
		streamer.flush()
		i = i - 1


stress_test_loop(5000, 1)

streamer.close()