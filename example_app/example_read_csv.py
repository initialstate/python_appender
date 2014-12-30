import getopt, sys, time, csv
from ISStreamer.Streamer import Streamer

def read_args(argv):
	try:
		opts, args = getopt.getopt(argv,"hb:k:f:",["bucket_name=", "client_key=", "file_location="])
	except getopt.GetoptError:
		print('example_read_csv.py -b <bucket_name> -k <client_key> -f <file_location>')
		sys.exit(1)

	for opt, arg in opts:
		if opt == '-h':
			print('example_read_csv.py -b <bucket_name> -k <client_key> -f <file_location>')
		elif opt in ("-b", "--bucket_name"):
			bucket = arg
		elif opt in ("-k", "--client_key"):
			client_key = arg
		elif opt in ("-f", "--file"):
			file_location = arg

	return bucket, client_key, file_location


if __name__ == "__main__":
	bucket, client_key, file_location = read_args(sys.argv[1:])

	streamer = Streamer(bucket_name=bucket, client_key=client_key, buffer_size=20, offline=False)

	with open(file_location, 'rb') as csvfile:
		reader = csv.reader(csvfile)
		counter = 0
		for row in reader:
			streamer.log(row[1], row[2], epoch=row[0])
			counter += 1

			if counter%10==0:
				time.sleep(.01) # rest for 10 ms to not go crazy with resources

	streamer.close()
