from ISStreamer.Streamer import Streamer

logger = Streamer("bucket_6",client_key="5mi1qMBxUDJOHpySP8q8HIE9qqooFHTY", debug=True)


def stress_test_loop(i):
	while i > 0:
		logger.log("stress_test", i)
		i = i - 1

stress_test_loop(10)

#logger.set_bucket("bucket_5_new")

#stress_test_loop(10)