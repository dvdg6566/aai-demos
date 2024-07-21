import boto3
from botocore.exceptions import ClientError

region = 'ap-southeast-1'
s3_client = boto3.client('s3')
lambda_client = boto3.client('lambda')

def get_bucket_names():
	try:
		resp = s3_client.list_buckets()
		buckets = [b['Name'] for b in resp['Buckets']]
	except ClientError as e:
		print("Error listing buckets")
		print(e)
		exit(0)

	return buckets

def list_all_s3():
	bucket_names = get_bucket_names()

	for bucket_name in bucket_names:
		print(f"Bucket found: {bucket_name}")
	
		try:
			response = s3_client.list_objects_v2(Bucket=bucket_name)
			for obj in response['Contents']:
				print(obj['Key'])
		except ClientError as e:
			print(f"Error lsiting objects in bucket {bucket_name}!")
			print(e)

		print()

def lambda_handler(event, context):
	list_all_s3()

if __name__ == '__main__':
	lambda_handler(None,None)