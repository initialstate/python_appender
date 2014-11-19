import psutil
import time
from ISStreamer.Streamer import Streamer
streamer = Streamer(bucket="Perf 1ms sampling; buffer 20; epoch override", buffer_size=20)

sample_rate_in_ms=1

for x in range(100):
	cur_time = time.time()
	streamer.log("sample", x, epoch=time)
	cpu_percents = psutil.cpu_percent(percpu=True)

	i = 1
	for percent in cpu_percents:
		streamer.log("cpu_{}_percent".format(i), percent, epoch=time)
		i += 1

	memory = psutil.virtual_memory()
	streamer.log("virtual_memory_%", memory.percent, epoch=time)
	streamer.log("virtual_memory_total", memory.total, epoch=time)
	streamer.log("virtual_memory_avail", memory.available, epoch=time)
	streamer.log("virtual_memory_used", memory.used, epoch=time)
	streamer.log("virtual_memory_free", memory.free, epoch=time)
	streamer.log("virtual_memory_active", memory.active, epoch=time)
	streamer.log("virtual_memory_inactive", memory.inactive, epoch=time)
	streamer.log("virtual_memory_wired", memory.wired, epoch=time)

	time.sleep(sample_rate_in_ms/1000)

streamer.close()