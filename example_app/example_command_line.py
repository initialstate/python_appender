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


	streamer = Streamer(bucket=bucket, client_key=client_key)

	try:
		while 1:	
			log = raw_input()
			parts = log.split(',')

			if len(parts) == 2:
				streamer.log(parts[0].strip(), parts[1].strip())
			else:
				print("format should be \"key, value\"")

	except KeyboardInterrupt:
		streamer.close()

if __name__ == "__main__":
	main(sys.argv[1:])