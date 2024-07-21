import boto3
from botocore.exceptions import ClientError
from secrets import token_hex
import subprocess

region = 'ap-southeast-1'

def create_buckets(prefix):
	s3_client = boto3.client('s3')

	bucketnames = [
		f"{prefix}-development",
		f"{prefix}-finance"
	]

	for bucket_name in bucketnames:
		try:
			s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region})
		except ClientError as e:
			print(f"Error creating bucket {bucket_name}")	
			print(e)
			exit(0)

	print("Successfully created S3 buckets!")

	subprocess.run("touch /tmp/test.txt", shell=True)
	with open("/tmp/test.txt", "w") as f:
		f.write("Upload Success!")

	for bucket_name in bucketnames:
		try: 
			s3_client.upload_file("/tmp/test.txt", bucket_name, "upload.txt")
		except ClientError as e:
			print(f"Error uploading demo file into bucket {bucket_name}")
			print(e)
			exit(0)

	print("Successfully written files to S3!")

def main():
	prefix = "demo" + token_hex(4)
	create_buckets(prefix)

if __name__ == '__main__':
	main()