from initialstate_log_streamer import LogStreamer

logger = LogStreamer("example_python_app", "lfYvGA5YuK0whixHCxzvHjNJdWlMovjO")

logger.log("signal_test", 1)
logger.log("signal_test", 2)
logger.log("signal_test", 3)
logger.log("signal_test", 4)
