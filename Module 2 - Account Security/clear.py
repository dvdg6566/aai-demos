import boto3
from botocore.exceptions import ClientError

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
iam = boto3.client('iam')
lambda_client = boto3.client('lambda')

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

def delete_demo_iam_entities():
	prefix="demo"

	# Delete IAM Users
	try:
		users = iam.list_users()['Users']
		for user in users:
			if not user['UserName'].startswith(prefix): continue
			try: 
				iam.delete_login_profile(UserName=user['UserName'])
			except Exception as e:
				print(e)

			for policy in iam.list_attached_user_policies(UserName=user['UserName'])['AttachedPolicies']:
				iam.detach_user_policy(UserName=user['UserName'], PolicyArn=policy['PolicyArn'])

			print(f"Deleting user:{user['UserName']}")
			# Additional safety check: Check if user has active access keys
			keys = iam.list_access_keys(UserName=user['UserName'])['AccessKeyMetadata']
			for key in keys:
				iam.delete_access_key(UserName=user['UserName'], AccessKeyId=key['AccessKeyId'])
			iam.delete_user(UserName=user['UserName'])
			print(f"Deleted user: {user['UserName']}")
	except ClientError as e:
		print(f"Error listing or deleting users: {user['UserName']}")
		print(e)
		exit(0)

	# Delete IAM Roles
	try:
		roles = iam.list_roles()['Roles']
		for role in roles:
			if role['RoleName'].startswith(prefix):
				print(f"Deleting role:{role['RoleName']}")
				# Detach all policies before deleting
				for policy in iam.list_attached_role_policies(RoleName=role['RoleName'])['AttachedPolicies']:
					iam.detach_role_policy(RoleName=role['RoleName'], PolicyArn=policy['PolicyArn'])
				iam.delete_role(RoleName=role['RoleName'])
				print(f"Deleted role: {role['RoleName']}")
	except ClientError as e:
		print(f"Error listing or deleting roles: {role['roleName']}")
		print(e)
		exit(0)
	
	# Delete IAM Policies
	try:
		policies = iam.list_policies(Scope='Local')['Policies'] 
		for policy in policies:
			if not policy['PolicyName'].startswith(prefix): continue
			policy_arn = policy['Arn']

			print(f"Deleting policy: {policy_arn}" )
			versions = iam.list_policy_versions(PolicyArn=policy_arn)['Versions']
			for version in versions:
				if not version['IsDefaultVersion']:
					iam.delete_policy_version(PolicyArn=policy_arn, VersionId=version['VersionId'])

			iam.delete_policy(PolicyArn=policy['Arn'])
			print(f"Deleted policy: {policy['Arn']}")
	except ClientError as e:
		print(f"Error listing or deleting policy: {policy['Arn']}")
		print(e)
		exit(0)

def delete_lambda_functions():
    # Get all Lambda functions
    functions = lambda_client.list_functions()['Functions']

    # Filter and delete demo functions
    for function in functions:
        if function['FunctionName'].startswith('demo'):
            lambda_client.delete_function(FunctionName=function['FunctionName'])
            print(f"Deleted Lambda function: {function['FunctionName']}")

def main():
	bucket_names = get_bucket_names()
	for bucket in bucket_names:
		clear_bucket(bucket)
	delete_demo_iam_entities() 
	delete_lambda_functions()

if __name__ == '__main__':
	main()