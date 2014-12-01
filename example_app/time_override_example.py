import time
from ISStreamer.Streamer import Streamer

# NOTE: the client_key is being provided by a local .ini file
streamer = Streamer(bucket="Time Override Example")

for x in range(100):

	# Get the current timestamp in epoch
	iteration_time = time.time()

	# log the iteration number and provide the previously calculated epoch
	streamer.log("iteration", x, epoch=iteration_time)

	# sleep for .5 seconds
	time.sleep(.5)

	# send another log with the overriden epoch
	streamer.log("message", "same time", epoch=iteration_time)

	# gaurentee the messages are flushed at the end of the loop
	streamer.flush()

	time.sleep(.5)

streamer.close()