#########
# Use: python ./example_read_csv.py -b your_bucket_key -k your_access_key -f 'csv_file_location.csv'
# Note: The CSV file structure should NOT contain a header and should be in the following format
#       <ISO-8601 Date Time>,<StreamKey>,<StreamValue>/n
##########

import getopt, sys, time, csv
from ISStreamer.Streamer import Streamer

def read_args(argv):
	try:
		opts, args = getopt.getopt(argv,"hb:k:f:",["bucket_key=", "access_key=", "file_location="])
	except getopt.GetoptError:
		print('example_read_csv.py -b <bucket_key> -k <access_key> -f <file_location>')
		sys.exit(1)

	for opt, arg in opts:
		if opt == '-h':
			print('example_read_csv.py -b <bucket_key> -k <access_key> -f <file_location>')
		elif opt in ("-b", "--bucket_key"):
			bucket = arg
		elif opt in ("-k", "--access_key"):
			access_key = arg
		elif opt in ("-f", "--file"):
			file_location = arg

	return bucket, access_key, file_location

def is_float(str):
	try:
		float(str)
		return True
	except ValueError:
		return False

if __name__ == "__main__":
	bucket, access_key, file_location = read_args(sys.argv[1:])

	streamer = Streamer(bucket_name=bucket, bucket_key=bucket, access_key=access_key, buffer_size=20, offline=False)

	with open(file_location, 'rb') as csvfile:
		reader = csv.reader(csvfile)
		counter = 0
		for row in reader:
			epoch = row[0]
			if not is_float(epoch):
				epoch = ((dateutil.parser.parse(epoch))-(dateutil.parser.parse("1970-01-01T00:00:00Z"))).total_seconds()
			streamer.log(row[1], row[2], epoch=epoch)
			counter += 1

			if counter%10==0:
				time.sleep(.2) # limit write bandwidth

	streamer.close()
