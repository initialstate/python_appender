#!/usr/bin/python

from ISStreamer.Streamer import Streamer
import sys, getopt

def main(argv):
	bucket = ''
	client_key = ''
	try:
		opts, args = getopt.getopt(argv,"hb:k:",["bucket_name=", "client_key="])
	except getopt.GetoptError:
		print('example_command_line.py -b <bucket_name> -k <client_key>')

	for opt, arg in opts:
		if opt == '-h':
			print('example_command_line.py -b <bucket_name> -k <client_key>')
		elif opt in ("-b", "--bucket_name"):
			bucket = arg
		elif opt in ("-k", "--client_key"):
			client_key = arg


	streamer = Streamer(bucket_name=bucket, client_key=client_key)

	try:
		while 1:
			log = ''
			try:
				if (sys.version_info < (2,7,0)):
				    sys.stderr.write("You need at least python 2.7.0 to use the ISStreamer")
				    exit(1)
				elif (sys.version_info >= (3,0)):
				    log = input()
				else:
				    log = raw_input()
			except EOFError:
				break
			parts = log.split(',')

			if len(parts) == 2:
				streamer.log(parts[0].strip(), parts[1].strip())
			else:
				print("format should be \"key, value\"")

	except KeyboardInterrupt:
		streamer.close()

if __name__ == "__main__":
	main(sys.argv[1:])