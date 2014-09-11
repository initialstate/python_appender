import httplib
import datetime
import json

class LogStreamer:
    "This is a log streamer written in python that can help stream data directly to Initial State"
    Bucket = ""
    ClientKey = ""
    def __init__(self, bucket="", clientKey=""):
        self.Bucket = bucket
        self.ClientKey = clientKey
    
    def __getitem__(self, key):
        return self.values[key]

    def __setitem__(self, key, value):
        self.values[key] = value

    def __delitem__(self, key):
        del self.values[key]

    def log(self, signal, value, trackerId = ""):
        request_time = datetime.datetime.utcnow().isoformat()
        ##conn = httplib.HTTPSConnection("groker-dev.initialstate.com")
        conn = httplib.HTTPConnection("localhost:8081")
        resource = "/logs/{bucket}/{clientKey}".format(bucket=self.Bucket, clientKey=self.ClientKey)
        headers = {}
        headers['Content-Type'] = 'application/json'
        headers['User-Agent'] = 'IS Log Streamer Python Module'

        body = {'log': value, 'date_time': request_time, 'signal_source': signal, 'tracker_id': trackerId}
        print json.dumps(body)
        conn.set_debuglevel(1)
        conn.request("POST", resource, json.dumps(body), headers)




if __name__ == "__main__":
    import sys
    log_streamer = LogStreamer(sys.argv[1], sys.argv[2])
    log_streamer.log(sys.argv[3], sys.argv[4])