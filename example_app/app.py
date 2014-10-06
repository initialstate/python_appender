from ISStreamer import Streamer

logger = Streamer.Streamer("example_python_app")

logger.log("signal_test", 1)
logger.log("signal_test", 2)
logger.log("signal_test", 3)
logger.log("signal_test", 4)
