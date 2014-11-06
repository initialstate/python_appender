from ISStreamer.Streamer import Streamer as streamer

class Streamer:
	instance = None
	def __init__(self, bucket, client_key="", debug_level=0):
		if Streamer.instance == None:
			Streamer.instance = streamer(bucket=bucket, client_key=client_key, debug_level=debug_level)

	def log(self, signal, value):
		Streamer.instance.log(signal, value)

	def close(self):
		Streamer.instance.close()