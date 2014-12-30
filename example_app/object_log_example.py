import psutil
from ISStreamer.Streamer import Streamer


streamer = Streamer(bucket_name="test object logging", debug_level=2)

# Example dict
streamer.log_object({"foo": "1", "bar": "2"})

# Example lists
cpu_percents = psutil.cpu_percent(percpu=True)
streamer.log_object(cpu_percents, signal_prefix="cpu")
streamer.log_object(['1', '2', '3'])

# Example objects with attributes
streamer.log_object(psutil.virtual_memory())

streamer.close()