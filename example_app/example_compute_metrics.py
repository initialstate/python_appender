import psutil
import time
from ISStreamer.Streamer import Streamer
streamer = Streamer(bucket="Perf 10ms sampling; buffer 20; object logging; python2", buffer_size=20)

sample_rate_in_ms=10

for x in range(100):

	streamer.log("sample", x)
	# Get total CPU usage
	cpu_percent = psutil.cpu_percent()
	streamer.log("cpu_total", cpu_percent)

	# Get individual CPU usage
	cpu_percents = psutil.cpu_percent(percpu=True)
	streamer.log_object(cpu_percents, signal_prefix="cpu")
	
	# Get the virtual memory usage
	memory = psutil.virtual_memory()
	streamer.log_object(memory, signal_prefix="virtual_mem")
	
	# Get the swap memory usage
	swap = psutil.swap_memory()
	streamer.log_object(swap, signal_prefix="swap_mem")

	# Get the network usage
	network = psutil.net_io_counters()
	streamer.log_object(network, signal_prefix="net_io")

	time.sleep(sample_rate_in_ms/1000)

streamer.close()