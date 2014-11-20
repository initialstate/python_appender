import psutil
import time
from ISStreamer.Streamer import Streamer
streamer = Streamer(bucket="Perf 10ms sampling; buffer 20; epoch override", buffer_size=20)

sample_rate_in_ms=10

for x in range(100):
	cur_time = time.time()
	streamer.log("sample", x, epoch=cur_time)
	# Get total CPU usage
	cpu_percent = psutil.cpu_percent()
	streamer.log("cpu_total", cpu_percent, epoch=cur_time)
	
	# Get individual CPU usage
	cpu_percents = psutil.cpu_percent(percpu=True)
	streamer.log_object(cpu_percents, signal_prefix="cpu", epoch=cur_time)

	# Get the virtual memory usage
	memory = psutil.virtual_memory()
	streamer.log_object(memory, epoch=cur_time)
	
	# Get the swap memory usage
	swap = psutil.swap_memory()
	streamer.log_object(swap, epoch=cur_time)

	# Get the network usage
	network = psutil.net_io_counters()
	streamer.log_object(network, epoch=cur_time)

	time.sleep(sample_rate_in_ms/1000)

streamer.close()