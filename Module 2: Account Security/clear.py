import boto3
from botocore.exceptions import ClientError

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')

def clear_bucket(bucket_name):
	print(f"Deleting bucket {bucket_name}")

	bucket = s3.Bucket(bucket_name)

	try:
		bucket.objects.all().delete()
	except ClientError as e:
		print(f"Error deleting objects from bucket {bucket_name}")
		print(e)
		exit(0)

	try:
		s3_client.delete_bucket(Bucket=bucket_name)
	except ClientError as e:
		print(f"Error deleting bucket: {bucket_name}")
		print(e)
		exit(0)

def get_bucket_names():
	try:
		resp = s3_client.list_buckets()
		buckets = [b['Name'] for b in resp['Buckets']]
	except ClientError as e:
		print("Error listing buckets")
		print(e)
		exit(0)

	return buckets

def main():
	bucket_names = get_bucket_names()
	for bucket in bucket_names:
		clear_bucket(bucket)

if __name__ == '__main__':
	main()