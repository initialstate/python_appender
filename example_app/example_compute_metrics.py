import psutil
import time
from ISStreamer.Streamer import Streamer

# Provide a client_key from local ini file, override buffer and flush for optimal streaming
streamer = Streamer(bucket_name="Example Performance Metrics",bucket_key="compute_metrics", buffer_size=100, ini_file_location="./isstreamer.ini", debug_level=1)

sample_rate_in_ms=100

for x in range(1000):

	streamer.log("sample", x)
	# Get total CPU usage
	cpu_percent = psutil.cpu_percent()
	streamer.log("cpu_total", cpu_percent)

	# Get individual CPU usage
	cpu_percents = psutil.cpu_percent(percpu=True)
	streamer.log_object(cpu_percents, key_prefix="cpu")
	
	# Get the virtual memory usage
	memory = psutil.virtual_memory()
	streamer.log_object(memory, key_prefix="virtual_mem")
	
	# Get the swap memory usage
	swap = psutil.swap_memory()
	streamer.log_object(swap, key_prefix="swap_mem")

	# Get the network usage
	network = psutil.net_io_counters()
	streamer.log_object(network, key_prefix="net_io")

	# flush the stream to ensure optimal buffer and consumption experience
	streamer.flush()

	# sleep before sampling again
	time.sleep(sample_rate_in_ms/1000)

# cleanup the stream and ensure logs are flushed
streamer.close()