import boto3
from botocore.exceptions import ClientError
from secrets import token_hex

region = 'ap-southeast-1'
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')

def create_bucket(prefix):
	bucketname = f"{prefix}-webserver"

	try:
		s3_client.create_bucket(Bucket=bucketname, CreateBucketConfiguration={'LocationConstraint': region})
	except ClientError as e:
		print(f"Error creating bucket {bucketname}")	
		print(e)
		exit(0)

	print("Successfully created S3 bucket!")
	bucket = s3.Bucket(bucketname)

	try:
		with open("webserver/index.html", "r") as f:
			bucket.put_object(
				Body=f.read(), 
				Key="index.html",
				ContentType = "text/html"
			)

		with open("webserver/script.js", "r") as f:
			bucket.put_object(
				Body=f.read(), 
				Key="script.js",
				ContentType = "text/javascript"
			)

	except ClientError as e:
		print(f"Error uploading demo file into bucket {bucketname}")
		print(e)
		exit(0)

	print("Successfully written files to S3!")


def main():
	prefix = "demo" + token_hex(4)
	create_bucket(prefix)

if __name__ == '__main__':
	main()