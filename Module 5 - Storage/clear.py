import boto3
from botocore.exceptions import ClientError

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')

def clear_bucket(bucket_name):
	print(f"Deleting bucket {bucket_name}")

	bucket = s3.Bucket(bucket_name)
	paginator = s3_client.get_paginator('list_object_versions')

	try:
		bucket.objects.all().delete()
	except ClientError as e:
		print(f"Error deleting objects from bucket {bucket_name}")
		print(e)
		exit(0)

	try:
		for page in paginator.paginate(Bucket=bucket_name):
			versions = page.get('Versions', [])
			delete_markers = page.get('DeleteMarkers', [])

			if not versions and not delete_markers: 
				continue

			objects_to_delete = [
				{'Key': obj['Key'], 'VersionId': obj['VersionId']} for obj in versions
			] + [
				{'Key': obj['Key'], 'VersionId': obj['VersionId']} for obj in delete_markers
			]

			s3_client.delete_objects(Bucket=bucket_name, Delete={'Objects': objects_to_delete})
			print(f"Deleted {len(objects_to_delete)} objects from {bucket_name}")

	except Exception as e:
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
		buckets = [b for b in buckets if 'demo' in b]
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