# local config helper stuff
try:
	import ISStreamer.configutil as configutil
except ImportError:
	import configutil
try:
	import ISStreamer.version as version
except ImportError:
	import version
import uuid

# python 2 and 3 conversion support
import sys
if (sys.version_info < (2,7,0)):
	sys.stderr.write("You need at least python 2.7.0 to use the ISStreamer")
	exit(1)
elif (sys.version_info >= (3,0)):
	import http.client as httplib
else:
	import httplib
import json
# time stuff
import datetime
import time
# performance stuff
import threading
import collections
import csv

class Streamer:
	BucketName = ""
	AccessKey = ""
	Channel = ""
	BufferSize = 10
	StreamApiBase = ""
	LogQueue = None
	DebugLevel = 0
	BucketKey = ""
	IsClosed = True
	Offline = False
	Async = True
	LocalFile = None
	ApiVersion = '<=0.0.4'
	MissedEvents = None
	def __init__(self, bucket_name="", bucket_key="", access_key="", ini_file_location=None, debug_level=0, buffer_size=10, offline=None, use_async=True):
		config = configutil.getConfig(ini_file_location)
		if (offline != None):
			self.Offline = offline
		else:
			if (config["offline_mode"] == "false"):
				self.Offline = False
			else:
				self.Offline = True

		self.Async = use_async
		if (self.Offline):
			try:
				file_location = "{}.csv".format(config["offline_file"])
				self.LocalFileHandler = open(file_location, 'w')
				self.LocalFile = csv.writer(self.LocalFileHandler)
			except:
				print("There was an issue opening the file (nees more description)")

		if (config == None and bucket_name=="" and access_key == ""):
			raise Exception("config not found and arguments empty")

		if (bucket_name == ""):
			bucket_name = config["bucket"]
		else:
			bucket_name = bucket_name
		if (access_key == ""):
			self.AccessKey = config["access_key"]
		else:
			self.AccessKey = access_key


		#self.LogQueue = Queue.Queue(self.BufferSize)
		self.BucketKey = bucket_key
		self.BufferSize = buffer_size
		self.LogQueue = collections.deque()

		self.StreamApiBase = config["stream_api_base"]
		self.set_bucket(bucket_name, bucket_key)
		self.DebugLevel = debug_level
		self.IsClosed = False

		self.console_message("access_key: {accessKey}".format(accessKey=self.AccessKey))
		self.console_message("stream_api_base: {api}".format(api=self.StreamApiBase))

	def ship_to_api(self, resource, contents):
		api_base = self.StreamApiBase

		headers = {
			'Content-Type': 'application/json',
			'User-Agent': 'PyStreamer v' + version.__version__,
			'Accept-Version': self.ApiVersion,
			'X-IS-AccessKey': self.AccessKey,
			'X-IS-BucketKey': self.BucketKey
		}

		def __ship(retry_attempts, wait=0):
			conn = None
			response = None
			if (self.StreamApiBase.startswith('https://')):
				api_base = self.StreamApiBase[8:]
				self.console_message("ship {resource}: stream api base domain: {domain}".format(domain=api_base, resource=resource), level=2)
				conn = httplib.HTTPSConnection(api_base, timeout=120)
			else:
				api_base = self.StreamApiBase[7:]
				self.console_message("ship {resource}: stream api base domain: {domain}".format(domain=api_base, resource=resource), level=2)
				conn = httplib.HTTPConnection(api_base, timeout=120)

			retry_attempts = retry_attempts - 1
			if (retry_attempts < 0):
				if (self.DebugLevel >= 2):
					raise Exception("shipping failed.. network issue?")
				else:
					self.console_message("ship: ISStreamer failed to ship after a number of attempts.", level=0)
					if (self.MissedEvents == None):
						self.MissedEvents = open("err_missed_events.txt", 'w+')
					if (self.MissedEvents != None):
						self.MissedEvents.write("{}\n".format(json.dumps(contents)))
					return

			try:
				if (wait > 0):
					self.console_message("ship-debug: pausing thread for {wait} seconds".format(wait=wait))
					time.sleep(wait)

				conn.request('POST', resource, json.dumps(contents), headers)
				response = conn.getresponse()

				if (response.status >= 200 and response.status < 300):
					self.console_message("ship: status: " + str(response.status) + "\nheaders: " + str(response.msg), level=2)
					self.console_message("ship: body: " + str(response.read()), level=3)
				elif (response.status == 401 or response.status == 403):
					self.console_message("ERROR: unauthorized access_key: " + self.AccessKey)
				elif (response.status == 402):
					self.console_message("AccessKey exceeded limit for month, check account")
					raise Exception("PAYMENT_REQUIRED")
				elif (response.status == 429):
					if "Retry-After" in response.msg:
						retry_after = response.msg["Retry-After"]
						self.console_message("Request limit exceeded, wait {limit} seconds before trying again".format(limit=retry_after))
						__ship(retry_attempts, int(retry_after)+1)
					else:
						self.console_message("Request limit exceeded")
				else:
					self.console_message("ship: failed on attempt {atmpt} (StatusCode: {sc}; Reason: {r})".format(sc=response.status, r=response.reason, atmpt=retry_attempts))
					raise Exception("ship exception")
			except Exception as ex:
				if (len(ex.args) > 0 and ex.args[0] == "PAYMENT_REQUIRED"):
					raise Exception("Either account is capped or an upgrade is required.")

				self.console_message("ship: exception shipping on attempt {atmpt}.".format(atmpt=retry_attempts))
				if (self.DebugLevel > 1):
					raise ex
				else:
					self.console_message("exception gobbled: {}".format(str(ex)))

				__ship(retry_attempts, 1)

		__ship(3)

	def set_bucket(self, bucket_name="", bucket_key="", retries=3):
		def __create_bucket(new_bucket_name, new_bucket_key, access_key):
			self.ship_to_api("/api/buckets", {'bucketKey': new_bucket_key, 'bucketName': new_bucket_name})

		if (bucket_key == None or bucket_key == ""):
			bucket_key = str(uuid.uuid4())

		self.BucketKey = bucket_key
		self.BucketName = bucket_name
		if (not self.Offline):
			if (self.Async):
				t = threading.Thread(target=__create_bucket, args=(bucket_name, bucket_key, self.AccessKey))
				t.daemon = False
				t.start()
			else:
				__create_bucket(bucket_name, bucket_key, self.AccessKey)
		else:
			self.console_message("Working in offline mode.", level=0)

	def console_message(self, message, level=1):
		if (self.DebugLevel >= level):
			print(message)

	def ship_messages(self, messages, retries=3):
		self.ship_to_api("/api/events", messages)


	def flush(self):
		if (self.Offline):
			self.console_message("flush: no need, in offline mode", level=2)
			return
		messages = []
		self.console_message("flush: checking queue", level=2)
		isEmpty = False
		while not isEmpty:
			try:
				m = self.LogQueue.popleft()
				messages.append(m)
			except IndexError:
				isEmpty = True
				self.console_message("flush: queue empty...", level=2)
		if len(messages) > 0:
			self.console_message("flush: queue not empty, shipping", level=2)

			self.ship_messages(messages)
			self.console_message("flush: finished flushing queue", level=2)


	def log_object(self, obj, key_prefix=None, epoch=None):
		if (epoch == None):
			epoch = time.time()

		if (key_prefix == None):
			key_prefix = "{}_".format(str(type(obj).__name__))
		elif (key_prefix != None and key_prefix != ""):
			key_prefix = "{}_".format(key_prefix)
		else:
			key_prefix = ""

		if (type(obj).__name__ == 'list'):
			i = 0
			for val in obj:
				key_name = "{}{}".format(key_prefix, i)
				self.log(key_name, val, epoch=epoch)
				i += 1
		elif (type(obj).__name__ == 'dict'):
			for key in obj:
				key_name = "{}{}".format(key_prefix, key)
				self.log(key_name, obj[key], epoch=epoch)
		else:
			for attr in dir(obj):
				if not isinstance(getattr(type(obj), attr, None), property):
					continue
				key_name = "{}{}".format(key_prefix, attr)
				self.log(key_name, getattr(obj, attr), epoch=epoch)


	def log(self, key, value, epoch=None):
		def __ship_buffer():
			i = self.BufferSize
			messages = []
			while(i > 0):
				try:
					m = self.LogQueue.popleft()
					messages.append(m)
				except IndexError:
					i = 0
					self.console_message("ship_buffer: queue empty")
				i = i - 1

			self.console_message("ship_buffer: shipping", level=2)
			self.ship_messages(messages)
			self.console_message("ship_buffer: finished shipping", level=2)

		timeStamp = time.time()
		gmtime = datetime.datetime.fromtimestamp(timeStamp)

		if epoch != None:
			try:
				gmtime = datetime.datetime.fromtimestamp(epoch)
				timeStamp = epoch
			except:
				self.console_message("epoch was overriden with invalid time, using current timstamp instead")

		formatted_gmTime = gmtime.strftime('%Y-%m-%d %H:%M:%S.%f')
		self.console_message("{time}: {key} {value}".format(key=key, value=value, time=formatted_gmTime))

		if (not self.Offline):
			if (len(self.LogQueue) >= self.BufferSize):
				self.console_message("log: queue size approximately at or greater than buffer size, shipping!", level=10)
				self.console_message("log: async is {}".format(self.Async))
				if (self.Async):
					self.console_message("log: spawning ship thread", level=3)
					t = threading.Thread(target=__ship_buffer)
					t.daemon = False
					t.start()
				else:
					__ship_buffer()

			self.console_message("log: queueing log item", level=2)
			log_item = {
				"key": key,
				"value": value,
				"epoch": timeStamp
			}
			self.LogQueue.append(log_item)
		else:
			self.LocalFile.writerow([timeStamp, key, value])


	def close(self):
		self.IsClosed = True
		self.flush()
		if (self.MissedEvents != None):
			self.MissedEvents.close()
		if (self.Offline):
			self.console_message("closing local file handler", level=2)
			self.LocalFileHandler.close()

	def __del__(self):
		"""Try to close/flush the cache before destruction"""
		try:
			if (not self.IsClosed):
				self.close()
		except:
			if (self.DebugLevel >= 2):
				raise Exception("failed to close the buffer, make sure to explicitly call close() on the Streamer")
			else:
				self.console_message("failed to close the buffer, make sure to explicitly call close() on the Streamer", level=1)
