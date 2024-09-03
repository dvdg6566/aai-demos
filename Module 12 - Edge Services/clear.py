import boto3
from botocore.exceptions import ClientError
import time

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
cloudfront = boto3.client('cloudfront')

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

def delete_cloudfront_distributions():
	distributions = cloudfront.list_distributions()

	for distribution in distributions['DistributionList']['Items']:
		distribution_id = distribution['Id']
		distribution_config = cloudfront.get_distribution_config(Id=distribution_id)
		etag = distribution_config['ETag']

		updated_config = {
			**distribution_config['DistributionConfig'],  # Include all existing parameters
			'Enabled': False     # Disable the distribution
		}

		# Disable the distribution first
		print(f"Disabling distribution: {distribution_id}")
		
		cloudfront.update_distribution(
			Id=distribution_id,
			IfMatch=etag,
			DistributionConfig=updated_config
		)

		# Wait for the distribution to be disabled
		while True:
			status = cloudfront.get_distribution(Id=distribution_id)['Distribution']['Status']
			if status == "Deployed":
				print(f"Distribution disabled: {distribution_id}")
				break
			else:
				print("Waiting for distribution to be disabled...")
				time.sleep(10) 

		# Delete the distribution
		print(f"Deleting distribution: {distribution_id}")
		cloudfront.delete_distribution(
			Id=distribution_id,
			IfMatch=etag
		)

	print("All CloudFront distributions have been deleted.")

def main():
	bucket_names = get_bucket_names()
	for bucket in bucket_names:
		clear_bucket(bucket)
	delete_cloudfront_distributions()

if __name__ == '__main__':
	main()