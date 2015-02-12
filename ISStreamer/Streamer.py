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
    LocalFile = None
    ApiVersion = '0.0.1'
    def __init__(self, bucket_name="", bucket_key="", access_key="", ini_file_location=None, debug_level=0, buffer_size=10, offline=None):
        config = configutil.getConfig(ini_file_location)
        if (offline != None):
            self.Offline = offline
        else:
            if (config["offline_mode"] == "false"):
                self.Offline = False
            else:
                self.Offline = True

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
    

    def set_bucket(self, bucket_name, bucket_key, retries=3):

        def __create_bucket(new_bucket_name, new_bucket_key, access_key):
            api_base = self.StreamApiBase
            conn = None
            if (self.StreamApiBase.startswith('https://')):
                api_base = self.StreamApiBase[8:]
                self.console_message("stream api base domain: {domain}".format(domain=api_base), level=2)
                conn = httplib.HTTPSConnection(api_base)
            else:
                api_base = self.StreamApiBase[7:]
                self.console_message("stream api base domain: {domain}".format(domain=api_base), level=2)
                conn = httplib.HTTPConnection(api_base)
            resource = "/api/buckets"
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'PyStreamer v' + version.__version__,
                'Accept-Version': self.ApiVersion,
                'X-IS-AccessKey': access_key
            }
            body = {
                'bucketKey': new_bucket_key,
                'bucketName': new_bucket_name,
            }

            def ___ship(retry_attempts, wait=0):
                if (retry_attempts <= 0):
                    if (self.DebugLevel >= 2):
                        raise Exception("bucket create failed")
                    else:
                        self.console_message("ISStreamer failed to create or find bucket after a number of attempts", level=0)
                        return

                try:
                    if (wait > 0):
                        time.sleep(wait)
                    conn.request("POST", resource, json.dumps(body), headers)
                    response = conn.getresponse()

                    if (response.status == 200 or response.status == 204):
                        self.console_message("bucket most likely exists", level=2)
                    elif (response.status == 201):
                        self.console_message("bucket created successfully!", level=2)
                        self.console_message("bucket created with \n   bucket_key: {bk} \n   bucket_name: {bn}".format(bk=new_bucket_key, bn=new_bucket_name), level=2)
                    elif (response.status == 401 or response.status == 403):
                        self.console_message("ERROR: AccessKey not authorized: " + self.AccessKey)
                    elif (response.status == 402):
                        self.console_message("AccessKey exceeded limit for month, check account at www.initialstate.com/app")
                        raise Exception("Either account is capped or an upgrade is required.")
                    else:
                        self.console_message("ISStreamer failed to setup the bucket on attempt {atmpt}. StatusCode: {sc}; Reason: {r}".format(sc=response.status, r=response.reason, atmpt=retry_attempts))
                        raise Exception("ship exception")
                except Exception as ex:
                    self.console_message("exception creating bucket on attempt {atmpt}.".format(atmpt=retry_attempts))
                    self.console_message(ex, level=2)
                    retry_attempts = retry_attempts - 1
                    ___ship(retry_attempts, 1)

            ___ship(retries)

        if (bucket_key == None or bucket_key == ""):
            bucket_key = str(uuid.uuid4())

        self.BucketKey = bucket_key
        self.BucketName = bucket_name
        if (not self.Offline):
            t = threading.Thread(target=__create_bucket, args=(bucket_name, bucket_key, self.AccessKey))
            t.daemon = False
            t.start()
        else:
            self.console_message("Working in offline mode.", level=0)

    def console_message(self, message, level=1):
        if (self.DebugLevel >= level):
            print(message)

    def ship_messages(self, messages, retries=3):
        api_base = self.StreamApiBase
        conn = None
        if (self.StreamApiBase.startswith('https://')):
            api_base = self.StreamApiBase[8:]
            self.console_message("ship messages: stream api base domain: {domain}".format(domain=api_base), level=2)
            conn = httplib.HTTPSConnection(api_base)
        else:
            api_base = self.StreamApiBase[7:]
            self.console_message("ship messages: stream api base domain: {domain}".format(domain=api_base), level=2)
            conn = httplib.HTTPConnection(api_base)
        resource = "/api/events"
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'PyStreamer v' + version.__version__,
            'Accept-Version': self.ApiVersion,
            'X-IS-AccessKey': self.AccessKey,
            'X-IS-BucketKey': self.BucketKey
        }

        def __ship(retry_attempts, wait=0):
            self.console_message("ship: beginning message ship!", level=2)
            if (retry_attempts <= 0):
                if (self.DebugLevel >= 2):
                    raise Exception("shipping logs failed.. network issue?")
                else:
                    self.console_message("ship: ISStreamer failed to ship the logs after a number of attempts {msgs}".format(msgs=json.dumps(messages)), level=0)
                    return
            
            try:
                if (wait > 0):
                    time.sleep(wait)
                conn.request('POST', resource, json.dumps(messages), headers)
                response = conn.getresponse()

                if (response.status >= 200 and response.status < 300):
                    self.console_message("ship: success!", level=2)
                elif (response.status == 401 or response.status == 403):
                    self.console_message("ERROR: unauthorized access_key: " + self.AccessKey)
                elif (response.status == 402):
                    self.console_message("AccessKey exceeded limit for month, check account at www.initialstate.com/app")
                    raise Exception("Either account is capped or an upgrade is required.")
                else:
                    self.console_message("ship: failed on attempt {atmpt} (StatusCode: {sc}; Reason: {r})".format(sc=response.status, r=response.reason, atmpt=retry_attempts))
                    raise Exception("ship exception")
            except:
                self.console_message("ship: exception shipping logs on attempt {atmpt}.".format(atmpt=retry_attempts))
                retry_attempts = retry_attempts - 1
                __ship(retry_attempts, 1)

        __ship(retries)
            

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
            key_prefix = str(type(obj).__name__)

        if (type(obj).__name__ == 'list'):
            i = 0
            for val in obj:
                key_name = "{}_{}".format(key_prefix, i)
                self.log(key_name, val, epoch=epoch)
                i += 1
        elif (type(obj).__name__ == 'dict'):
            for key in obj:
                key_name = "{}_{}".format(key_prefix, key)
                self.log(key_name, obj[key], epoch=epoch)
        else:
            for attr in dir(obj):
                if not isinstance(getattr(type(obj), attr, None), property):
                    continue
                key_name = "{}_{}".format(key_prefix, attr)
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
                t = threading.Thread(target=__ship_buffer)
                t.daemon = False
                t.start()
        
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
        if (self.Offline):
            self.console_message("closing local file handler", level=2)
            self.LocalFileHandler.close()

    def __del__(self):
        """Try to close/flush the cache before destruction"""
        try:
            if (not self.IsClosed):
                self.flush()
        except:
            if (self.DebugLevel >= 2):
                raise Exception("failed to close the buffer, make sure to explicitly call close() on the Streamer")
            else:
                self.console_message("failed to close the buffer, make sure to explicitly call close() on the Streamer", level=1)
